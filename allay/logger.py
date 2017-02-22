from sys import stderr, stdout


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

    warn(*message)
    exit(exit_code)


def log(*message):
    output(stdout, *message)


def warn(*message):
    output(stderr, *message)