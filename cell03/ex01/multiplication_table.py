#!/usr/bin/env python3

n = int(input("Enter a number\n"))

for i in range(10):
    m = i * n
    print("%d x %d = %d" % (i, n, m))