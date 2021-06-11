from __future__ import print_function
from math import log

def log2(x):
    return log(x, 2)

def is_pow2(n):
    return (n & (n-1) == 0) and n != 0

def print_binary(s, b = None):
    if b is None:
        print("{0:b}".format(s))
    else:
        format_str = "{0:0" + str(b) + "b}"
        print(format_str.format(s))

def get_interval(start, end):
    """
    Return a list of intervals that represent [start, end] (inclusive)
    Assume end is always 1 less than a power of 2
    """

    if start == end:
        return [(start, 0)]

    if start > end:
        return []

    # if not is_pow2(end + 1):
    #     raise ValueError("end is not one less than a power of 2: {}".format(end))

    length = (end + 1) - start
    largest_interval_bits = int(log2(length))

    # theres a better bit way to do this with masks
    # zero out the last largest_inteval_bits bits of end
    new_start = (end >> largest_interval_bits) << largest_interval_bits

    interval = (new_start, (1 << largest_interval_bits) - 1)

    # ensure that this interval does not cover more past than end
    # for instance [24, 30] does not behave properly 
    # since our generated mask would be for [24, 31] 
    # there's definitely a better way to do this entire algorithm
    assert end == (new_start | ((1 << largest_interval_bits) - 1))

    # this interval can be expressed in a single range
    if start == new_start:
        return [interval]
    else:
        a = get_interval(start, new_start - 1)
        a.append(interval)
        return a

def tcam_lookup(key):
    """
    Returns the first entry that matches key in the TCAM in form (value, mask)
    The TCAM entries are static

    key: Query key to match with, represented as (value, mask)
    """

    value, mask = key

    # test with a 8-entry TCAM, each TCAM entry will end in 3 index bits
    # TCAM entries are stored as value, mask
    # 0011 000
    # 0*10 001
    # 1001 010
    # 1*** 011
    # 0111 100
    # 011* 101
    # 0*** 110
    # **** 111
    tcam = []
    tcam.append((int("0011000", 2), int("0000000", 2)))
    tcam.append((int("0010001", 2), int("0100000", 2)))
    tcam.append((int("1001010", 2), int("0000000", 2)))
    tcam.append((int("1000011", 2), int("0111000", 2)))
    tcam.append((int("0111100", 2), int("0000000", 2)))
    tcam.append((int("0110101", 2), int("0001000", 2)))
    tcam.append((int("0000110", 2), int("0111000", 2)))
    tcam.append((int("0000111", 2), int("1111000", 2)))

    # print(tcam)

    for tcam_value, tcam_mask in tcam:
        new_mask = tcam_mask | mask

        if tcam_value | new_mask == value | new_mask:
            return tcam_value, tcam_mask

    return None

def multi_match_mud(key, n_bits, limit = None):
    """
    Returns up to limit matches from the TCAM
    If limit is None, returns all matches for key

    key: Query key to match with, represented as (interval, mask)
    n_bits: Number of bits required to represent all entries in TCAM
    """

    # just set it to some value greater than the number of entries in TCAM
    if limit is None:
        limit = 1 << (n_bits + 1)

    count = 0
    matches = []

    key_val, key_mask = key

    # mask to get the bits representing the index
    index_mask = (1 << n_bits ) - 1

    # each entry is stored as (interval, mask)
    d = []
    # start with the initial prefix **..**
    d.append((0, index_mask))

    while len(d) > 0:
        next_val, next_mask = d.pop()

        lookup_value = key_val << n_bits | next_val
        lookup_mask = key_mask << n_bits | next_mask

        # append the range to the lookup key
        entry = tcam_lookup((lookup_value, lookup_mask))

        # print(entry)

        if entry is None:
            continue

        # TODO: determine if this entry reprsents a duplicate point
        # if is_valid(entry)

        matches.append(entry)
        entry_index = entry[0] & index_mask

        print(entry_index)

        # the start position is entry_index + 1
        # the end position is the end of the original interval, which is found by replacing * with 1
        next_intervals = get_interval(entry_index + 1, next_val | next_mask)

        # intervals come out in biggest start position first, need to reverse in order to preserve order
        while len(next_intervals) > 0:
            d.append(next_intervals.pop())

        count += 1

        if count >= limit:
            break

    return matches


def main():
    # print(tcam_lookup((24, 0)))
    # for x, y in multi_match_mud((7, 8), 3, 4):
    #     print_binary(x, 7)
    #     print_binary(y, 7)
    #     print("")
    for x, y in get_interval(1, 31):
        print_binary(x, 6)
        print_binary(y, 6)
        print("")

if __name__ == '__main__':
    main()

