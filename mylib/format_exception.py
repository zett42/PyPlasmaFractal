import traceback

def format_exception_ansi_colors(e):
    # Define ANSI color codes
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    BOLD = "\033[1m"
    RESET = "\033[0m"

    # Extract the stacktrace and format it
    exception_info = "".join(traceback.format_exception_only(type(e), e))
    traceback_info = "".join(traceback.format_tb(e.__traceback__))
    stacktrace = traceback_info + exception_info

    # Split stacktrace into lines
    lines = stacktrace.split("\n")
    formatted_lines = []

    for line in lines:
        # Check if the line contains file path
        if "File" in line:
            # Color the path and line number in blue
            parts = line.split(", ")
            parts[0] = BLUE + parts[0] + RESET  # File path
            if len(parts) > 1:
                parts[1] = BLUE + parts[1] + RESET  # Line number
            line = ", ".join(parts)
            # Highlight function name and code in green
            line = line.replace(" in ", " in " + GREEN)
            line = line.replace(")", RESET + ")")

        # Check if line contains error message
        elif "Error" in line:
            line = BOLD + RED + line + RESET

        # Check if the line is pointing to an error in code
        elif "^" in line:
            line = YELLOW + line + RESET
        
        formatted_lines.append(line)

    # Join the formatted lines back into a single string
    formatted_stacktrace = "\n".join(formatted_lines)
    return formatted_stacktrace
