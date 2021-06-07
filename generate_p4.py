

from __future__ import print_function
from tcamknn import *
import p4template
from p4template import MAX_BITS

from random import randrange
import random

points = [
    [5],
    [7]
]

W = 8
HMAX = 8
NDIM = 16

RANDOM_PTS = True
NPOINTS = 5000


# Generate random points for benchmark purposes
if RANDOM_PTS:
    random.seed(42)
    max_val = (2**W) - HMAX
    min_val = HMAX

    points = [[randrange(min_val, max_val) for _ in xrange(NDIM)] for _ in xrange(NPOINTS)]
    
    


NBITS = encoding_len(W, HMAX) * NDIM

N_INTERVALS = 3 # Number of hypercubes around each point

ACTION_NAME = 'send_back'



def generate_entries():
    entries = []

    # Intervals must be the outer loop for TCAM priority to work out properly. Smaller intervals
    # should always come first.
    for spread in range(N_INTERVALS):                
        for point in points:
            
            if spread == 0:
                word, width = tcode_ndim_point(point, W, HMAX)
                assert(width <= MAX_BITS)
                entries.append((point, spread, word))
            else:
                lowers = [dim - spread for dim in point]
                uppers = [dim + spread for dim in point]

                (word, mask), width = tcode_ndim_interval(lowers, uppers, W, HMAX)
                assert(width <= MAX_BITS)

                # Need to invert the mask, or we make P4 very unhappy
                imask = ~mask

                #P4 also wants the word to be 0'd on the wildcard bits
                word = word & imask

                entries.append((point, spread, (word, imask)))
                
    return entries

ENTRIES = generate_entries()

if __name__ == '__main__':
    
    print(p4templatelong.start)
    for idx, (point, spread, entry) in enumerate(ENTRIES):
        if spread == 0:
            print('    \t{} : {}({});'.format(entry, ACTION_NAME, idx + 1))
        else:
            word, mask = entry
            iimask = ~mask
            print('    \t{} &&& ~({}w{}) : {}({});'.format(word, MAX_BITS, iimask, ACTION_NAME, idx + 1))
    print(p4templatelong.end)    
