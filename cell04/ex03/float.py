#!/usr/bin/env python3

n = float(input("Give me a number: "))

if n % 1 != 0:
    print("This number is a decimal.")
else:
    print("This number is an integer.")