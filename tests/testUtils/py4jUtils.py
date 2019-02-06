#!/usr/bin/env python
# title           :
# description     :
# author          :bryant.chhun
# date            :1/30/19
# version         :0.0
# usage           :
# notes           :
# python_version  :3.6

"""
All of this setup code is taken from Py4J:
https://github.com/bartdag/py4j/blob/master/py4j-python/src/py4j/tests/java_gateway_test.py

We will use it for our use case when testing our py4j communication.
"""

from collections import deque
from contextlib import contextmanager
from decimal import Decimal
import gc
import math
from multiprocessing import Process
import os
from socket import AF_INET, SOCK_STREAM, socket
import subprocess
import tempfile
from threading import Thread
import time
from traceback import print_exc
import unittest

from py4j.compat import (
    range, isbytearray, ispython3bytestr, bytearray2, long,
    Queue)
from py4j.finalizer import ThreadSafeFinalizer
from py4j.java_gateway import (
    JavaGateway, JavaMember, get_field, get_method,
    GatewayClient, set_field, java_import, JavaObject, is_instance_of,
    GatewayParameters, CallbackServerParameters, quiet_close, DEFAULT_PORT,
    set_default_callback_accept_timeout, GatewayConnectionGuard,
    get_java_class)
from py4j.protocol import (
    Py4JError, Py4JJavaError, Py4JNetworkError, decode_bytearray,
    encode_bytearray, escape_new_line, unescape_new_line, smart_decode)


SERVER_PORT = 25333
TEST_PORT = 25332
PY4J_PREFIX_PATH = os.path.dirname(os.path.realpath(__file__))
PY4J_JAVA_PATHS = [
    os.path.join(PY4J_PREFIX_PATH,
                 "../../../../py4j-java/build/classes/main"),  # gradle
    os.path.join(PY4J_PREFIX_PATH,
                 "../../../../py4j-java/build/classes/test"),  # gradle
    os.path.join(PY4J_PREFIX_PATH,
                 "../../../../py4j-java/build/classes/java/main"),  # gradle 4
    os.path.join(PY4J_PREFIX_PATH,
                 "../../../../py4j-java/build/classes/java/test"),  # gradle 4
    os.path.join(PY4J_PREFIX_PATH,
                 "../../../../py4j-java/build/resources/main"),  # gradle
    os.path.join(PY4J_PREFIX_PATH,
                 "../../../../py4j-java/build/resources/test"),  # gradle
    os.path.join(PY4J_PREFIX_PATH,
                 "../../../../py4j-java/target/classes/"),  # maven
    os.path.join(PY4J_PREFIX_PATH,
                 "../../../../py4j-java/target/test-classes/"),  # maven
    os.path.join(PY4J_PREFIX_PATH,
                 "../../../../py4j-java/bin"),  # ant
]
PY4J_JAVA_PATH = os.pathsep.join(PY4J_JAVA_PATHS)

set_default_callback_accept_timeout(0.125)

def stderr_is_polluted(line):
    """May occur depending on the environment in which py4j is executed.
    The stderr ccanot be relied on when it occurs.
    """
    return "Picked up _JAVA_OPTIONS" in line


def sleep(sleep_time=0.250):
    """Default sleep time to enable the OS to reuse address and port.
    """
    time.sleep(sleep_time)


def start_echo_server():
    subprocess.call(["java", "-cp", PY4J_JAVA_PATH, "py4j.EchoServer"])


def start_echo_server_process():
    # XXX DO NOT FORGET TO KILL THE PROCESS IF THE TEST DOES NOT SUCCEED
    sleep()
    p = Process(target=start_echo_server)
    p.start()
    sleep(1.5)
    return p


def start_example_server():
    subprocess.call([
        "java", "-Xmx512m", "-cp", PY4J_JAVA_PATH,
        "py4j.examples.ExampleApplication"])


def start_short_timeout_example_server():
    subprocess.call([
        "java", "-Xmx512m", "-cp", PY4J_JAVA_PATH,
        "py4j.examples.ExampleApplication$ExampleShortTimeoutApplication"])


def start_ipv6_example_server():
    subprocess.call([
        "java", "-Xmx512m", "-cp", PY4J_JAVA_PATH,
        "py4j.examples.ExampleApplication$ExampleIPv6Application"])


def start_example_app_process():
    # XXX DO NOT FORGET TO KILL THE PROCESS IF THE TEST DOES NOT SUCCEED
    p = Process(target=start_example_server)
    p.start()
    sleep()
    check_connection()
    return p


def start_short_timeout_app_process():
    # XXX DO NOT FORGET TO KILL THE PROCESS IF THE TEST DOES NOT SUCCEED
    p = Process(target=start_short_timeout_example_server)
    p.start()
    sleep()
    check_connection()
    return p


def start_ipv6_app_process():
    # XXX DO NOT FORGET TO KILL THE PROCESS IF THE TEST DOES NOT SUCCEED
    p = Process(target=start_ipv6_example_server)
    p.start()
    # Sleep twice because we do not check connections.
    sleep()
    sleep()
    return p


def check_connection(gateway_parameters=None):
    test_gateway = JavaGateway(gateway_parameters=gateway_parameters)
    try:
        # Call a dummy method just to make sure we can connect to the JVM
        test_gateway.jvm.System.currentTimeMillis()
    except Py4JNetworkError:
        # We could not connect. Let"s wait a long time.
        # If it fails after that, there is a bug with our code!
        sleep(2)
    finally:
        test_gateway.close()


def get_socket():
    testSocket = socket(AF_INET, SOCK_STREAM)
    testSocket.connect(("127.0.0.1", TEST_PORT))
    return testSocket


def safe_shutdown(instance):
    if hasattr(instance, 'gateway'):
        try:
            instance.gateway.shutdown()
        except Exception:
            print_exc()


@contextmanager
def gateway(*args, **kwargs):
    g = JavaGateway(
        gateway_parameters=GatewayParameters(
            *args, auto_convert=True, **kwargs))
    time = g.jvm.System.currentTimeMillis()
    try:
        yield g
        # Call a dummy method to make sure we haven't corrupted the streams
        assert time <= g.jvm.System.currentTimeMillis()
    finally:
        g.shutdown()


@contextmanager
def example_app_process():
    p = start_example_app_process()
    try:
        yield p
    finally:
        p.join()