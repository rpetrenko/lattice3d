#!/usr/bin/env python

import argparse
import os
from os.path import expanduser
import pandas as pd
import numpy as np
from functools import reduce
import operator


def memory_usage_MB(df):
    bytes = df.memory_usage().sum()
    return bytes/1024./1024.


def load_file(fname):
    dtypes = {"x": np.int8, "y": np.int8, "z": np.int8, "value": np.float32}
    # you can set dtypes to None to verify that default loading of data will consume 28 MB in RAM
    # just using proper types shrinks memory footprint to 6 MB
    df = pd.read_csv(fname, header=None, names=["x", "y", "z", "value"], sep=" ", index_col=False, dtype=dtypes)
    print("Loaded file {}, shape={}".format(fname, df.shape))
    assert len(df.shape) == 2, "shape is wrong"
    assert df.shape[0] > 0, "no data"
    assert df.shape[1] == 4, "should have 4 columns"
    print("Dataframe memory usage {:.3f} MB; shape {}".format(memory_usage_MB(df), df.shape))
    # set  x, y, z as indices
    df = df.groupby(['x', 'y', 'z'])['value'].mean()
    return df


def get_xyz_ranges(df):
    df_idx = df.index
    l_ind = []
    for i in range(3):
        idx = df_idx.levels[i]
        mi, ma, n = min(idx), max(idx), idx.shape[0]
        l_ind.append({"min": mi, "max": ma, "n": n})
    print("Total elements {}".format(reduce(operator.mul, [x['n'] for x in l_ind])))
    return l_ind


def get_missing_elements(df):
    return df[df['value'].isnull()].copy()


def get_idx_neighbours(i, j, k, l_ind):
    """
    Get max 6 neighbouring cells: i+-1, j+-1, k+-1
    :param i:
    :param j:
    :param k:
    :param l_ind:
    :return:
    """
    res = list()
    if i-1 >= l_ind[0]['min']:
        res.append((i-1, j, k))
    if i+1 <= l_ind[0]['max']:
        res.append((i+1, j, k))
    if j-1 >= l_ind[1]['min']:
        res.append((i, j-1, k))
    if j+1 <= l_ind[1]['max']:
        res.append((i, j+1, k))
    if k-1 >= l_ind[2]['min']:
        res.append((i, j, k-1))
    if k+1 <= l_ind[2]['max']:
        res.append((i, j, k+1))
    return res


def fill_cell_neighbours(sr, cell, l_ind):
    s = 0
    c = 0
    if sr.loc[cell].isnull().value:
        i, j, k = cell
        idx_neighbor = get_idx_neighbours(i, j, k, l_ind)
        for l, m, n in idx_neighbor:
            # print("index",l,m,n)
            x = sr.loc[(l,m,n)]
            # print(x)
            if not x.isnull().value:
                c += 1
                s += x
        if c != 0:
            x = s / float(c)
            sr.loc[cell] = x


def fill_missing_average6(df_missing, df):
    """
    Fill missing elements as average of the up to 6 nearest neighbors elements
    :param df:
    :return:
    """
    l_ind = get_xyz_ranges(df)
    for cell in df_missing.index.tolist():
        fill_cell_neighbours(df, cell, l_ind)
    return df


def create_cuboid_shape(l_ind):
    index = pd.MultiIndex.from_product([range(l_ind[0]['min'], l_ind[0]['max'] + 1),
                                        range(l_ind[1]['min'], l_ind[1]['max'] + 1),
                                        range(l_ind[2]['min'], l_ind[2]['max'] + 1)],
                                       names=["x", "y", "z"])
    return index


def run(fname):
    print("Running file: {}".format(fname))
    df = load_file(fname)
    idx_ranges = get_xyz_ranges((df))
    print("Index ranges {}".format(idx_ranges))
    x_n, y_n, z_n = idx_ranges[0]['n'], idx_ranges[1]['n'], idx_ranges[2]['n']
    tot_size = x_n * y_n * z_n
    if df.shape[0] != tot_size:
        print("Some values are missing, trying to fix it")
        print("Number of missing elements {}".format(tot_size - df.shape[0]))
        index = create_cuboid_shape(idx_ranges)
        df = pd.DataFrame(df, index=index)
        df_missing = get_missing_elements(df)
        print("Missing element cells")
        print(df_missing.index.tolist())
        df = fill_missing_average6(df_missing, df)
        df_missing = get_missing_elements(df)
        if df_missing.shape[0] != 0:
            raise Exception("after filling 6 neighbours, there are still missing elements, consider other fill-in strategies")
    else:
        index = df.index
    print("Reshaping to proper size {} {} {}".format(x_n, y_n, z_n))
    mat = df.as_matrix().reshape((x_n, y_n, z_n))
    print("Calculating gradients along each axis")
    mat_x = np.gradient(mat, axis=0)
    mat_y = np.gradient(mat, axis=1)
    mat_z = np.gradient(mat, axis=2)
    dfx = pd.DataFrame(mat_x.reshape(tot_size, 1), index=index)
    dfy = pd.DataFrame(mat_y.reshape(tot_size, 1), index=index)
    dfz = pd.DataFrame(mat_z.reshape(tot_size, 1), index=index)
    return dfx, dfy, dfz


def df_save(df, fname):
    print("Saving dataframe to {}".format(fname))
    df.to_csv(fname, sep=" ", header=False, index=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="""
           usage:  python gradients.py --data-file lattice3x3x3-linear.txt --out-dir out
        """
    )
    parser.add_argument("--data-file", help="filename with data in format x,y,z,value", required=True)
    parser.add_argument("--out-dir", help="output dir", required=True)
    args = parser.parse_args()
    if not args.data_file:
        parser.print_help()
        exit(1)
    fname = expanduser(args.data_file)
    if os.path.exists(fname):
        dfx, dfy, dfz = run(fname)
        outdir = args.out_dir
        df_save(dfx, "{}/{}".format(outdir, "dfx_out.txt"))
        df_save(dfy, "{}/{}".format(outdir, "dfy_out.txt"))
        df_save(dfz, "{}/{}".format(outdir, "dfz_out.txt"))
        print("done")
    else:
        raise Exception("file not found {}".format(fname))

