#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2015 uralbash <root@uralbash.ru>
#
# Distributed under terms of the MIT license.

"""
Unix socket server
"""
import os
import socket
import logging
import json
import threading
from store import Store

SOCKET_FILE = '/tmp/storedevserver.socket'
LOG_FILE = 'test.log'

logger = logging.getLogger(__name__)
logging.basicConfig(filename=LOG_FILE, level=logging.DEBUG, format='%(asctime)s %(message)s',
                    datefmt='%m/%d/%Y %I:%M:%S %p')


def readthread(dev):
    dev.read_loop()

def writethread(dev):
    dev.write_loop()


if os.path.exists(SOCKET_FILE):
    os.remove(SOCKET_FILE)

logger.info("Opening UNIX socket...")
try:
    server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    server.bind(SOCKET_FILE)
    server.listen(1)
except Exception, e:
    logger.error("Error opnening socket with exception %s" % e)

logger.info("Listing on socket %s" % SOCKET_FILE)
dev = Store("/Users/vsevolodpluzhnikov/PycharmProjects/moerastor/io/testfile")
thread_read = threading.Thread(name='read-thread', target=readthread,
                               args=(dev,))
thread_write = threading.Thread(name='write-thread', target=writethread,
                                args=(dev,))
thread_read.daemon = True
thread_write.daemon = True
thread_read.start()
thread_write.start()
while True:
    conn, addr = server.accept()
    datagram = conn.recv(1024)
    if not datagram:
        break
    else:
        try:
            dic = json.loads(datagram)
            logger.debug("Recived datagram %s" % dic)
            if dic['type'] == 'command':
                if dic['desc'] == 'shutdown':
                    logger.info("Shutdown command recieved on socket")
                    break
                elif dic['desc'] == 'getstat':
                    logger.info("Current stats reqested on socket")
                    logger.info(json.dumps({'state': dev.is_healthy(),
                                            'read_latency': dev.read_latency, 'write_latency': dev.write_latency}))
                    # conn.send("test".encode('utf-8'))
                    conn.send(json.dumps({'state': dev.is_healthy(), 'read_latency': dev.read_latency,
                                              'write_latency': dev.write_latency}).encode('utf-8'))
                else:
                    conn.send("Unknown command recieved on socket".encode('utf-8'))
                    logger.info("Unknown command recieved on socket")
        except Exception, e:
            logger.error(e)
logger.info("Stopping service on socket %s" % SOCKET_FILE)
server.close()
os.remove(SOCKET_FILE)