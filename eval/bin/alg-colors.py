#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import alive_progress
import comargs
import colo
import colo.GraphParms as gp
import json
import logging
import math
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import numpy
import os
import pandas
import pathlib

def algorithm_colors():
    algs = gp.algs_approx() + gp.algs_dag() + gp.algs_exact();
    str = ''
    for a in algs:
        str = str + f'{a:12s} {gp.get_color(a)}\n'
    return str

def main():
    '''Entry point when used a script'''
    print(algorithm_colors())

if __name__ == '__main__':
    exit(main())
