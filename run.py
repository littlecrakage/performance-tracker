import sys
import os
import glob

# Add backend directory to Python path
backend_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'backend')
sys.path.insert(0, backend_dir)

from app import create_app
import socket

# Allow reuse of port even if previous process left sockets in TIME_WAIT
socket.socket(socket.AF_INET, socket.SOCK_STREAM).setsockopt(
    socket.SOL_SOCKET, socket.SO_REUSEADDR, 1
)

app = create_app()

if __name__ == '__main__':
    from werkzeug.serving import run_simple
    extra = glob.glob(os.path.join(backend_dir, 'templates', '*.html'))
    extra += glob.glob(os.path.join(backend_dir, 'static', '**', '*'), recursive=True)
    run_simple('0.0.0.0', 1337, app, use_reloader=True, use_debugger=True,
               extra_files=extra)
