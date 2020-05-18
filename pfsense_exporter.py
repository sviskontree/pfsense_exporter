#!/usr/local/bin/python3.7
import argparse
import ipaddress
from urllib.parse import urlparse
from http.server import BaseHTTPRequestHandler, HTTPServer
from socketserver import ThreadingMixIn
from pfsense_collector import collect

class ExporterHandler(BaseHTTPRequestHandler):
	def do_GET(self):
		url = urlparse(self.path)
		if url.path == '/metrics':
			#call collect
			output = bytes(collect(), encoding="utf-8")
			self.send_response(200)
			self.send_header('Content-Type', 'text/plain; version=0.0.4; charset=utf-8')
			self.end_headers()
			self.wfile.write(output)
		elif url.path == '/':
			self.send_response(200)
			self.end_headers()
			self.wfile.write(bytes("""<html>
			<head><title>Pfsense exporter</title></head>
			<body>
			<h1>Pfsense exporter</h1>
			<p>Visit <a href=\"/metrics\">Metrics</a></p>
			</body>
			</html>""", "utf-8")) 
		else:
			self.send_response(404)
			self.end_headers()

class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
	"""Handle requests in a separate thread."""

def check_valid_port(value):
	port = int(value)
	if not 1024<= port <= 65535:
		raise argparse.ArgumentTypeError("Invalid port number")
	return port

def check_valid_ip(value):
	ip = str(value)
	try:
		return str(ipaddress.ip_address(ip))
	except ValueError:
		raise argparse.ArgumentTypeError("Invalid ip")

if __name__ == '__main__':
	parser = argparse.ArgumentParser()
	parser.add_argument("-p", "--port", help="Port to listen to, defaults to 9988", type=check_valid_port, default=9988)
	parser.add_argument("-i", "--ip", help="IP to listen to, defaults to 0.0.0.0", type=check_valid_ip, default="0.0.0.0")
	args = parser.parse_args()
	server = ThreadedHTTPServer((args.ip, args.port), ExporterHandler)
	print("Starting server")
	server.serve_forever()
