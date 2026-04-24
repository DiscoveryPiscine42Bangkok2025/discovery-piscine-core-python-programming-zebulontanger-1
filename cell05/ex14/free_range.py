#!/usr/bin/env python3

import sys

del sys.argv[0]

if len(sys.argv) == 2:
    num1 = int(sys.argv[0])
    num2 = int(sys.argv[1])

    l = []

    for i in range(num1, num2 + 1):
        l.append(str(i))
    
    print(f"[{', '.join(l)}]")


  
else:
    print('none')