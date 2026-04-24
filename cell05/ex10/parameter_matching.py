#!/usr/bin/env python3

import sys

if len(sys.argv) > 1:
    txt = sys.argv[1]

    word = input("What was the parameter? ")

    if word == txt:
        print("Good Job!")
    else:
        print("Nope, sorry...")

else:
    print('none')