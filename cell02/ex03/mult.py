#!/usr/bin/env python3

num1 = int(input())
num2 = int(input())

mult = num1 * num2

print("%d x %d = %d" % (num1, num2, mult))

if mult > 0:
    print("This number is positive.")
elif mult < 0:
    print("This number is negative.")
elif mult == 0:
    print("This number is both positive and negative.")