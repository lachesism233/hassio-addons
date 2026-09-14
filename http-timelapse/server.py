#!/usr/bin/env python3
import os
import sys
from http.server import HTTPServer, SimpleHTTPRequestHandler

PORT = 8099


def main():
    directory = sys.argv[1] if len(sys.argv) > 1 else "/share/timelapse"
    os.makedirs(directory, exist_ok=True)
    os.chdir(directory)

    server = HTTPServer(("", PORT), SimpleHTTPRequestHandler)
    print(f"Serving {directory} on port {PORT}", flush=True)
    server.serve_forever()


if __name__ == "__main__":
    main()
