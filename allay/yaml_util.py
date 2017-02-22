import yaml


def load(file_path):
    fp = open(file_path)
    return yaml.load(fp.read())


def pretty_print(obj):
    return yaml.dump(obj, default_flow_style=False, default_style='')


def write(obj, file_path):
    fp = open(file_path, 'w')
    fp.write(pretty_print(obj))
    fp.close()
