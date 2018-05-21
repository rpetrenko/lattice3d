* we'll compute gradients along each axis for a 3D lattice with some values at each point (x, y, z)
* x, y, z are integers, and values are floats
* to generate test file with 3x3x3 linear cell
```python
x = 0.
for i in range(-1,2):
    for j in range(-1,2):
        for k in range(-1,2):
            print("{} {} {} {}".format(i,j,k,x))
            x += 1.
```
* in the test file we'll intentionally make (0,0,0) element as NaN
* the missing values are computed as average of neighbouring elements x,y,z +/- 1, excluding diagonals

