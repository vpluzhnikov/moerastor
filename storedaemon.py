#!/usr/bin/env python

import sys, time
from common.daemon import Daemon
from io.store import Store
import logging
import threading

logger = logging.getLogger(__name__)
LOG_FILE = 'logs/storedaemon.log'
PID_FILE = '/tmp/mstore-daemon.pid'

def readthread(devname):
    k = Store(devname)
    k.read_loop()

def writethread(devname):
    k = Store(devname)
    k.write_loop()

class MyDaemon(Daemon):

    def run(self):
        try:
            thread_read = threading.Thread(name='read-thread', target=readthread,
                                           args=(self.config, ))
            thread_write = threading.Thread(name='write-thread', target=writethread,
                                            args=(self.config, ))
            thread_read.start()
            thread_write.start()
        except Exception, e:
            logger.error(e)

if __name__ == "__main__":

    logging.basicConfig(filename=LOG_FILE, level=logging.DEBUG, format='%(asctime)s %(message)s',
                        datefmt='%m/%d/%Y %I:%M:%S %p')

    daemon = MyDaemon(PID_FILE,config="/Users/vsevolodpluzhnikov/PycharmProjects/moerastor/io/testfile")
    if len(sys.argv) == 2:
        if 'start' == sys.argv[1]:
            daemon.start()
        elif 'stop' == sys.argv[1]:
            daemon.stop()
        elif 'restart' == sys.argv[1]:
            daemon.restart()
        else:
            print "Unknown command"
            sys.exit(2)
        sys.exit(0)
    else:
        print "usage: %s start|stop|restart" % sys.argv[0]
        sys.exit(2)