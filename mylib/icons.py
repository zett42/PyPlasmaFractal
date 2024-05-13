import logging
import os
from typing import *
import imgui

class Icons:
    """
    A class to manage Material Design Icons unicode mappings as static attributes, and merge the font automatically.
    Static attributes represent common icons as Unicode strings, simplifying usage in GUI elements or text.
    """
    # Static attributes for icon unicode strings
    WARNING = "\U000F0026"
    ERROR = "\U000F0025"
    ALERT_REMOVE = "\U000F14BC"
    # Add more icon attributes here...


    @staticmethod
    def merge_font(fonts_dir: str, font_file_name: str = 'MaterialDesignIconsDesktop.ttf', font_size: int = 28) -> None:
        """
        Merge the Material Design Icons font with default fonts in an imgui application using the glyph ranges
        determined from the icon code points.

        Args:
        fonts_dir (str): Directory where the icon font file is stored.
        font_file_name (str): Name of the Material Design Icons font file to be used.
        font_size (int): Size of the font.
        """
        fonts = imgui.get_io().fonts

        # Path to the font file
        font_path = os.path.join(fonts_dir, font_file_name)
        glyph_ranges = Icons._determine_glyph_ranges()

        # Convert list of tuples into a flat, zero-terminated array
        flat_glyph_ranges = []
        for start, end in glyph_ranges:
            flat_glyph_ranges.extend([start, end])
        flat_glyph_ranges.append(0)  # Zero-terminate the array
        
        # Define glyph ranges for specific icons
        glyph_range_object = imgui.core.GlyphRanges(flat_glyph_ranges)
        
        # Configuration for merging fonts
        config = imgui.core.FontConfig(merge_mode=True)
        
        # Add the font to imgui
        logging.debug(f"Loading font from: {font_path}")
        fonts.add_font_from_file_ttf(font_path, font_size, font_config=config, glyph_ranges=glyph_range_object)


    @staticmethod
    def _determine_glyph_ranges() -> List[Tuple[int, int]]:
        """
        Determine glyph ranges from the static icon attributes using Unicode code points. This method calculates
        and compiles the glyph ranges necessary for merging the font.

        Returns:
        list of tuples: Glyph ranges for the icons managed by this class.
        """
        # Convert Unicode strings to code points
        code_points = [ord(getattr(Icons, attr)) for attr in dir(Icons) if attr.isupper()]
        if not code_points:
            return []
        
        # Sort the code points
        code_points = sorted(code_points)
        ranges = []
        start = end = code_points[0]

        # Build ranges by checking contiguous blocks of code points
        for code_point in code_points[1:]:
            if code_point == end + 1:
                end = code_point
            else:
                ranges.append((start, end))
                start = end = code_point

        ranges.append((start, end))  # Append the last range

        return ranges
