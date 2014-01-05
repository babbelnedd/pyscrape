# Credits
# Konstantin Lepa   <konstantin.lepa@gmail.com>   Termcolor 1.1.0     http://bit.ly/1dCtM52       (MIT LICENSE)
# Andre Burgaud                                                       http://bit.ly/1iEUduA       (MIT LICENSE)

import sys

#region Windows

if 'win' in sys.platform:
    from ctypes import windll, Structure, c_short, c_ushort, byref

    SHORT = c_short
    WORD = c_ushort


    class COORD(Structure):
        _fields_ = [("X", SHORT), ("Y", SHORT)]


    class SMALL_RECT(Structure):
        _fields_ = [("Left", SHORT), ("Top", SHORT), ("Right", SHORT), ("Bottom", SHORT)]


    class CONSOLE_SCREEN_BUFFER_INFO(Structure):
        _fields_ = [("dwSize", COORD), ("dwCursorPosition", COORD), ("wAttributes", WORD),
                    ("srWindow", SMALL_RECT), ("dwMaximumWindowSize", COORD)]

    # winbase.h
    STD_INPUT_HANDLE = -10
    STD_OUTPUT_HANDLE = -11
    STD_ERROR_HANDLE = -12

    # wincon.h
    FOREGROUND_BLACK = 0x0000
    FOREGROUND_BLUE = 0x0001
    FOREGROUND_GREEN = 0x0002
    FOREGROUND_CYAN = 0x0003
    FOREGROUND_RED = 0x0004
    FOREGROUND_MAGENTA = 0x0005
    FOREGROUND_YELLOW = 0x0006
    FOREGROUND_GREY = 0x0007
    FOREGROUND_INTENSITY = 0x0008 # foreground color is intensified.

    BACKGROUND_BLACK = 0x0000
    BACKGROUND_BLUE = 0x0010
    BACKGROUND_GREEN = 0x0020
    BACKGROUND_CYAN = 0x0030
    BACKGROUND_RED = 0x0040
    BACKGROUND_MAGENTA = 0x0050
    BACKGROUND_YELLOW = 0x0060
    BACKGROUND_GREY = 0x0070
    BACKGROUND_INTENSITY = 0x0080 # background color is intensified.

    stdout_handle = windll.kernel32.GetStdHandle(STD_OUTPUT_HANDLE)
    SetConsoleTextAttribute = windll.kernel32.SetConsoleTextAttribute
    GetConsoleScreenBufferInfo = windll.kernel32.GetConsoleScreenBufferInfo


    def get_text_attr():
        csbi = CONSOLE_SCREEN_BUFFER_INFO()
        GetConsoleScreenBufferInfo(stdout_handle, byref(csbi))
        return csbi.wAttributes


    def set_text_attr(color):
        SetConsoleTextAttribute(stdout_handle, color)

#endregion


class Foreground(object):
    if 'win' in sys.platform:
        Blue = 0x0001 | 0x0008
        Green = 0x0002 | 0x0008
        Cyan = 0x0003 | 0x0008
        Red = 0x0004 | 0x0008
        Magenta = 0x0005 | 0x0008
        Yellow = 0x0006 | 0x0008
        White = 0x0007 | 0x0008
    else:
        Blue = 'blue'
        Green = 'green'
        Cyan = 'cyan'
        Red = 'red'
        Magenta = 'magenta'
        Yellow = 'yellow'
        White = 'white'


def print_colored(msg, foreground):
    def _print_colored_nix(text, color=None, on_color=None, attrs=None):
        ATTRIBUTES = dict(
            list(zip(['bold', 'dark', '', 'underline', 'blink', '', 'reverse', 'concealed'], list(range(1, 9)))))
        del ATTRIBUTES['']
        HIGHLIGHTS = dict(list(
            zip(['on_grey', 'on_red', 'on_green', 'on_yellow', 'on_blue', 'on_magenta', 'on_cyan', 'on_white'],
                list(range(40, 48)))))
        COLORS = dict(
            list(zip(['grey', 'red', 'green', 'yellow', 'blue', 'magenta', 'cyan', 'white', ], list(range(30, 38)))))
        RESET = '\033[0m'

        import os

        if os.getenv('ANSI_COLORS_DISABLED') is None:
            fmt_str = '\033[%dm%s'
            if color is not None:
                text = fmt_str % (COLORS[color], text)

            if on_color is not None:
                text = fmt_str % (HIGHLIGHTS[on_color], text)

            if attrs is not None:
                for attr in attrs:
                    text = fmt_str % (ATTRIBUTES[attr], text)

            text += RESET
        print(text)

    if 'linux' in sys.platform:
        _print_colored_nix(msg, foreground)
    elif 'win' in sys.platform:
        default_colors = get_text_attr()

        set_text_attr(foreground | default_colors & 0x0070)
        print(msg)
        set_text_attr(default_colors)
    else:
        print(msg)