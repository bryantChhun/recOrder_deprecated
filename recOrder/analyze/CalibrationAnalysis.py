# bchhun, {2019-08-09}
from recOrder.analyze import AnalyzeBase
from recOrder.microscope.mm2python_simple import set_lc, get_lc, define_lc_state, \
    set_lc_state, snap_and_retrieve

import numpy as np
from scipy import optimize

"""
functions to run LC optimization
"""


class CalibrationAnalysis(AnalyzeBase):

    PROPERTIES = {'LCA': 'Retardance LC-A [in waves]',
                  'LCB': 'Retardance LC-B [in waves]',
                  'State0': 'Pal. elem. 00; enter 0 to define; 1 to activate',
                  'State1': 'Pal. elem. 01; enter 0 to define; 1 to activate',
                  'State2': 'Pal. elem. 02; enter 0 to define; 1 to activate',
                  'State3': 'Pal. elem. 03; enter 0 to define; 1 to activate',
                  'State4': 'Pal. elem. 04; enter 0 to define; 1 to activate',
                  }

    def __init__(self, gateway_):
        super().__init__()
        self.gateway = gateway_
        self.entry_point = self.gateway.entry_point
        self.mm = self.entry_point.getStudio()
        self.mmc = self.entry_point.getCMMCore()

        # other vars
        self.lcExt = None
        self.swing = None
        self.wavelength = None
        self.lc_bound = None
        self.l_elliptical = None

    def opt_lc(self, x, device_property, method, reference):
        """
        function to optimize using a scipy.optimize
        :param x: int,float
            input value
        :param device_property: str
            Meadowlark device property to adjust (LCA or LCB)
        :param method: str
            'mean' or other calculation
        :param reference: int, float
            prior output against which to optimize
        :return: float
        """
        set_lc(x, self.waves, device_property)

        # snap and return metric
        data = snap_and_retrieve(self.entry_point)
        if method == 'mean':
            return np.abs(np.mean(data) - reference)

    def iter_opt(self, lca_bound_, lcb_bound_, reference, num_iter):
        """
        call scipy.optimize on the opt_lc function with arguments
        each iteration loop optimizes on LCA and LCB once
        Bounds are around CURRENT LCA/LCB values

        :param lca_bound_: float
            half the range to restrict the search for LCA
        :param lcb_bound_: float
            half the range to restrict the search for LCB
        :param reference: float
            optimize difference between opt_lc output and this value
        :param num_iter: int
            number of LCA-LCB cycles
        :return:
        """
        if lca_bound_ < 0.01 or lca_bound_ > 1.6:
            raise ValueError("lc_bound must be within the allowed LC range [0.01, 1.6]")
        if lcb_bound_ < 0.01 or lcb_bound_ > 1.6:
            raise ValueError("lc_bound must be within the allowed LC range [0.01, 1.6]")

        for i in range(num_iter):
            print("lca lcb iteration # " + str(i))
            current_lca = get_lc(self.mmc, self.PROPERTIES['LCA'])
            current_lcb = get_lc(self.mmc, self.PROPERTIES['LCB'])

            # check that bounds don't exceed range of LC
            lca_lower_bound = 0.01 if (current_lca - lca_bound_) <= 0.01 else current_lca - lca_bound_
            lca_upper_bound = 1.6 if (current_lca + lca_bound_) >= 1.6 else current_lca + lca_bound_

            lcb_lower_bound = 0.01 if current_lcb - lcb_bound_ <= 0.01 else current_lcb - lcb_bound_
            lcb_upper_bound = 1.6 if current_lcb + lcb_bound_ >= 1.6 else current_lcb + lcb_bound_

            # optimize lca
            """
            xopt = optimal value of LC
            fval = output of opt_lc (mean intensity)
            ierr = error flag
            numfunc = number of function calls
            """
            xopt0, fval0, ierr0, numfunc0 = optimize.fminbound(self.opt_lc,
                                                               x1=lca_lower_bound,
                                                               x2=lca_upper_bound,
                                                               args=(
                                                                   self.PROPERTIES['LCA'],
                                                                   'mean',
                                                                   reference),
                                                               full_output=True
                                                               )
            print("\tlca = " + str(xopt0))
            print("\tdifference intensity = " + str(fval0))

            # optimize lcb
            xopt1, fval1, ierr1, numfunc1 = optimize.fminbound(self.opt_lc,
                                                               x1=lcb_lower_bound,
                                                               x2=lcb_upper_bound,
                                                               args=(
                                                                   self.PROPERTIES['LCB'],
                                                                   'mean',
                                                                   reference),
                                                               full_output=True
                                                               )
            print("\tlcb = \t" + str(xopt1))
            print("\tdifference intensity = \t" + str(fval1))
        return fval1

    def search_iExt(self, a_min, a_max, b_min, b_max, lc_bound):
        """
        do a standard grid search to optimize LCA and LCB
        :param a_min:
        :param a_max:
        :param b_min:
        :param b_max:
        :return:
        """
        min_int = 65536
        better_lca = -1
        better_lcb = -1

        # coarse search
        for lca in np.arange(a_min, a_max, 0.1):
            for lcb in np.arange(b_min, b_max, 0.1):
                set_lc(self.mmc, lca, self.PROPERTIES['LCA'])
                set_lc(self.mmc, lcb, self.PROPERTIES['LCB'])
                current_int = np.mean(snap_and_retrieve(self.entry_point))
                if current_int < min_int:
                    better_lca = lca
                    better_lcb = lcb
                    min_int = current_int
                    print("update (%f, %f, %f)" % (min_int, better_lca, better_lcb))

        print("coarse search done")
        print("better lca = " + str(better_lca))
        print("better lcb = " + str(better_lcb))
        print("better int = " + str(min_int))

        best_lca = better_lca
        best_lcb = better_lcb

        # fine search using grid search
        # for lca in np.arange(better_lca - 0.02, better_lca + 0.02, 0.002):
        #     for lcb in np.arange(better_lcb - 0.02, better_lcb + 0.02, 0.002):
        #         lca = 0.01 if lca <= 0.01 else lca
        #         lca = 1.6 if lca >= 1.6 else lca
        #
        #         lcb = 0.01 if lcb <= 0.01 else lcb
        #         lcb = 1.6 if lcb >= 1.6 else lcb
        #
        #         set_lc(lca, PROPERTIES['LCA'])
        #         set_lc(lcb, PROPERTIES['LCB'])
        #         current_int = np.mean(snap_and_retrieve())
        #         if current_int < min_int:
        #             best_lca = lca
        #             best_lcb = lcb
        #             min_int = current_int
        #             print("update (%f, %f, %f)" % (min_int, best_lca, best_lcb))

        # fine search using brent's
        set_lc(self.mmc, best_lca, self.PROPERTIES['LCA'])
        set_lc(self.mmc, best_lcb, self.PROPERTIES['LCB'])
        min_int = self.iter_opt(lc_bound, lc_bound, 0, 1)

        best_lca = get_lc(self.mmc, self.PROPERTIES['LCA'])
        best_lcb = get_lc(self.mmc, self.PROPERTIES['LCB'])

        print("fine search done")
        print("best lca = " + str(best_lca))
        print("best lcb = " + str(best_lcb))
        print("best int = " + str(min_int))

        return min_int

    # ========== Optimization wrappers =============
    # ==============================================

    @AnalyzeBase.emitter(channel=10)
    def opt_Iext(self, lc_bound_):
        """
        find lca and lcb values that minimize intensity
        :param lc_bound_: float
            half the range to restrict the search
        :return: tuple
            (lca, lcb) at extinction
        """
        set_lc(self.mmc, 0.25, self.PROPERTIES['LCA'])
        set_lc(self.mmc, 0.5, self.PROPERTIES['LCB'])

        # i_ext = iter_opt(lc_bound_, lc_bound_, 0, 1)
        i_ext_ = self.search_iExt(0.01, 1.5, 0.01, 1.5, lc_bound_)

        define_lc_state(self.mmc, self.PROPERTIES, self.PROPERTIES['State0'])
        lca_ext_ = get_lc(self.mmc, self.PROPERTIES['LCA'])
        lcb_ext_ = get_lc(self.mmc, self.PROPERTIES['LCB'])
        return lca_ext_, lcb_ext_, i_ext_

    @AnalyzeBase.emitter(channel=11)
    def opt_I1(self):
        """
        no optimization performed for this.  Simply apply swing and read intensity
        This is the same as "Ielliptical"
        :return: float
            mean of image
        """

        set_lc(self.mmc, self.lcExt[0] + self.swing, self.PROPERTIES['LCA'])
        set_lc(self.mmc, self.lcExt[1], self.PROPERTIES['LCB'])

        define_lc_state(self.mmc, self.PROPERTIES, self.PROPERTIES['State1'])

        image = snap_and_retrieve(self.entry_point)
        return np.mean(image), get_lc(self.mmc, self.PROPERTIES['LCA']), get_lc(self.mmc, self.PROPERTIES['LCB'])

    @AnalyzeBase.emitter(channel=12)
    def opt_I2(self, lca_bound, lcb_bound):
        """
        optimized relative to Ielliptical
        Parameters
        ----------
        lca_bound
        lcb_bound

        Returns
        -------

        """
        set_lc(self.mmc, self.lcExt[0], self.PROPERTIES['LCA'])
        set_lc(self.mmc, self.lcExt[1] + self.swing, self.PROPERTIES['LCB'])

        self.iter_opt(lca_bound, lcb_bound, self.l_elliptical, 1)

        define_lc_state(self.mmc, self.PROPERTIES, self.PROPERTIES['State2'])

        return get_lc(self.mmc, self.PROPERTIES['LCA']), get_lc(self.mmc, self.PROPERTIES['LCB'])

    @AnalyzeBase.emitter(channel=13)
    def opt_I3(self, lca_bound, lcb_bound):
        """

        Parameters
        ----------
        lca_bound
        lcb_bound

        Returns
        -------

        """
        set_lc(self.mmc, self.lcExt[0], self.PROPERTIES['LCA'])
        set_lc(self.mmc, self.lcExt[1] - self.swing, self.PROPERTIES['LCB'])

        self.iter_opt(lca_bound, lcb_bound, self.l_elliptical, 1)

        define_lc_state(self.mmc, self.PROPERTIES, self.PROPERTIES['State3'])

        return get_lc(self.mmc, self.PROPERTIES['LCA']), get_lc(self.mmc, self.PROPERTIES['LCB'])

    @AnalyzeBase.emitter(channel=14)
    def opt_I4(self, lca_bound, lcb_bound):
        """

        Parameters
        ----------
        lca_bound
        lcb_bound

        Returns
        -------

        """
        set_lc(self.mmc, self.lcExt[0] - self.swing, self.PROPERTIES['LCA'])
        set_lc(self.mmc, self.lcExt[1], self.PROPERTIES['LCB'])

        self.iter_opt(lca_bound, lcb_bound, self.l_elliptical, 1)

        define_lc_state(self.mmc, self.PROPERTIES, self.PROPERTIES['State4'])

        return get_lc(self.mmc, self.PROPERTIES['LCA']), get_lc(self.mmc, self.PROPERTIES['LCB'])

    def calculate_extinction(self):
        return (1 / np.sin(2 * np.pi * self.swing) ** 2) * \
               (self.l_elliptical - self.I_black) / (self.i_ext - self.I_black)

    @AnalyzeBase.receiver(channel=20)
    def full_calibration(self, swing, wavelength, lc_bound):
        # optimize to find extinction, increase bound to broaden range
        print("optimizing and setting iExt")
        self.swing = swing
        self.wavelength = wavelength
        self.lc_bound = lc_bound

        lca_ext, lcb_ext, i_ext = self.opt_Iext(lc_bound)

        self.lcExt = (lca_ext, lcb_ext)

        # record I0 'elliptical' state
        print("recording lelliptical")
        self.l_elliptical, _, _ = self.opt_I1()

        # optimize I45, I90, I135 based on lelliptical
        print("setting I2")
        self.opt_I2(0.005, 0.01)
        print("setting I3")
        self.opt_I3(0.005, 0.01)
        print("setting I4")
        self.opt_I4(0.01, 0.005)
        print("EXTINCTION = %d" % self.calculate_extinction())
