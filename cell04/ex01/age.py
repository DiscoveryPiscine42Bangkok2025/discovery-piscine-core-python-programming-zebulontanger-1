#!/usr/bin/env python3

age = int(input("Please tell me your age: "))
c_age = age
print(f"You are currently {age} years old.")

for i in range(10, 40, 10):
    age = c_age
    age += i
    print(f"In {i} years, you'll be {age} years old.")