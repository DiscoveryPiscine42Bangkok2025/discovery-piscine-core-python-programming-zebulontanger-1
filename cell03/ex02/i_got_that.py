#!/usr/bin/env python3

say = input("What you gotta say? : ")

if say != 'STOP':
    while True:
        say = input("I got that! Anything else? : ")
        if say == "STOP":
            break