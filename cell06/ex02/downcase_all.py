#!/usr/bin/env python3
import sys

def downcase_it(args_list):
    for arg in args_list:
        word = arg.lower()
        print(word)

if len(sys.argv) > 1:
    downcase_it(sys.argv[1:])
else:
    print('none')