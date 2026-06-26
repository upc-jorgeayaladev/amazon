import http.server
import socketserver
import os
import sys

PORT = 8080
DIR = os.path.dirname(os.path.abspath(__file__))
MAX_PORT_ATTEMPTS = 10

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIR, **kwargs)

    def log_message(self, format, *args):
        print(f"[{self.log_date_time_string()}] {args[0]} {args[1]} {args[2]}")


class ReusableThreadingTCPServer(socketserver.ThreadingTCPServer):
    allow_reuse_address = True
    daemon_threads = True


def create_server():
    last_error = None

    for port in range(PORT, PORT + MAX_PORT_ATTEMPTS):
        try:
            return ReusableThreadingTCPServer(("localhost", port), Handler), port
        except OSError as error:
            last_error = error
            if getattr(error, "winerror", None) not in {10013, 10048}:
                raise

    raise last_error


try:
    httpd, active_port = create_server()
except OSError as error:
    print(f"No se pudo iniciar el servidor: {error}")
    sys.exit(1)

print("Nexus Warehouse")
print("================")
print(f"Servidor disponible en: http://localhost:{active_port}")
if active_port != PORT:
    print(f"El puerto {PORT} estaba ocupado; se utilizó el puerto {active_port}.")
print("Presiona Ctrl+C para detener el servidor.")
print()

with httpd:
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nServidor detenido.")
        sys.exit(0)
