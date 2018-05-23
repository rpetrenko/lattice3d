#!/usr/bin/env python

import argparse


def generate_data(min_xyz, max_xyz, missing_cells=None):
    """
    Generate i,j,z cells according to ranges populating cells with their sequential number of creation
    Misinge cells list is used to simulate missing data in real experiments, {i,j,k} cells will be skipped
    :param min_xyz: i_min,j_min,k_min
    :param max_xyz: i_max,j_max,k_max
    :param missing_cells: i1,j1,k1,i2,j2,k2,.... (multiples of 3)
    :return: nothing, print out the results
    """
    x = 0.
    remove_cells = list()
    if missing_cells:
        values = missing_cells.split(",")
        assert len(values) % 3 == 0, "missing cells indices must be multiples of 3"
        cell = []
        for v in values:
            cell.append(int(v))
            if len(cell) == 3:
                remove_cells.append(tuple(cell))
                cell = []
    mins = [int(x) for x in min_xyz.split(',')]
    maxs = [int(x) for x in max_xyz.split(',')]
    i_range = range(mins[0], maxs[0])
    j_range = range(mins[1], maxs[1])
    k_range = range(mins[2], maxs[2])
    for i in i_range:
        for j in j_range:
            for k in k_range:
                if (i, j, k) not in remove_cells:
                    print("{} {} {} {}".format(i, j, k, x))
                x += 1.


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description=""" usage:  python generate_data.py --min-xyz --max-xyz --missing-cells
        """
    )
    parser.add_argument("--min-xyz",
                        help="comma-separated minimum values for i:j:k",
                        required=True)
    parser.add_argument("--max-xyz",
                        help="comma-separated maximum values for i:j:k",
                        required=True)
    parser.add_argument("--missing-cells",
                        help="comma-separated list of  cells to skip, e.g. i1,j1,k1,i2,j2,k2",
                        required=False)
    args = parser.parse_args()
    generate_data(args.min_xyz, args.max_xyz, args.missing_cells)