### Computing gradients on a 3D lattice
This project demonstrates usage of numpy gradients with 3D arrays

* we'll compute gradients along each axis for a 3D lattice with some values at each point (x, y, z)
* x, y, z are integers, and values are floats
* to generate test file with 3x3x3 linear cell, and two missing cells (0,0,0) and (0,1,1)
```bash
generate_data.py
```
* in the test file we'll intentionally make (0,0,0) element as NaN
* the missing values are computed as average of neighbouring elements x,y,z +/- 1, excluding diagonals
* run against sample file
```bash
 python gradients.py --data-file lattice3x3x3-linear.txt --out-dir out
```
