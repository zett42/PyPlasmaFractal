import tempfile
from typing import *
import re
import logging

logger = logging.getLogger(__name__)

#------------------------------------------------------------------------------------------------------------------------------

def resolve_shader_template(
    filename: str, 
    get_file_content: Callable[[str], str], 
    template_args: Optional[Dict[str, str]] = {},
    max_include_depth: int = 10,
    extra_debug_info: bool = False
) -> str:
    """
    Resolve and integrate shader includes and apply template arguments within the shader source code, starting 
    from a specified filename. The function supports nested includes and handles inline replacements for marked 
    placeholders using specified template arguments at all levels. It ensures that includes do not exceed a 
    specified maximum depth, prevents circular dependencies, and optimizes processing by resolving each include file
    only once per unique set of template arguments.

    This function can interpret two kinds of directives within shader code:
    1. #include: For simply including the content of another shader file without additional template processing.
    2. #apply_template: For including content from another shader file and simultaneously applying inline specified
       template arguments.

    Parameters:
        filename (str): The filename of the initial shader source code containing include directives.
        get_file_content (Callable[[str], str]): A function to fetch shader source code by filename. This function
            should raise an exception if the file cannot be accessed or does not exist.
        template_args (Dict[str, str], optional): A dictionary of template arguments for replacements at the top-level 
            shader source. Defaults to empty, which applies no template arguments initially.
        max_include_depth (int, optional): The maximum recursion depth allowed for resolving includes. This prevents 
            infinite recursion due to deeply nested or circular includes. Defaults to 10.
        extra_debug_info (bool, optional): Whether to include additional debug information in the resolved shader code.

    Returns:
        str: The fully resolved shader source code with all includes processed and placeholders replaced as specified.

    Raises:
        Exception: If there are circular includes, if the maximum include depth is exceeded, or if there are issues
            accessing files as specified in include directives. Specific errors are raised for misuse of directives, 
            such as providing template arguments with #include or omitting them with #apply_template.

    Notes:
        Each included file is resolved only once per unique combination of template arguments to ensure efficiency
        and avoid redundant processing.
    """
    include_pattern = re.compile(r'^\s*(#include|#apply_template)\s+"([^"]+)"(?:,\s*(.+))?', re.IGNORECASE | re.MULTILINE)
    argument_pattern = re.compile(r'(\w+)\s*=\s*(\w+)')

    included_files = set()   # Tracks files with their template arguments to prevent duplicate instances
    current_path = []        # Stack to track current file inclusion path to detect circular dependencies

    resolved_source = _include_file(filename, get_file_content, 1, max_include_depth,
                                    included_files, current_path, 
                                    include_pattern, argument_pattern, template_args,
                                    extra_debug_info)
    
    if extra_debug_info:
        # Write resolved fragment shader source to a temporary file to aid debugging
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.glsl') as temp_file:
            temp_file.write(resolved_source)
            temp_file_path = temp_file.name
            logger.debug(f'RESOLVED TEMPLATE "{filename}": {temp_file_path}')

    return resolved_source


#------------------------------------------------------------------------------------------------------------------------------

def _include_file(
    filename: str, 
    get_file_content: Callable[[str], str], 
    depth: int, 
    max_include_depth: int, 
    included_files: Set[Tuple[str, Optional[str]]], 
    current_path: List[str], 
    include_pattern: re.Pattern,
    argument_pattern: re.Pattern,
    template_args: Dict[str, object],
    extra_debug_info: bool = False
) -> str:
    """
    Process the inclusion of a shader file, managing nested includes and template arguments.

    This function handles the recursive inclusion of files, applying template arguments, and avoiding circular 
    dependencies or excessive depth in file inclusions. It interprets directives within the shader code to include
    additional files and apply template arguments to them as specified.

    Parameters:
        filename (str): The filename of the shader source to be included.
        get_file_content (Callable[[str], str]): A function to retrieve shader source content by filename.
        depth (int): The current depth of recursion for includes.
        max_include_depth (int): The maximum allowable recursion depth for includes to prevent infinite loops.
        included_files (Set[Tuple[str, Optional[str]]]): A set to track included files and their template arguments to 
            avoid redundant processing.
        current_path (List[str]): A list tracking the current path of file inclusions to detect circular includes.
        include_pattern (re.Pattern): Compiled regex pattern to identify include directives in the shader code.
        argument_pattern (re.Pattern): Compiled regex pattern to parse template arguments from include directives.
        template_args (Dict[str, str]): Template arguments to apply to the shader code.
        extra_debug_info (bool, optional): Whether to include additional debug information in the resolved shader code.

    Returns:
        str: The shader code with all includes processed and template arguments applied, if applicable.

    Raises:
        Exception: If the maximum include depth is exceeded, or if circular dependencies are detected. Errors in file 
            access or misuse of template directives also raise exceptions with appropriate messages.
    """
    
    logger.debug(f'Processing template file "{filename}" at depth {depth} with template args: {template_args}')

    if depth > max_include_depth:
        raise Exception(f'Maximum include depth of {max_include_depth} exceeded.')

    include_key = (filename, tuple(sorted(template_args.items())))  # Unique key for file with template arguments
    if include_key in included_files:
        logger.debug(f'Skipping already included file: "{filename}" with args {template_args}')
        return ''  # Skip as this exact instance has already been included

    try:
        content = get_file_content(filename)
        logger.debug(f'Loaded content from "{filename}"')
    except Exception as e:
        raise Exception(f'Error loading source from "{filename}": {str(e)}')    

    try:
        content = _apply_template_args(content, template_args)
    except Exception as e:
        raise Exception(f'Error applying template arguments in "{filename}": {str(e)}')

    current_path.append(filename)
    included_files.add(include_key)

    def replace_include(match: re.Match):

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

        template_args = {m.group(1): m.group(2) for m in re.finditer(argument_pattern, template_args_str)}

        result = _include_file(include_name, get_file_content, depth + 1, max_include_depth, 
                               included_files, current_path, include_pattern, argument_pattern, template_args,
                               extra_debug_info)

        return result

    result = re.sub(include_pattern, replace_include, content)

    current_path.pop()

    logger.debug(f'Finished processing file: "{filename}"')

    if extra_debug_info:
        comment = '//////////'
        content_header = f'\n{comment} FILE: "{filename}"' + (f'\n{comment} {template_args}' if template_args else '') + '\n\n'
        content_footer = f'\n{comment} END FILE: "{filename}"\n'
        return content_header + result + content_footer
    
    return result

#------------------------------------------------------------------------------------------------------------------------------

def _apply_template_args(content: str, args: Dict[str, object]) -> str:
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

#------------------------------------------------------------------------------------------------------------------------------

def make_file_source_resolver(base_directory: str) -> Callable[[str], str]:
    """
    Create a callable that fetches shader source code from files relative to a specified base directory.

    Parameters:
        base_directory (str): The base directory from which shader include paths will be resolved.

    Returns:
        Callable[[str], str]: A function that takes a shader file name (relative to the base directory) and
        returns the contents of the shader file as a string.
    """
    def get_file_content(shader_file_name: str) -> str:

        # Construct the full path to the shader file
        file_path = os.path.join(base_directory, shader_file_name)

        # Attempt to open and read the shader file
        try:
            with open(file_path, 'r') as file:
                return file.read()
        except FileNotFoundError:
            raise FileNotFoundError(f"The file {shader_file_name} was not found in the directory {base_directory}.")
        except IOError as e:
            raise IOError(f"Could not read the file {shader_file_name}: {str(e)}")

    return get_file_content

#------------------------------------------------------------------------------------------------------------------------------

def make_dict_source_resolver(shader_dict: Dict[str, str]) -> Callable[[str], str]:
    """
    Creates a callable to retrieve shader source codes based on filenames from a dictionary.

    Args:
        shader_dict (dict): Dictionary mapping filename to shader source codes.

    Returns:
        Callable[[str], str]: A function that takes a filename and returns the shader source code.
    """
    def get_shader_from_dict(filename: str) -> str:

        if filename in shader_dict:
            return shader_dict[filename]
        else:
            raise KeyError(f'Shader file "{filename}" not found in the dictionary.')

    return get_shader_from_dict
