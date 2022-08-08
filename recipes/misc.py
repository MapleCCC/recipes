from colorama import Fore, Style


__all__ = ["bright_red", "bright_green", "bright_blue", "bright_yellow"]


def bright_red(s: str) -> str:
    """
    Augment a string, so that when printed to console, the string is displayed in bright red color.
    """

    if "NO_COLOR" in os.environ:
        return s

    return Style.BRIGHT + Fore.RED + s + Style.RESET_ALL


def bright_green(s: str) -> str:
    """
    Augment a string, so that when printed to console, the string is displayed in bright green color.
    """

    if "NO_COLOR" in os.environ:
        return s

    return Style.BRIGHT + Fore.GREEN + s + Style.RESET_ALL


def bright_blue(s: str) -> str:
    """
    Augment a string, so that when printed to console, the string is displayed in bright blue color.
    """

    if "NO_COLOR" in os.environ:
        return s

    return Style.BRIGHT + Fore.BLUE + s + Style.RESET_ALL


def bright_yellow(s: str) -> str:
    """
    Augment a string, so that when printed to console, the string is displayed in bright yellow color.
    """

    if "NO_COLOR" in os.environ:
        return s

    return Style.BRIGHT + Fore.YELLOW + s + Style.RESET_ALL

