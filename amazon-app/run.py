import http.server
import socketserver
import os
import sys

PORT = 8080
DIR = os.path.dirname(os.path.abspath(__file__))

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIR, **kwargs)

    def log_message(self, format, *args):
        print(f"[{self.log_date_time_string()}] {args[0]} {args[1]} {args[2]}")

print(f"Smart Warehouse App")
print(f"==================")
print(f"Serving at: http://localhost:{PORT}")
print(f"Open your browser and navigate to the URL above.")
print(f"Press Ctrl+C to stop the server.")
print()

with socketserver.TCPServer(("", PORT), Handler) as httpd:
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped.")
        sys.exit(0)
