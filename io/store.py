import time
import os
from logging import getLogger
import threading

DEFAULT_READ_TIMEOUT = 1
DEFAULT_WRITE_TIMEOUT = 5
DEFAULT_CHECK_BLOCK = 4096

logger = getLogger(__name__)

class Store():

    def __init__(self, devname, read_timeout=DEFAULT_READ_TIMEOUT, write_timeout=DEFAULT_WRITE_TIMEOUT):
        self.devname = devname
        self.read_timeout = DEFAULT_READ_TIMEOUT
        self.write_timeout = DEFAULT_WRITE_TIMEOUT
        self.read_latency = -1
        self.write_latency = -1
        if read_timeout:
            self.read_timeout = read_timeout
        if write_timeout:
            self.write_timeout = write_timeout
        self.last_check = -1
        self.health = self.is_healthy()

    def is_healthy(self):
        if (self.last_check):
            if ((time.time() - self.last_check) > self.read_timeout):
                return "Suspected"
            else:
                return "Healthy"
        else:
            return "Degaded"

    def _check_read_latency(self):
        try:
            with open(self.devname, "r+b") as f:
                start_time = time.time()
                f.seek(0)
                f.read(4096)
                f.close
                end_time = time.time()
                self.read_latency = end_time - start_time
            self.last_check = time.time()
        except:
            print "I/O Error while read checking"

    def _check_write_latency(self):
        try:
            with open(self.devname, "r+b") as f:
                start_time = time.time()
                f.seek(0)
                f.write(bytearray(os.urandom(4096)))
                f.close
                end_time = time.time()
                self.write_latency = end_time - start_time
            self.last_check = time.time()
        except:
            print "I/O Error while write checking"


    def read_loop(self):
        while True:
            time.sleep(self.read_timeout)
            self._check_read_latency()
            logger.info(self.is_healthy())
            logger.info("Read latency for dev %s = %s" % (self.devname, self.read_latency))


    def write_loop(self):
        while True:
            time.sleep(self.write_timeout)
            self._check_write_latency()
            logger.info(self.is_healthy())
            logger.info("Write latency for dev %s = %s" % (self.devname, self.write_latency))

    def serve_dev(self):
        try:
            logger.error("1")
            t = threading.Thread(target=self.read_loop())
            t.daemon = True
            t.start()
            time.sleep(0.5)
            logger.error("2")
        except Exception, e:
            logger.error(e)