import pickle

data = pickle.load(open('data/hypixelCog/ah_names.pkl', 'rb'))


def stage_1(input_list: list):
    for item in input_list:
        if not is_ascii(item):
            input_list.pop(input_list.index(item))
    pickle.dump(input_list, open("data/hypixelCog/stage_1.pkl", 'wb'))
    return input_list


def is_ascii(s):
    return all(ord(c) < 128 for c in s)


stage_1(data)
