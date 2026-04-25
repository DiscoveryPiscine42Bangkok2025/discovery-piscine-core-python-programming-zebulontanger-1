#!/usr/bin/env python3
import sys

args = sys.argv[1:]

if args:
    for arg in args:
        if len(arg) > 8:
            processed = arg[:8]
        elif len(arg) < 8:
            processed = arg.ljust(8, 'Z')
        else:
            processed = arg
        
        print(processed)
else:
    print('none')