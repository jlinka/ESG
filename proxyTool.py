# -*- coding: utf-8 -*-
"""
Created on Tue Oct 17 13:52:56 2017

@author: jlinka
"""

import socks
import socket
#需要crt的配置支持
socks.setdefaultproxy(socks.PROXY_TYPE_SOCKS5, "127.0.0.1", 7080)
socket.socket = socks.socksocket
