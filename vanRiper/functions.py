from itertools import groupby
from operator import itemgetter

# function that takes json data deserialized into a dictionary
# and recursively finds all the values that, recursively, match a certain key.
# perfect for having an unknown depth


def get_all(data, key):
    sub_iter = []
    if isinstance(data, dict):
        if key in data:
            yield data[key]
        sub_iter = data.itervalues()
    if isinstance(data, list):
        sub_iter = data
    for x in sub_iter:
        for y in get_all(x, key):
            yield y


def orderIT(data):
    numberList = []
    # put all numbers in a list with appropriate ordering
    for k, g in groupby(enumerate(data), lambda (i, x): i-x):
        tempList = list(map(itemgetter(1), g))
        if not numberList:
            # list is empty so it's the first iteration and you don't need to check for items to append to it. Just simply push tempList to numberList
            for each in tempList:
                numberList.append(each)
        else:
            # make sure they're all strings first
            # numberList = list(map(str, numberList))
            # it's ready to check and figure which numbers to modify with the current List
            last = numberList[-1]  # get a copy of the last item
            for each in tempList:
                if isinstance(last, float):
                    # ignore it because they aren't what we want
                    # it is consecutive and we shouldn't do anything to it but append it to numberList
                    numberList.append(each)
                else:
                    if each - numberList[-1] != 1 or each - numberList[-1] != 0:
                        # then it is non consecutive and we need to combine them into a float
                        if last == numberList[-1]:
                            numberList.pop()  # remove last item so you're ready to append
                        else:
                            pass
                        numberList.append(float(str(last) + '.' + str(each)))
                    else:
                        # it is consecutive and we shouldn't do anything to it but append it to numberList
                        numberList.append(each)

    # MAKE THE INTEGERS ALL INTO STRINGS!!
    numberList = list(map(str, numberList))
    return numberList
