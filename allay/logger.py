from sys import stderr, stdout

from termcolor import colored


def output(fd, *text_args):
    text = ""

    for var in text_args:
        text += str(var)

    fd.write(text + '\n')


def error(*message, **kwargs):
    if isinstance(message[0], BaseException):
        raise message[0]

    exit_code = 1

    if 'exit_code' in kwargs:
        exit_code = int(kwargs['exit_code'])

    text = colored(' '.join(map(str, message)), 'red')

    output(stderr, text)
    exit(exit_code)


def log(*message):
    text = colored(' '.join(map(str, message)), 'green')
    output(stdout, text)


def warn(*message):
    text = colored(' '.join(map(str, message)), 'yellow')
    output(stderr, text)