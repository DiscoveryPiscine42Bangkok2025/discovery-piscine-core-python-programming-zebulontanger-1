#!/usr/bin/env python3

def array_of_names(persons_dict):
    return [f"{first}".capitalize() + ' ' + f"{last}".capitalize() for first, last in persons_dict.items()]

persons = {
    "jean": "valjean",
    "grace": "hopper",
    "xavier": "niel",
    "fifi": "brindacier"
}

print(array_of_names(persons))