import sys

if 'win' in sys.platform:
    #http://www.burgaud.com/bring-colors-to-the-windows-console-with-python/
    from ctypes import windll, Structure, c_short, c_ushort, byref

    SHORT = c_short
    WORD = c_ushort


    class COORD(Structure):
        """struct in wincon.h."""
        _fields_ = [
            ("X", SHORT),
            ("Y", SHORT)]


    class SMALL_RECT(Structure):
        """struct in wincon.h."""
        _fields_ = [
            ("Left", SHORT),
            ("Top", SHORT),
            ("Right", SHORT),
            ("Bottom", SHORT)]


    class CONSOLE_SCREEN_BUFFER_INFO(Structure):
        """struct in wincon.h."""
        _fields_ = [
            ("dwSize", COORD),
            ("dwCursorPosition", COORD),
            ("wAttributes", WORD),
            ("srWindow", SMALL_RECT),
            ("dwMaximumWindowSize", COORD)]

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
elif 'linux' in sys.platform:
    from termcolor import colored


def get_text_attr():
    csbi = CONSOLE_SCREEN_BUFFER_INFO()
    GetConsoleScreenBufferInfo(stdout_handle, byref(csbi))
    return csbi.wAttributes


def set_text_attr(color):
    SetConsoleTextAttribute(stdout_handle, color)


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
    if 'linux' in sys.platform:
        print colored(msg, foreground)
    elif 'win' in sys.platform:
        default_colors = get_text_attr()

        set_text_attr(foreground | default_colors & 0x0070)
        print msg
        set_text_attr(default_colors)
    else:
        print msg

