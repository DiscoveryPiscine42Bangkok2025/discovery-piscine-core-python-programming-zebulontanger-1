#!/usr/bin/env python3
import sys
del sys.argv[0]

def downcase_it(*args):
    return args.lower()

if len(sys.argv) > 0:
    downcase_it()
else:
    print('none')