import fnmatch
from pathlib import Path
import tempfile
from typing import *
import re
import logging

from PyPlasmaFractal.mylib.config.storage import Storage

logger = logging.getLogger(__name__)

#------------------------------------------------------------------------------------------------------------------------------

class ShaderTemplateResolver:
    """
    A class to resolve and integrate shader includes and apply template arguments within the shader source code.
    
    Attributes:
        storage (Storage[str]): A storage instance to fetch shader source code by filename.
        max_include_depth (int): The maximum recursion depth allowed for resolving includes.
        extra_debug_info (bool): Whether to include additional debug information in the resolved shader code.
        include_pattern (re.Pattern): Compiled regex pattern to identify include directives in the shader code.
        argument_pattern (re.Pattern): Compiled regex pattern to parse template arguments from include directives.
    """
    def __init__(self, storage: Storage[str], max_include_depth: int = 10, extra_debug_info: bool = False):
        """
        Initialize the ShaderTemplateResolver with the given parameters.

        Parameters:
            storage (Storage[str]): A storage instance to fetch shader source code by filename.
            max_include_depth (int): The maximum recursion depth allowed for resolving includes. Defaults to 10.
            extra_debug_info (bool): Whether to include additional debug information in the resolved shader code. Defaults to False.
        """
        self.storage = storage
        self.max_include_depth = max_include_depth
        self.extra_debug_info = extra_debug_info
        self.include_pattern = re.compile(r'^\s*(#include|#apply_template)\s+"([^"]+)"(?:,\s*(.+))?', re.IGNORECASE | re.MULTILINE)
        self.argument_pattern = re.compile(r'(\w+)\s*=\s*(\w+)')


    def resolve(self, filename: str, template_args: Optional[Dict[str, str]] = None) -> str:
        """
        Resolve the shader template by integrating includes and applying template arguments.

        Parameters:
            filename (str): The filename of the initial shader source code containing include directives.
            template_args (Dict[str, str], optional): A dictionary of template arguments for replacements. Defaults to None.

        Returns:
            str: The fully resolved shader source code with all includes processed and placeholders replaced.
        """
        template_args = template_args or {}
            
        included_files = set()
        current_path = []
        resolved_source = self._include_file(filename, 1, included_files, current_path, template_args)
        
        if self.extra_debug_info:
            with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.glsl') as temp_file:
                temp_file.write(resolved_source)
                temp_file_path = temp_file.name
                logger.debug(f'RESOLVED TEMPLATE "{filename}": {temp_file_path}')
        
        return resolved_source


    def _include_file(self, filename: str, depth: int, included_files: Set[Tuple[str, Optional[str]]],
                      current_path: List[str], template_args: Dict[str, str]) -> str:
        """
        Process the inclusion of a shader file, managing nested includes and template arguments.

        Parameters:
            filename (str): The filename of the shader source to be included.
            depth (int): The current depth of recursion for includes.
            included_files (Set[Tuple[str, Optional[str]]]): A set to track included files and their template arguments.
            current_path (List[str]): A list tracking the current path of file inclusions to detect circular includes.
            template_args (Dict[str, str]): Template arguments to apply to the shader code.

        Returns:
            str: The shader code with all includes processed and template arguments applied.
        
        Raises:
            Exception: If the maximum include depth is exceeded, or if circular dependencies are detected.
        """
        logger.debug(f'Processing template file "{filename}" at depth {depth} with template args: {template_args}')
        
        if depth > self.max_include_depth:
            raise Exception(f'Maximum include depth of {self.max_include_depth} exceeded.')
        
        include_key = (filename, tuple(sorted(template_args.items())))
        if include_key in included_files:
            logger.debug(f'Skipping already included file: "{filename}" with args {template_args}')
            return ''
        
        if '*' in filename or '?' in filename:
            return self._handle_wildcard_includes(filename, depth, included_files, current_path, template_args)
        
        try:
            content = self.storage.load(filename)
            logger.debug(f'Loaded content from "{filename}"')
        except Exception as e:
            raise Exception(f'Error loading source from "{filename}": {str(e)}')
        
        try:
            content = self._apply_template_args(content, template_args)
        except Exception as e:
            raise Exception(f'Error applying template arguments in "{filename}": {str(e)}')
        
        current_path.append(filename)
        included_files.add(include_key)
        
        result = self._replace_includes_and_templates(content, current_path, depth, included_files, template_args)
        
        current_path.pop()
        
        logger.debug(f'Finished processing file: "{filename}"')
        
        if self.extra_debug_info:
            comment = '//////////'
            content_header = f'\n{comment} FILE: "{filename}"' + (f'\n{comment} {template_args}' if template_args else '') + '\n\n'
            content_footer = f'\n{comment} END FILE: "{filename}"\n'
            return content_header + result + content_footer
        
        return result


    def _replace_includes_and_templates(self, content: str, current_path: List[str], depth: int,
                                        included_files: Set[Tuple[str, Optional[str]]], template_args: Dict[str, str]) -> str:
        """
        Replace include and apply_template directives in shader code with the corresponding file content.

        Parameters:
            content (str): The shader code to process.
            current_path (List[str]): The current path of file inclusions to detect circular includes.
            depth (int): The current depth of recursion for includes.
            included_files (Set[Tuple[str, Optional[str]]]): A set to track included files and their template arguments.
            template_args (Dict[str, str]): Template arguments to apply to the shader code.

        Returns:
            str: The shader code with all includes and templates processed.
        
        Raises:
            Exception: If there are misuse of directives, such as providing template arguments with #include or omitting them with #apply_template.
        """
        def replace_func(match: re.Match):
            
            parent_file = current_path[-1]
            directive = match.group(1)
            include_name = match.group(2).strip()
            template_args_str = match.group(3) or ''
            
            logger.debug(f"Found directive '{directive}' for file '{include_name}' with args '{template_args_str}'")
            
            if directive.lower() == '#include' and template_args_str:
                raise Exception(f'Error in \"{parent_file}\": Template arguments are not allowed for #include directive.\n  {match.group(0)}')
            
            if directive.lower() == '#apply_template' and not template_args_str:
                raise Exception(f'Error in \"{parent_file}\": Missing template arguments for #apply_template directive.\n  {match.group(0)}')
            
            if include_name in current_path:
                raise Exception(f'Error in \"{parent_file}\": Circular include detected.\n  {match.group(0)}')
            
            template_args = {m.group(1): m.group(2) for m in re.finditer(self.argument_pattern, template_args_str)}
            
            result = self._include_file(include_name, depth + 1, included_files, current_path, template_args)
            
            return result
        
        return re.sub(self.include_pattern, replace_func, content)
    

    def _handle_wildcard_includes(self, filename: str, depth: int, included_files: Set[Tuple[str, Optional[str]]],
                                  current_path: List[str], template_args: Dict[str, str]) -> str:
        """
        Handle wildcard patterns in the filename by listing and matching files from the storage,
        and recursively including each matched file.

        Parameters:
            filename (str): The filename with potential wildcard patterns.
            depth (int): The current depth of recursion for includes.
            included_files (Set[Tuple[str, Optional[str]]]): A set to track included files and their template arguments.
            current_path (List[str]): A list tracking the current path of file inclusions to detect circular includes.
            template_args (Dict[str, str]): Template arguments to apply to the shader code.

        Returns:
            str: The shader code with all includes processed and template arguments applied.
        """
        logger.debug(f'Resolving wildcard filename "{filename}"')
        
        normalized_filename = Path(filename).as_posix()
        all_files = [Path(f).as_posix() for f in self.storage.list()]
        
        results = []
        for match in fnmatch.filter(all_files, normalized_filename):
            results.append(self._include_file(match, depth, included_files, current_path, template_args))
        
        return "\n\n".join(results)


    def _apply_template_args(self, content: str, args: Dict[str, str]) -> str:
        """
        Apply template arguments to placeholders in the given string by scanning for placeholders.
        Placeholders are matched and replaced case-insensitively.
        Reports errors for unmatched placeholders and unused dictionary keys.
        Only placeholders consisting of alphanumeric characters and underscores are considered valid.

        Args:
            content (str): The string containing placeholders to be replaced.
            args (Dict[str, str]): A dictionary of template arguments, where the keys are the placeholders
                and the values are the corresponding replacement values.

        Returns:
            str: The modified content string with placeholders replaced by their corresponding values.

        Raises:
            Exception: If there are unused dictionary keys or unmatched placeholders.

        Example:
            >>> content = "Hello, <name>! Today is <DAY>."
            >>> args = {"name": "John", "day": "Monday"}
            >>> apply_template_args(content, args)
            'Hello, John! Today is Monday.'
        """
        
        # Create a new dictionary where all keys are lowercase to handle case-insensitive matching
        case_insensitive_args = {key.lower(): value for key, value in args.items()}

        # Set to collect all unique placeholders found in the content
        found_placeholders = set()

        # Regex pattern to find all valid occurrences of placeholders in the format <placeholder>
        placeholder_pattern = re.compile(r"<(\w+)>")

        # Function to replace each placeholder with corresponding value from case_insensitive_args
        def replace_placeholder(match):
            placeholder = match.group(1).lower()
            found_placeholders.add(placeholder.lower())

            # Return the replacement if it exists in case_insensitive_args, otherwise report error
            if placeholder in case_insensitive_args:
                return str(case_insensitive_args[placeholder])
            else:
                raise Exception(f"Unmatched placeholder detected: {match.group(0)}")

        # Replace all found placeholders in the content
        modified_content = placeholder_pattern.sub(replace_placeholder, content)

        # Check for unused dictionary keys
        unused_keys = set(case_insensitive_args.keys()) - found_placeholders
        if unused_keys:
            # Raise an exception for unused dictionary keys
            raise Exception(f"Unused dictionary keys detected: {unused_keys}")

        return modified_content
