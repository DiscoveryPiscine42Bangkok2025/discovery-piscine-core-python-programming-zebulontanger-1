#!/usr/bin/env python3

old_array = [2, 3, 5, 7, 11, 13, 17, 19, 23]
new_array = []

for i in range(len(old_array)):
    n = int(old_array[i])
    
    if n > 5:
        n += 2

        new_array.append(n)

        new_set = set(new_array)

print(old_array)
print(new_set)