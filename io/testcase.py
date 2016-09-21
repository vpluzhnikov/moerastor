# -*- coding: utf-8 -*-
#!/usr/bin/python

# from store import Store
# import logging
# #
# logger = logging.getLogger(__name__)
# LOG_FILE = 'test.log'
#
# logging.basicConfig(filename=LOG_FILE, level=logging.DEBUG, format='%(asctime)s %(message)s',
#                     datefmt='%m/%d/%Y %I:%M:%S %p')
# #
# # k = Store("./testfile")
# k.write_loop()
#

#!/usr/bin/env python
#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2015 uralbash <root@uralbash.ru>
#
# Distributed under terms of the MIT license.

"""
Unix socket client
"""
import os
import socket
import json

SOCKET_FILE = '/tmp/storedevserver.socket'

print("Подключение...")
if os.path.exists(SOCKET_FILE):
    client = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    client.connect(SOCKET_FILE)
    print("Выполнено.")
    print("Ctrl-C что бы выйти.")
    print("Отправьте 'DONE' что бы выключить сервер.")
    while True:
        try:
            x = raw_input("> ")  # for py2 use raw_input
            if "" != x:
                xs = json.dumps({'type':'command', 'desc' : x})
                print("ОТПРАВЛЕНО: %s" % xs)
                client.send(xs.encode('utf-8'))
                data=client.recv(1024)
                if data:
                    print data
                if "shutdown" == x:
                    print("Выключение.")
                    break
        except KeyboardInterrupt as k:
            print("Выключение.")
            break
    client.close()
else:
    print("Не могу соединиться!")
print("Выполнено")