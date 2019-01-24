#!/usr/bin/env python
# title           : this_python_file.py
# description     :This will create a header for a python script.
# author          :bryant.chhun
# date            :12/12/18
# version         :0.0
# usage           :python this_python_file.py -flags
# notes           :
# python_version  :3.6

from sklearn.metrics import mean_squared_error
from datetime import datetime
import os

def mse(y_pred, y_target):
    start = datetime.now()
    mse = mean_squared_error(y_target, y_pred)
    stop = datetime.now()
    print("\tmse value = "+str(mse))
    print("\ttime for MSE calculation = " + str((stop - start).microseconds) +"\n")
    return mse

def testDataPath():
    '''
    To get the absolute path of the test data.
        This is needed because code that calls RetrieveData from different locations either all
        need to use absolute paths, or need to call relative paths properly.  This method eliminates that need.
    :return:
    '''
    dir = os.path.dirname(__file__)
    test_data_path = os.path.join(dir, './testData/rawData/2018_10_02_MouseBrainSlice/')
    return test_data_path