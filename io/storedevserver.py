import os
import socket
import logging
import json
import threading
from store import Store

logger = logging.getLogger(__name__)

def readthread(dev):
    dev.read_loop()

def writethread(dev):
    dev.write_loop()

class StoreDevServer():
    def __init__(self, mondev, socketfile="/tmp/storedevserver.socket"):
        self.socketfile = socketfile
        if os.path.exists(self.socketfile):
            os.remove(self.socketfile)
        logger.info("Opening UNIX socket...")
        try:
            self.server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            self.server.bind(socketfile)
            self.server.listen(1)
            logger.info("Listing on socket %s" % self.socketfile)
        except Exception, e:
            logger.error("Error opnening socket with exception %s" % e)
        self.mondev = Store(mondev)

    def run(self):
        thread_read = threading.Thread(name='read-thread', target=self.mondev.read_loop,
                                       args=())
        thread_write = threading.Thread(name='write-thread', target=self.mondev.write_loop,
                                        args=())
        thread_read.daemon = True
        thread_write.daemon = True
        thread_read.start()
        thread_write.start()
        while True:
            conn, addr = self.server.accept()
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
                            logger.info(json.dumps({'state': self.mondev.is_healthy(),
                                                    'read_latency': self.mondev.read_latency,
                                                    'write_latency': self.mondev.write_latency}))
                            conn.send(json.dumps({'state': self.mondev.is_healthy(),
                                                  'read_latency': self.mondev.read_latency,
                                                  'write_latency': self.mondev.write_latency}).encode('utf-8'))
                        else:
                            conn.send("Unknown command recieved on socket".encode('utf-8'))
                            logger.info("Unknown command recieved on socket")
                except Exception, e:
                    logger.error(e)
        logger.info("Stopping service on socket %s" % self.socketfile)
        self.server.close()
        os.remove(self.socketfile)
