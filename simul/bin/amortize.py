#!/usr/bin/env python3
# -*- coding: utf-8 -*-
########################################
# Runs qemu.sh for each group X times.
# Group1 is ran x times with each base/incr result appended into an base and inc array.
# At the end of iterations the np.mean / np.std is applied on the base/inc arrays and stored for future output.
########################################

import subprocess
from subprocess import run
import bicosts
import argparse
import os
import numpy as np
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt

DFLT = {
    'cpi' : 1,
    'brt' : 2048,
    'group': 6,
    'iter': 10,
}

def arguments():
    '''
    Parses the arguments from the command line

    returns an argparse.ArgumentParser.parse_args() object
    '''
    fclass = argparse.ArgumentDefaultsHelpFormatter
    parser = argparse.ArgumentParser(formatter_class=fclass)

    parser.add_argument('-c', '--cpi', type=int, default=DFLT['cpi'],
                        help='Constant for cycles per instruction')
    parser.add_argument('-b', '--brt', type=int, default=DFLT['brt'],
                        help='Constant for block reload time')
    parser.add_argument('-g', '--group', type=int, default=DFLT['group'],
                        help='Range of fj-g1 folders, default is fj-g1 - fj-g6')
    parser.add_argument('-i', '--iter', type=int, default=DFLT['iter'],
                        help='QEMU cachelog generations')
    parsed = parser.parse_args()
    return parsed


def main():
    '''
    Script entry point
    Amortizes cores, and objects for a forkjoin folder.
    ASSUMES the fork-join task structure of the fj-g* sample directories.
    '''
    args = arguments()

    if(args.iter < 1):
        print("Error iterations must be greater than 1.")
        exit()

    print(args)

    # Bench Names
    bench_names = [["bs", "bssort100", "crc"],
                    ["expinit", "fft", "insertsort"],
                    ["jfdctint", "lcdnum", "matmult"],
                    ["minver","ns","nsichneu"],
                    ["qurt", "select", "simple"],
                    ["sqrt", "statemate","ud"]]

    # Directory Paths
    wd = os.getcwd()
    qemu_path = wd + '/bin/qemu.sh'

    # Metric Folder/ File
    metric_dir = wd + "/bin" + "/metrics"

    # Create Folder if Not Exists
    isExist = os.path.exists(metric_dir)
    if not isExist:
        print("Creating metric directory.")
        os.makedirs(metric_dir)

    metric_file = open(metric_dir + "/metrics.txt", "w")

    # Arrays for aggregating data
    baseArray = []
    incrArray = []

    # Used for storing Group Data For Future Printing
    groupData = []

    # Prepare Table Headers
    LAYOUT = "{!s:<12} | {!s:10} | {!s:10} | {!s:10} | {!s:10}"
    layHeader = ["Benchmarks", "Base", "BaseStd.", "Inc", "IncStd."]

    benchCount = 1;

    # Loop Through All fg-x folders
    for j in range(args.group):

        # Obtain fg-x/risv32-img directory
        os.chdir("..")
        os.chdir(wd + '/' + "fj-g" + str(j+1))
        risv32_img_path = os.getcwd() + '/riscv32-img'

        # Run fg-x X iterations
        for i in range(args.iter):

            # Run QEMU and Generate Cache Log
            qemu_run = run(['sh', qemu_path, risv32_img_path])
            if qemu_run.returncode != 0:
                print("Could not qemu.sh, please check your directory.")
                exit()
            # Obtain Bicosts
            objectCosts = bicosts.modstart('cache.log', args.cpi, args.brt)

            # Empty Lists to convert into NP
            base_list = []
            incr_list = []

            for obj_x in range(len(objectCosts)):
                base_list.append(objectCosts[obj_x]['base'])
                incr_list.append(objectCosts[obj_x]['incrf'])


            # Convert into 2D NP
            base_list = [np.array(base_list)]
            incr_list = [np.array(incr_list)]

            # Set Initial Arrays for Cocatenate
            if i == 0:
                baseArray = base_list
                incrArray = incr_list
            else:
                baseArray = np.concatenate((baseArray, base_list), axis=0)
                incrArray = np.concatenate((incrArray, incr_list), axis=0)


        # For Each Benchmark in Each Group

        for x in range(len(baseArray[0])):
            groupRow = []
            #Benchmarks| Base | Base Std.| Inc | Inc Std.
            groupRow.append(bench_names[j][x])

            # Rounded to 4 Decimal Points, Change As Desired
            groupRow.append(np.around(np.mean(baseArray[:,x]), 6))
            groupRow.append(np.around(np.std(baseArray[:,x]), 6))
            groupRow.append(np.around(np.mean(incrArray[:,x]), 6))
            groupRow.append(np.around(np.std(incrArray[:,x]), 6))

            groupData.append(groupRow)

    # Write And Print Out Results
    metric_file.write(LAYOUT.format(*layHeader))
    print("\n\nResults for " + str(args.iter) + " iterations per group number.\n\n")
    print(LAYOUT.format(*layHeader))

    # Loop for Each Group
    for gnum in (groupData):
        print(LAYOUT.format(*gnum))
        metric_file.writelines("\n" + LAYOUT.format(*gnum))
    metric_file.close
    print("\nEvaluation metrics have been stored in: ", metric_dir)


    os.chdir(wd)
    with open('mrtc-base-incr.tex', 'w') as texfile:
    # Print the LaTeX version
        TEXLAYOUT = "        {!s:<12} & {:10.0f} & {:10.2f} & {:10.2f} & {:10.2e} \\\\"
        start='''\\begin{table}[ht]
  \\begin{center}
    \\begin{tabular}{r|r|c|c|c}
      Benchmark & ${\\beta}$ & ${\\sigma_\\beta}$ & ${\\gamma}$ & ${\\sigma_\\gamma}$ \\\\
      \\hline
'''
        end='''
      \\end{tabular}
    \\caption{MRTC Mean Base ${\\beta}$ and Incremental Costs ${\\gamma}$}
    \\label{table:mrtc-costs}
  \\end{center}
\\end{table}
'''
        print(start)
        texfile.write(start)
        for gnum in (groupData):
            print(TEXLAYOUT.format(*gnum))
            texfile.write(TEXLAYOUT.format(*gnum) + '\n')
        print(end)
        texfile.write(end)
    print('TeX Table Contents: mrtc-base-incr.tex')





if __name__ == '__main__':
    exit(main())
