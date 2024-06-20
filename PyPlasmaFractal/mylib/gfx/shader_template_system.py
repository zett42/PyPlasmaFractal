import fnmatch
from pathlib import Path
import tempfile
from typing import *
import re
import logging

from PyPlasmaFractal.mylib.config.storage import Storage

logger = logging.getLogger(__name__)

#------------------------------------------------------------------------------------------------------------------------------

class SourceInfo:
    """
    Holds information about the source file and line number.

    Attributes:
        filename (str): The name of the source file.
        line_number (int): The line number in the source file.
    """
    def __init__(self, filename: str, line_number: int):
        
        self.filename = filename
        self.line_number = line_number


class ResolvedLine:
    """
    Represents a resolved line of shader code along with its source information.

    Attributes:
        line (str): The resolved line of shader code.
        source (SourceInfo): The source information for the line.
    """
    def __init__(self, line: str, source: SourceInfo):
        
        self.line = line
        self.source = source


class ShaderTemplateResolver:
    """
    Resolves shader templates, handling includes and template arguments.

    Attributes:
        storage (Storage[str]): Storage mechanism to load shader files.
        max_include_depth (int): Maximum allowed depth for nested includes.
        extra_debug_info (bool): Flag to include extra debug information.
    """
    def __init__(self, storage: 'Storage[str]', max_include_depth: int = 10, extra_debug_info: bool = False):
        
        self.storage = storage
        self.max_include_depth = max_include_depth
        self.extra_debug_info = extra_debug_info
        self.include_pattern = re.compile(r'^\s*(#include|#apply_template)\s+"([^"]+)"(?:,\s*(.+))?', re.IGNORECASE | re.MULTILINE)
        self.argument_pattern = re.compile(r'(\w+)\s*=\s*(\w+)')


    def resolve(self, filename: str, template_args: Optional[Dict[str, str]] = None, source_info: Optional[List[SourceInfo]] = None) -> str:
        """
        Resolves a shader template by processing includes and applying template arguments.

        Args:
            filename (str): The name of the shader file to resolve.
            template_args (Optional[Dict[str, str]]): Arguments for template substitution.
            source_info (Optional[List[SourceInfo]]): List to store source information.

        Returns:
            str: The resolved shader source code.
        """
        if source_info is None:
            source_info = []
            
        template_args = template_args or {}
        
        included_files = set()
        current_path = []

        resolved_source = self._include_file(filename, 1, included_files, current_path, template_args)

        resolved_content = '\n'.join([line.line for line in resolved_source])
        source_info.extend([line.source for line in resolved_source])

        if self.extra_debug_info:
            with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.glsl') as temp_file:
                temp_file.write(resolved_content)
                temp_file_path = temp_file.name
                logger.debug(f'RESOLVED TEMPLATE "{filename}": {temp_file_path}')

        return resolved_content


    def _include_file(self, filename: str, depth: int, included_files: Set[Tuple[str, Optional[str]]],
                      current_path: List[str], template_args: Dict[str, str]) -> List[ResolvedLine]:
        """
        Includes and processes a file, handling nested includes and template arguments.

        Args:
            filename (str): The name of the file to include.
            depth (int): Current depth of nested includes.
            included_files (Set[Tuple[str, Optional[str]]]): Set of included files to avoid duplicates.
            current_path (List[str]): Stack of the current include path.
            template_args (Dict[str, str]): Arguments for template substitution.

        Returns:
            List[ResolvedLine]: List of resolved lines from the included file.
        """
        logger.debug(f'Processing template file "{filename}" at depth {depth} with template args: {template_args}')
        
        if depth > self.max_include_depth:
            raise Exception(f'Maximum include depth of {self.max_include_depth} exceeded.')
        
        include_key = (filename, tuple(sorted(template_args.items())))
        if include_key in included_files:
            logger.debug(f'Skipping already included file: "{filename}" with args {template_args}')
            return []
        
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
        
        result = self._replace_includes_and_templates(content, current_path, depth, included_files, filename)
        
        current_path.pop()
        
        logger.debug(f'Finished processing file: "{filename}"')
        
        if self.extra_debug_info:
            comment = '//////////'
            content_header = [ResolvedLine(f'{comment} FILE: "{filename}"', SourceInfo(filename, -1))]
            content_footer = [ResolvedLine(f'{comment} END FILE: "{filename}"', SourceInfo(filename, -1))]
            return content_header + result + content_footer
        
        return result


    def _replace_includes_and_templates(self, content: str, current_path: List[str], depth: int,
                                        included_files: Set[Tuple[str, Optional[str]]],
                                        parent_filename: str) -> List['ResolvedLine']:
        """
        Replaces include and template directives in the content with the resolved lines.

        Args:
            content (str): The content of the current file.
            current_path (List[str]): Stack of the current include path.
            depth (int): Current depth of nested includes.
            included_files (Set[Tuple[str, Optional[str]]]): Set of included files to avoid duplicates.
            parent_filename (str): Name of the parent file.

        Returns:
            List[ResolvedLine]: List of resolved lines from the processed content.
        """
        def replace_directive(match: re.Match) -> List['ResolvedLine']:

            directive, include_name, template_args_str = match.group(1), match.group(2).strip(), match.group(3) or ''
            
            if directive.lower() == '#include' and template_args_str:
                raise Exception(f'Error in \"{parent_filename}\": Template arguments are not allowed for #include directive.\n  {match.group(0)}')
            
            if directive.lower() == '#apply_template' and not template_args_str:
                raise Exception(f'Error in \"{parent_filename}\": Missing template arguments for #apply_template directive.\n  {match.group(0)}')
            
            if include_name in current_path:
                raise Exception(f'Error in \"{parent_filename}\": Circular include detected.\n  {match.group(0)}')
            
            parsed_template_args = {m.group(1): m.group(2) for m in re.finditer(self.argument_pattern, template_args_str)}
            return self._include_file(include_name, depth + 1, included_files, current_path, parsed_template_args)

        resolved_lines = []
        lines = content.split('\n')

        for line_number, line in enumerate(lines):
            match = self.include_pattern.match(line.strip())
            if match:
                resolved_lines.extend(replace_directive(match))
            else:
                resolved_lines.append(ResolvedLine(line, SourceInfo(parent_filename, line_number)))

        return resolved_lines


    def _handle_wildcard_includes(self, filename: str, depth: int, included_files: Set[Tuple[str, Optional[str]]],
                                  current_path: List[str], template_args: Dict[str, str]) -> List[ResolvedLine]:
        """
        Handles includes with wildcard characters by resolving matching files.

        Args:
            filename (str): The wildcard filename pattern.
            depth (int): Current depth of nested includes.
            included_files (Set[Tuple[str, Optional[str]]]): Set of included files to avoid duplicates.
            current_path (List[str]): Stack of the current include path.
            template_args (Dict[str, str]): Arguments for template substitution.

        Returns:
            List[ResolvedLine]: List of resolved lines from the matching files.
        """
        logger.debug(f'Resolving wildcard filename "{filename}"')
        
        normalized_filename = Path(filename).as_posix()
        all_files = [Path(f).as_posix() for f in self.storage.list()]
        
        results = []
        for match in fnmatch.filter(all_files, normalized_filename):
            results.extend(self._include_file(match, depth, included_files, current_path, template_args))
        
        return results


    def _apply_template_args(self, content: str, args: Dict[str, str]) -> str:
        """
        Applies template arguments to the content by replacing placeholders.

        Args:
            content (str): The content with placeholders.
            args (Dict[str, str]): Dictionary of template arguments.

        Returns:
            str: The content with placeholders replaced by argument values.
        """
        case_insensitive_args = {key.lower(): value for key, value in args.items()}
        found_placeholders = set()
        placeholder_pattern = re.compile(r"<(\w+)>")

        def replace_placeholder(match):

            placeholder = match.group(1).lower()
            found_placeholders.add(placeholder.lower())

            if placeholder in case_insensitive_args:
                return str(case_insensitive_args[placeholder])
            else:
                raise Exception(f"Unmatched placeholder detected: {match.group(0)}")

        modified_content = placeholder_pattern.sub(replace_placeholder, content)
        
        unused_keys = set(case_insensitive_args.keys()) - found_placeholders
        if unused_keys:
            raise Exception(f"Unused dictionary keys detected: {unused_keys}")

        return modified_content


class ShaderCompileError(Exception):
    """
    Exception raised when a shader compilation error occurs.
    
    Attributes:
        message (str): The error message describing the shader compilation error.
    """    
    def __init__(self, message: str):
        super().__init__(message)


def handle_shader_template_compile_error(e: Exception, base_directory: str, 
                                         vertex_shader_source_info: List[SourceInfo], fragment_shader_source_info: List[SourceInfo]):
    """
    Handles shader template compilation errors by parsing error messages and providing detailed information
    about the error locations within the source templates.
    
    Args:
        e (Exception): The exception raised during shader compilation.
        base_directory (str): The base directory where shader source files are located.
        vertex_shader_source_info (List[SourceInfo]): List of SourceInfo objects for the vertex shader source,
            defining the source file name and line number in the template that contributed to each line of the resolved shader code.
        fragment_shader_source_info (List[SourceInfo]): List of SourceInfo objects for the fragment shader source,
            defining the source file name and line number in the template that contributed to each line of the resolved shader code.
        
    Raises:
        ShaderCompileError: If a shader compilation error is detected, a detailed ShaderCompileError is raised,
            providing the error locations within the source templates.
        Exception: If the error is not related to shader compilation, the original exception is re-raised.
    """
    error_msg = str(e)
    
    if not error_msg.strip().startswith("GLSL Compiler failed"):
        raise e    
    
    parsed_errors = _parse_shader_errors(error_msg)
    
    combined_error_msg = "Shader compilation errors:\n"
    
    for error in parsed_errors:
        
        line_number = error['line_number']
        message     = error['error_message']
        shader_type = error['shader_type']
        
        source_info = (vertex_shader_source_info if shader_type == 'vertex_shader' else fragment_shader_source_info)
        
        if line_number >= 0 and line_number < len(source_info):
            source = source_info[line_number]
            source_path = Path(base_directory) / source.filename
            combined_error_msg += (f'\n  File "{source_path}", line {source.line_number}, in {shader_type}\n    {message}\n')
        else:
            combined_error_msg += (f'\n  File "unknown", line {line_number}, in {shader_type}\n    {message}\n')
    
    raise ShaderCompileError(combined_error_msg) from e


def _parse_shader_errors(exception_message: str) -> List[Dict[str, Union[int, str]]]:
    
    error_pattern = re.compile(r'ERROR: (\d+):(\d+): (.+)')
    parsed_errors = []
    sections = exception_message.split('\n\n')
    
    if len(sections) < 2:
        return parsed_errors
    
    shader_info = sections[1].split('\n')
            
    for line in shader_info[2:]:
        match = error_pattern.match(line)
        if match: 
            parsed_errors.append({
                'line_number': int(match.group(2)),
                'error_message': match.group(3),
                'shader_type': shader_info[0]
            })
            
    return parsed_errors
