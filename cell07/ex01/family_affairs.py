#!/usr/bin/env python3

def find_the_redheads(dupont_families_dict):
    return [f"{first}" for first, last in dupont_families_dict.items() if last == 'red']

dupont_family = {
"florian": "red",
"marie": "blond",
"virginie": "brunette",
"david": "red",
"franck": "red"
}
print(find_the_redheads(dupont_family))