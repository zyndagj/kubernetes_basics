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


def main():
	parser = argparse.ArgumentParser(description='Simple webserver that reads a file and appends "hello world"')
	parser.add_argument('-p', metavar='INT', type=int, help='Port to serve on [%(default)s]', default=8080)
	parser.add_argument('-f', metavar='FILE', type=str, help='File read and update [%(default)s]', default='./serve')
	parser.add_argument('--clean', action='store_true', help='Start from fresh file')
	args = parser.parse_args()
	if args.clean and os.path.exists(args.f):
		os.remove(args.f)
	# Run Server
	start_server(args.f, args.p)

def start_server(ufile, port):
	def uhandler(*args):
		UpdateHandler(ufile, *args)
	server = HTTPServer(('', port), uhandler)
	logger.info("Webpage will update text ever time it is queried")
	logger.info("Starting server at http://localhost:%i use Ctrl+C to stop"%(port))
	try:
		server.serve_forever()
	except KeyboardInterrupt:
		logger.info("Keyboard interrupt received, exiting")
		sys.exit()

counter = 0
hostname = os.uname()[1]

class UpdateHandler(BaseHTTPRequestHandler):
	def __init__(self, ufile, *args):
		self.file = ufile
		super().__init__(*args)
	def do_HEAD(self):
		self.send_response(200)
		self.send_header("Content-type", "text/html")
		self.end_headers()
	def append_get(self):
		global counter, hostname
		with open(self.file, 'a+') as IF:
			counter += 1
			IF.write("%s - %i - Hello World!\n"%(hostname,counter))
			IF.seek(0)
			return [l.rstrip('\n') for l in IF.readlines()]
	def do_GET(self):
		x = self.wfile.write
		self.do_HEAD()
		if self.path != '/': return
		# <--- HTML starts here --->
		x(b"<html>")
		# <--- HEAD starts here --->
		x(b"<head><title>Update server</title></head>")
		# <--- HEAD ends here --->
		# <--- BODY starts here --->
		x(b"<body><p>")
		x(str.encode('</p>\n<p>'.join(self.append_get())))
		x(b"</p></body>")
		# <--- BODY ends here --->
		x(b"</html>")
		# <--- HTML ends here --->

if __name__ == "__main__":
	main()
