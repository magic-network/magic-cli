import six
from pyfiglet import figlet_format

DEFAULT_COLOR = "green"

try:
    from termcolor import colored
except ImportError:
    colored = None


# Print to stdout with color and/or figlet
def log(string, color=DEFAULT_COLOR, font="slant", figlet=False):
    if colored:
        if not figlet:
            six.print_(colored(string, color))
        else:
            six.print_(colored(figlet_format(string, font=font), color))
    else:
        six.print_(string)


def devlog(string):
    log("(DEV) %s" % string, "blue")
