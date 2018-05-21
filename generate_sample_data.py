#!/bin/env python

x = 0.
remove_cells = [
    (0, 0, 0),
    (0, 1, 1)
]
for i in range(-1, 2):
    for j in range(-1, 2):
        for k in range(-1, 2):
            if (i, j, k) not in remove_cells:
                print("{} {} {} {}".format(i, j, k, x))
            x += 1.
