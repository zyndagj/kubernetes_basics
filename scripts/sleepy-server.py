#!/usr/bin/env python
#
###############################################################################
# Author: Greg Zynda
# Last Modified: 07/30/2020
###############################################################################
# BSD 3-Clause License
#
# Copyright (c) 2020, Texas Advanced Computing Center
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# * Redistributions of source code must retain the above copyright notice, this
#   list of conditions and the following disclaimer.
#
# * Redistributions in binary form must reproduce the above copyright notice,
#   this list of conditions and the following disclaimer in the documentation
#   and/or other materials provided with the distribution.
#
# * Neither the name of the copyright holder nor the names of its
#   contributors may be used to endorse or promote products derived from
#   this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
###############################################################################


# Inspired by https://stackoverflow.com/a/30516693
from http.server import BaseHTTPRequestHandler, HTTPServer
import socketserver
import argparse, sys, os
from time import sleep
import logging

FORMAT = "[%(levelname)s - %(funcName)10s] %(message)s"
logging.basicConfig(level=logging.INFO, format=FORMAT)
logger = logging.getLogger(__name__)

hostname = os.uname()[1]

def main():
	parser = argparse.ArgumentParser(description='Simple webserver the sleeps')
	parser.add_argument('-p', metavar='INT', type=int, help='Port to serve on [%(default)s]', default=8080)
	parser.add_argument('-s', metavar='INT', type=float, help='Number of seconds to sleep', default=0.5)
	parser.add_argument('-m', metavar='STR', type=str, help='Message [%(default)s]', default='Hello World!')
	args = parser.parse_args()
	# Run Server
	start_server(args.s, args.m, args.p)

def start_server(sleep_time, message, port):
	def shandler(*args):
		SleepyHandler(sleep_time, message, *args)
	server = HTTPServer(('', port), shandler)
	logger.info("Webpage will sleep for %.2f seconds and then print '%s'"%(sleep_time, message))
	logger.info("Starting server at http://localhost:%i use Ctrl+C to stop"%(port))
	try:
		server.serve_forever()
	except KeyboardInterrupt:
		logger.info("Keyboard interrupt received, exiting")
		sys.exit()

class SleepyHandler(BaseHTTPRequestHandler):
	def __init__(self, sleep_time, message, *args):
		self.sleep_time = sleep_time
		self.message = message
		super().__init__(*args)
	def do_HEAD(self):
		self.send_response(200)
		self.send_header("Content-type", "text/html")
		self.end_headers()
	def do_GET(self):
		global hostname
		x = self.wfile.write
		self.do_HEAD()
		if self.path != '/': return
		# <--- HTML starts here --->
		x(b"<html>")
		# <--- HEAD starts here --->
		x(b"<head><title>Sleepy server</title></head>")
		# <--- HEAD ends here --->
		# <--- BODY starts here --->
		x(b"<body>")
		x(str.encode("<p>%s - Getting a little sleepy...</p>"%(hostname)))
		sleep(self.sleep_time)
		x(str.encode("<p>%s</p>"%(self.message)))
		x(b"</body>")
		# <--- BODY ends here --->
		x(b"</html>")
		# <--- HTML ends here --->

if __name__ == "__main__":
	main()
