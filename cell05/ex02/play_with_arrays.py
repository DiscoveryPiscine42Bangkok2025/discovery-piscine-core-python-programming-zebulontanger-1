#!/usr/bin/env python3

old_array = [2, 3, 5, 7, 11, 13, 17, 19, 23]
new_array = []

for i in range(len(old_array)):
    n = int(old_array[i])
    
    if n > 5:
        n += 2

        new_array.append(n)

print("Original array: " + str(old_array))
print("New array: " + str(new_array))