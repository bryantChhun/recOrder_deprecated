#!/usr/bin/env python
# title           :
# description     :
# author          :bryant.chhun
# date            :1/29/19
# version         :0.0
# usage           :
# notes           :
# python_version  :3.6

import unittest

from recOrder.acquire.FileManagement import MonitorDatastores


class TestImageReconstruction(unittest.TestCase):
    """
    Some tests and setup code borrowed from :
    https://github.com/bartdag/py4j/blob/master/py4j-python/src/py4j/tests/java_gateway_test.py

    """

    def setup(self):
        gateway = JavaGateway()
        self.monitor = MonitorDatastores(gateway)

    def test_slots(self):
        return None

    def test_timeout(self):
        self.setup()
        self.monitor.run()

    def test_gateway(self):
        return None


    def test_set_acquired(self):
        #to check that a set of 4 or 5 states is acquired and stored
        return None


    def test_emitter(self):
        # to check that the data is emitted to pipeline correctly
        return None


class MethodTest(unittest.TestCase):
    def setUp(self):
        self.p = start_example_app_process()
        # This is to ensure that the server is started before connecting to it!
        self.gateway = JavaGateway()

    def tearDown(self):
        safe_shutdown(self)
        self.p.join()

    def testNoneArg(self):
        ex = self.gateway.getNewExample()
        try:
            ex.method2(None)
            ex2 = ex.method4(None)
            self.assertEquals(ex2.getField1(), 3)
            self.assertEquals(2, ex.method7(None))
        except Exception:
            print_exc()
            self.fail()

    def testUnicode(self):
        sb = self.gateway.jvm.java.lang.StringBuffer()
        sb.append("\r\n\tHello\r\n\t")
        self.assertEqual("\r\n\tHello\r\n\t", sb.toString())

    def testEscape(self):
        sb = self.gateway.jvm.java.lang.StringBuffer()
        sb.append("\r\n\tHello\r\n\t")
        self.assertEqual("\r\n\tHello\r\n\t", sb.toString())