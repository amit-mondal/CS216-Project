#!/usr/bin/env python

from __future__ import print_function

import argparse
import sys
import socket
import random
import struct
import re

from scapy.all import sendp, send, srp1
from scapy.all import Packet, hexdump
from scapy.all import Ether, BitField, XByteField, IntField
from scapy.all import bind_layers
import readline

from tcamknn import *
from generate_p4 import ENTRIES, NDIM, W, HMAX, NBITS, MAX_BITS, points

from random import randrange


class TCAMLookup(Packet):
    name = 'TCAMLookup'
    fields_desc = [
        BitField('key', 0, MAX_BITS)
    ]


bind_layers(Ether, TCAMLookup, type=0x1234)


def main():

    s = ''
    iface = 'eth0'

    if len(sys.argv) > 1 and len(sys.argv) != NDIM + 1:
        print('Number of command line args must match the number of dimensions {}'.format(NDIM))
        sys.exit(1)

    if len(sys.argv) == 1:
        idx = randrange(0, len(points))
        point = points[idx]
        print('Chose random point {}'.format(point))
    else:
        point = [int(e) for e in sys.argv[1:]]
        
    key, width = tcode_ndim_point(point, W, HMAX)

    assert(width == NBITS)
    assert(width <= MAX_BITS)
    
    try:
        pkt = Ether(dst='00:04:00:00:00:00', type=0x1234) / TCAMLookup(key=key)
        pkt = pkt/' '

        #pkt.show()

        resp = srp1(pkt, iface=iface, timeout=1, verbose=False)
        if resp:
            tcamlookup=resp[TCAMLookup]
            if tcamlookup:

                if tcamlookup.key == 0:
                    print('no TCAM match')
                else:
                    point, spread, entry = ENTRIES[tcamlookup.key - 1]
                    print('matched point {}, cube spread {}'.format(point, spread))
                
            else:
                print("cannot find tcam header in the packet")
        else:
            print("Didn't receive response")
    except Exception as error:
        print(error)


if __name__ == '__main__':
    main()

    
