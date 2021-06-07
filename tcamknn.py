from __future__ import print_function
from math import floor, log

# Redefined because this has to run on Python 2.7
def log2(x):
    return log(x, 2)

# floor returns float in Python 2.7
def ifloor(x):
    return int(floor(x))

def brgc(x):
    return x ^ (x >> 1)

def is_pow2(n):
    return (n & (n-1) == 0) and n != 0


def tcode_point(p, hmax):
    assert(is_pow2(hmax))

    word = brgc(p) >> (int(log2(hmax)) - 1)
    
    for i in range(hmax):
        if (i != 0) and (i != hmax // 2):
            b = ifloor((p - i) // hmax) % 2
            word = (word << 1) | b
    return word

def print_interval(t):
    word, mask = t

    #print(f'word: {format(word, "06b")}, mask: {format(mask, "06b")}')
    print('word: {}, mask: {}'.format(format(word, "06b"), format(mask, "06b")))

def tcode_simple_interval(i, hmax):
    s, t = i
    assert(is_pow2(hmax))
    assert(t - s + 1 == hmax)

    result = 0

    x, y = s, t
    
    mask = 0
    for i in range(x + 1, y + 1):
        mask = mask | (brgc(i - 1) ^ brgc(i))

    hmax_base = int(log2(hmax))
    word = brgc(x) >> (hmax_base - 1)
    mask = mask >> (hmax_base - 1)

    for i in range(hmax):
        if (i != 0) and (i != hmax // 2):
            if (x % hmax) != i:
                mask = (mask << 1) | 1
                word = word << 1
            else:
                mask = mask << 1
                b = ifloor((x - i) // hmax) % 2
                word = (word << 1) | b

    return (word, mask)

def conjoin_intervals(ia, ib):
    aword, amask = ia
    bword, bmask = ib

    # Ensure that * values are 0 in the word
    aword = (aword & ~amask)
    bword = (bword & ~bmask)

    new_mask = amask & bmask
    ormask = amask | bmask
    assert((aword | ormask) == (bword | ormask))
    new_word = aword | bword

    return new_word, new_mask

def tcode_interval(i, hmax):
    s, t = i
    assert(is_pow2(hmax))
    assert((t - s) <= (hmax - 1))

    subintervals = [i]

    if t - s + 1 != hmax:
        i1 = (s, s + hmax - 1)
        i2 = (t - hmax + 1, t)
        subintervals = [i1, i2]

    result = 0
    count = 0


    for x, y in subintervals:
        mask = 0
        for i in range(x + 1, y + 1):
            mask = mask | (brgc(i - 1) ^ brgc(i))

        hmax_base = int(log2(hmax))
        word = brgc(x) >> (hmax_base - 1)
        mask = mask >> (hmax_base - 1)

        for i in range(hmax):
            if (i != 0) and (i != hmax // 2):
                if (x % hmax) != i:
                    mask = (mask << 1) | 1
                    word = word << 1
                else:
                    mask = mask << 1
                    b = ifloor((x - i) // hmax) % 2
                    word = (word << 1) | b

        if count > 0:
            result = conjoin_intervals(result, (word, mask))
        else:
            result = (word, mask)
            
        count += 1

    return result

def encoding_len(w, hmax):
    assert(is_pow2(hmax))
    return w - int(log2(hmax)) + hmax - 1

def tcode_ndim_point(p, w, hmax):
    l = encoding_len(w, hmax)
    width = 0
    result = 0
    
    for dim in p:
        word = tcode_point(dim, hmax)
        result = result << l
        result = result | word
        width += l

    return result, width

def tcode_ndim_interval(lowers, uppers, w, hmax):
    l = encoding_len(w, hmax)
    width = 0
    res_word = 0
    res_mask = 0

    for lower, upper in zip(lowers, uppers):
        word, mask = tcode_interval((lower, upper), hmax)
        res_word = res_word << l
        res_mask = res_mask << l
        res_word = res_word | word
        res_mask = res_mask | mask
        width += l

    return (res_word, res_mask), width

def in_ndim_interval(p, lowers, uppers, w, hmax):
    word, _ = tcode_ndim_point(p, w, hmax)
    (iword, mask), _ = tcode_ndim_interval(lowers, uppers, w, hmax)

    return (word | mask) == (iword | mask)
    

def in_interval(p, pt, hmax):
    word = tcode_point(p, hmax)
    iword, mask = tcode_interval(pt, hmax)

    return (word | mask) == (iword | mask)
