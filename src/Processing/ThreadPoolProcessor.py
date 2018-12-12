#!/usr/bin/env python
# title           : this_python_file.py
# description     :This will create a header for a python script.
# author          :bryant.chhun
# date            :12/12/18
# version         :0.0
# usage           :python this_python_file.py -flags
# notes           :
# python_version  :3.6

from concurrent.futures import ThreadPoolExecutor


"""
Singleton for a shared ThreadPoolExecutor service
    meant for threaded image processing
"""
class tpExecutor():

    _recon_Executor = ThreadPoolExecutor(max_workers = 10)

    def getExecutor(self):
        if not self._recon_Executor:
            self._recon_Executor = ThreadPoolExecutor(max_workers=10)
        return self._recon_Executor
