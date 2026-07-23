"""ANSI terminal colour utilities.

Provides the ``Color`` class with methods to produce styled and 24-bit
coloured strings for terminal output.
"""

import random


class Color():
    """Factory for ANSI-styled terminal strings.

    Each method returns a string wrapped in the appropriate ANSI escape
    sequence.  Nesting is supported.
    """
    def rgb(self, r: int, g: int, b: int) -> str:
        """Return an ANSI escape sequence for a 24-bit foreground colour."""
        return f"\033[38;2;{r};{g};{b}m"

    @staticmethod
    def end() -> str:
        """Return the ANSI reset escape sequence."""
        return "\033[0m"

    @staticmethod
    def error(msg: str) -> str:
        """Return a red bold error message string."""
        return f"\033[31;1mError: {msg}\033[0m"

    @staticmethod
    def warning(msg: str) -> str:
        """Return a yellow bold warning message string."""
        return f"\033[33;1mWarning: {msg}\033[0m"

    @staticmethod
    def info(msg: str) -> str:
        """Return a cyan bold info message string."""
        return f"\033[36;1m{msg}\033[0m"

    @staticmethod
    def success(msg: str) -> str:
        """Return a green bold success message string."""
        return f"\033[32;1m{msg}\033[0m"

    @staticmethod
    def random_color() -> str:
        """Return an ANSI escape sequence for a random foreground colour."""
        red: int = 0
        green: int = 0
        blue: int = 0

        radiant = random.randint(0, 255)
        if radiant < 85:
            red = random.randint(0, 85)
            green = random.randint(0, 85)
            blue = random.randint(0, 85)
        elif radiant < 170:
            red = random.randint(85, 170)
            green = random.randint(85, 170)
            blue = random.randint(85, 170)
        else:
            red = random.randint(170, 255)
            green = random.randint(170, 255)
            blue = random.randint(170, 255)
        return f"\033[38;2;{red};{green};{blue}m"

    def get_comb(self) -> list[tuple[str, str]]:
        """Return a list of colour combination tuples."""
        return [
            (self.rgb(255, 255, 0), self.rgb(0, 255, 255)),
            (self.rgb(255, 255, 0), self.rgb(0, 0, 0)),
            (self.rgb(255, 0, 255), self.rgb(0, 255, 255)),
            (self.rgb(255, 0, 255), self.rgb(0, 0, 0)),
            (self.rgb(0, 255, 255), self.rgb(0, 0, 0)),
            (self.rgb(227, 178, 60), self.rgb(0, 0, 0)),
            (self.rgb(255, 192, 203), self.rgb(79, 47, 79)),
            (self.rgb(255, 0, 0), self.rgb(112, 224, 208)),
            (self.rgb(255, 0, 0), self.rgb(0, 168, 107)),
            (self.rgb(255, 0, 0), self.rgb(127, 0, 255)),
            (self.rgb(112, 224, 208), self.rgb(0, 168, 107)),
            (self.rgb(112, 224, 208), self.rgb(127, 0, 255)),
            (self.rgb(0, 168, 107), self.rgb(127, 0, 255)),
            (self.rgb(255, 255, 0), self.rgb(255, 0, 255)),
            (self.rgb(255, 0, 255), self.rgb(212, 175, 55)),
            (self.rgb(255, 0, 255), self.rgb(64, 224, 208)),
            (self.rgb(255, 0, 255), self.rgb(178, 34, 34)),
            (self.rgb(212, 175, 55), self.rgb(64, 224, 208)),
            (self.rgb(212, 175, 55), self.rgb(178, 34, 34)),
            (self.rgb(64, 224, 208), self.rgb(178, 34, 34)),
            (self.rgb(255, 105, 180), self.rgb(139, 69, 19)),
            (self.rgb(212, 175, 55), self.rgb(33, 37, 41)),
            (self.rgb(212, 175, 55), self.rgb(128, 128, 128)),
            (self.rgb(0, 0, 128), self.rgb(238, 221, 195)),
            (self.rgb(0, 0, 128), self.rgb(255, 69, 0)),
            (self.rgb(0, 0, 128), self.rgb(255, 130, 0)),
            (self.rgb(238, 221, 195), self.rgb(255, 69, 0)),
            (self.rgb(238, 221, 195), self.rgb(255, 130, 0)),
            (self.rgb(255, 69, 0), self.rgb(255, 130, 0)),
            (self.rgb(101, 67, 33), self.rgb(0, 139, 139)),
            (self.rgb(101, 67, 33), self.rgb(0, 0, 0)),
            (self.rgb(0, 139, 139), self.rgb(0, 0, 0)),
            (self.rgb(0, 0, 128), self.rgb(197, 150, 35)),
            (self.rgb(0, 0, 128), self.rgb(20, 24, 46)),
            (self.rgb(0, 0, 128), self.rgb(204, 85, 0)),
            (self.rgb(0, 0, 128), self.rgb(211, 211, 211)),
            (self.rgb(197, 150, 35), self.rgb(20, 24, 46)),
            (self.rgb(197, 150, 35), self.rgb(204, 85, 0)),
            (self.rgb(197, 150, 35), self.rgb(211, 211, 211)),
            (self.rgb(20, 24, 46), self.rgb(204, 85, 0)),
            (self.rgb(20, 24, 46), self.rgb(211, 211, 211)),
            (self.rgb(204, 85, 0), self.rgb(211, 211, 211)),
            (self.rgb(212, 115, 212), self.rgb(15, 82, 186)),
            (self.rgb(212, 115, 212), self.rgb(176, 224, 230)),
            (self.rgb(15, 82, 186), self.rgb(176, 224, 230)),
            (self.rgb(0, 0, 255), self.rgb(139, 69, 19)),
            (self.rgb(0, 0, 255), self.rgb(75, 0, 130)),
            (self.rgb(139, 69, 19), self.rgb(75, 0, 130)),
            (self.rgb(1, 50, 32), self.rgb(255, 165, 0)),
            (self.rgb(255, 218, 185), self.rgb(255, 165, 0)),
            (self.rgb(112, 224, 208), self.rgb(0, 0, 128)),
            (self.rgb(250, 128, 114), self.rgb(0, 0, 128)),
            (self.rgb(0, 128, 0), self.rgb(255, 0, 255)),
            (self.rgb(4, 139, 154), self.rgb(64, 224, 208)),
            (self.rgb(4, 139, 154), self.rgb(128, 128, 128)),
            (self.rgb(247, 127, 119), self.rgb(64, 224, 208)),
            (self.rgb(247, 127, 119), self.rgb(128, 128, 128)),
            (self.rgb(64, 224, 208), self.rgb(128, 128, 128)),
            (self.rgb(255, 0, 255), self.rgb(255, 20, 147)),
            (self.rgb(255, 0, 255), self.rgb(75, 0, 130)),
            (self.rgb(112, 66, 20), self.rgb(255, 20, 147)),
            (self.rgb(112, 66, 20), self.rgb(75, 0, 130)),
            (self.rgb(255, 20, 147), self.rgb(75, 0, 130)),
            (self.rgb(255, 182, 193), self.rgb(135, 206, 235)),
            (self.rgb(255, 182, 193), self.rgb(79, 47, 79)),
            (self.rgb(188, 184, 138), self.rgb(135, 206, 235)),
            (self.rgb(188, 184, 138), self.rgb(79, 47, 79)),
            (self.rgb(135, 206, 235), self.rgb(79, 47, 79)),
            (self.rgb(245, 245, 220), self.rgb(255, 191, 0)),
            (self.rgb(44, 34, 30), self.rgb(255, 191, 0)),
            (self.rgb(112, 66, 20), self.rgb(245, 245, 220)),
            (self.rgb(112, 66, 20), self.rgb(188, 184, 138)),
            (self.rgb(4, 139, 154), self.rgb(245, 245, 220)),
            (self.rgb(4, 139, 154), self.rgb(188, 184, 138)),
            (self.rgb(245, 245, 220), self.rgb(188, 184, 138)),
            (self.rgb(154, 205, 50), self.rgb(34, 139, 34)),
            (self.rgb(128, 128, 0), self.rgb(34, 139, 34))
        ]
