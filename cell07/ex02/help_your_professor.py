#!/usr/bin/env python3

def average(class_dict):
    t_score = 0
    count = 0
    avg = 0
    for name, score in class_dict.items():
        t_score += int(score)
        count += 1

    avg = t_score / count

    return f"{avg:.2f}"

class_3B = {
"marine": 18,
"jean": 15,
"coline": 8,
"luc": 9
}
class_3C = {
"quentin": 17,
"julie": 15,
"marc": 8,
"stephanie": 13
}

print(f"Average for class 3B: {average(class_3B)}.")
print(f"Average for class 3C: {average(class_3C)}.")

