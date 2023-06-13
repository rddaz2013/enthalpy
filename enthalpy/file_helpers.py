import os
import glob
import re

import numpy as np
import pandas as pd

import plot_helpers
import integration
import derivation


def clean_file(filepath):
    """
    INPUT: filepath
    OUTPUT: Pandas dataframe

    Takes a .txt file and outputs a cleaned, renamed Pandas df. Note: skiprows
    is predefined to 49; this depends on your data structure.
    """

    f = pd.read_table(filepath, skiprows = 49, encoding='utf-16', delimiter='\t')
    f.reset_index(inplace = True)
    colnames = ['time', 'temp', 'heat_flow', 'purge_flow']
    f.columns = colnames
    return f

def get_file_title(filepath):
    return float(re.findall(r"[-+]?\d*\.\d+|\d+", filepath)[0])

def get_dir(append = ''):
    """
    Changes to a custom subdirectory in the HC directory
    """
    filepath = '/Users/Logan/Google Drive/hampton_creek/' + append
    os.chdir(filepath)

def get_files():
    get_dir('data/raw/all_preps')
    return list(glob.glob("*.txt"))
