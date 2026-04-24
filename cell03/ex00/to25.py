#!/usr/bin/env python3

n = int(input("Enter a number less than 25\n"))

if n > 25:
    print("Error")
else:
    while n <= 25:
        print("Inside the loop, my variable is %d" % n)
        n += 1