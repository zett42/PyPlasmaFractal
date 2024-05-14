import os
from pathlib import PurePath
from typing import Callable

def trim_text_with_ellipsis(text: str, max_width: int, calc_text_width: Callable[[str], int], ellipsis: str = '...', trim_start: bool = False) -> str:
    """
    Trims the given text to fit within the specified maximum width, adding an ellipsis if necessary.

    Args:
        text (str): The original text to be trimmed.
        max_width (int): The maximum width allowed for the trimmed text.
        calc_text_width (Callable[[str], int]): A function that calculates the width of a given text.
        ellipsis (str, optional): The ellipsis string to be added when the text is trimmed. Defaults to '...'.
        trim_start (bool, optional): Specifies whether the trimming should start from the beginning of the text. 
            If False, the trimming will start from the end of the text. Defaults to False.

    Returns:
        str: The trimmed text with an ellipsis if necessary.
    """

    # Check if the original text is within the allowed width, if so return it directly
    if calc_text_width(text) <= max_width:
        return text

    # If the allowed width is less than the ellipsis width, simply return the ellipsis
    if max_width < calc_text_width(ellipsis):
        return ellipsis

    # Setup initial bounds for binary search
    low, high = 0, len(text)

    # Function to construct the trimmed text based on the direction of trimming
    def get_trimmed_text(mid):
        if trim_start:
            return ellipsis + text[mid:]
        else:
            return text[:mid] + ellipsis

    # Binary search to find the optimal trim point
    while low < high:
        mid = (low + high) // 2
        trimmed_text = get_trimmed_text(mid)
        measured_width = calc_text_width(trimmed_text)

        if measured_width > max_width:
            if trim_start:
                low = mid + 1
            else:
                high = mid
        else:
            if trim_start:
                high = mid
            else:
                low = mid + 1

    # Check last adjustment to confirm within width
    # Binary search might terminate with low equal to high or low just one more than high
    # so we check both conditions:
    best_fit = get_trimmed_text(low if low < len(text) else high)
    if calc_text_width(best_fit) > max_width:
        best_fit = get_trimmed_text(high if trim_start else low - 1)

    return best_fit


def trim_path_with_ellipsis(path: str, max_width: int, calc_text_width: Callable[[str], int], ellipsis: str = '...') -> str:
    """
    Trims a given path to fit within a maximum width, replacing parts by an ellipsis if necessary.

    Args:
        path (str): The path to be trimmed.
        max_width (int): The maximum width of the trimmed path.
        calc_text_width (Callable[[str], int]): A function that calculates the display width of a string.
        ellipsis (str, optional): The ellipsis string to be added when the path is trimmed. Defaults to '...'.

    Returns:
        str: The trimmed path.

    """
    # Check if the original path is within the allowed width, if so return it directly
    if calc_text_width(path) <= max_width:
        return path

    # Parse the input path into parts using PurePath
    path_obj = PurePath(path)
    parts = path_obj.parts
    if not parts:
        return ''

    # Calculate the display width of the ellipsis and the path separator
    ellipsis_width = calc_text_width(ellipsis)
    separator_width = calc_text_width(os.sep)
    
    # Calculate the display width of the path anchor (e.g., drive letter or root directory)
    anchor = path_obj.anchor
    anchor_width = calc_text_width(anchor)

    # Initialize with the last part (filename or deepest directory)
    trimmed_path_obj = PurePath(parts[-1])
    trimmed_path_width = calc_text_width(str(trimmed_path_obj))

    # Check if adding ellipsis to the last part already exceeds the width limit
    if trimmed_path_width + ellipsis_width > max_width:
        # Fall back to trimming the last part directly
        return trim_text_with_ellipsis(str(trimmed_path_obj), max_width, calc_text_width, ellipsis, trim_start=True)

    # Check if adding anchor, last part, and ellipsis exceeds the width limit
    if trimmed_path_width + anchor_width + ellipsis_width > max_width:
        # Remove all parts except the last one
        return str(PurePath(ellipsis) / trimmed_path_obj)

    # Construct the trimmed path by including as many parts as possible without exceeding max_width

    current_width = anchor_width + separator_width + trimmed_path_width

    for part in reversed(parts[:-1]):
        part_width = calc_text_width(str(part))
        if part_width + ellipsis_width + current_width > max_width:
            break

        trimmed_path_obj = PurePath(part) / trimmed_path_obj
        current_width += separator_width + part_width 

    # Return the final trimmed path
    return str(PurePath(anchor) / ellipsis / trimmed_path_obj)
