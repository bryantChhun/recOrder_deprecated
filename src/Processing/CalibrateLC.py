#!/usr/bin/env python
# title           :
# description     :
# author          :bryant.chhun
# date            :2/18/19
# version         :0.0
# usage           :
# notes           :
# python_version  :3.6


"""
this module will be called from the ReconOrderUI button
"""
class CalibrateLC:

    def __init__(self):
        # inherit py4j?
        self.state0 = (float, float)
        self.state1 = (float, float)
        self.state2 = (float, float)
        self.state3 = (float, float)
        self.state4 = (float, float)

        self.state_ref = (float, float)

        self.swing = 0.03

        #Connect signals to py4j
        #any data inits...

    def start(self):
        #snap_lext
        # minimize

        # minimize( snap_lext , min)
        # record state0

        # snap_l0
        # record state1
        # record avg int, save as lelliptical

        # minimize( snap_l45, current-lelliptical)
        # record state2

        # minimize( snap_l90, current-lelliptical)
        # record state3

        # minimize( snap_l135, current-lelliptical)
        # record state4

        # write all states to deviceAdapter


        return None

    def minimize_gd(self, func, target):
        #gradient descent using func(math) on target(func) until minimum is found

        # iterate:
        # snap (func: that returns value)
        # calculate metric (target: current-elliptical or abs min)
        # calculate gradient
        # make lca/lcb adjustments (plus/minus current)
        # end loop
        return None

    def minimize_brents(self, func, target):
        #brent's root finding using func on target until minimum is found

        # iterate:
        # snap (function that returns value)
        # calculate metric (current-elliptical)
        # calculate gradient
        # make lca/lcb adjustments
        # end loop
        return None

    def snap_lext(self):
        #return float intensity
        return None

    def snap_l0(self):
        #return float intensity
        return None

    def snap_l45(self):
        #return float intensity
        return None

    def snap_l90(self):
        #return float intensity
        return None

    def snap_l135(self):
        #return float intensity
        return None

    @property
    def LCA(self):
        return None

    @LCA.setter
    def LCA(self):
        #adjustment should be atomic and blocking?
        return None

    @property
    def LCB(self):
        return None

    @property
    def LCB(self):
        #adjustment should be atomic and blocking?
        return None


