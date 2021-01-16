import os
import json

basedir = os.path.dirname(__file__)

def make_datadir():
    data_loc = os.path.join(basedir,'..','data')
    if not os.path.exists(data_loc):
        os.mkdir(data_loc)
    return