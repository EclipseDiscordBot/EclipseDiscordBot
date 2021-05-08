import pickle
from classes.deprecated import deprecated


@deprecated
def stage_1(input_list: list):
    for item in input_list:
        if not item:
            input_list.pop(input_list.index(item))
    return input_list


@deprecated
def is_ascii(s):
    return all(ord(c) < 128 for c in s)


if __name__ == '__main__':
    stage_1(["test","test"])
