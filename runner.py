import os
import sys
import time
import signal
import socket
from threading import Thread
import multiprocessing

def port_in_use(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0

def run_backend():
    from backend.main import PipimBackend
    if port_in_use(5050):
        print("Port 5050 already in use. Skipping backend start.")
        sys.exit(0)
    backend = PipimBackend()
    backend.run(debug=False, use_reloader=False)

def run_frontend():
    from frontend.main import PipimFrontend
    frontend = PipimFrontend()
    frontend.mainloop()

    # Kill the current process (ensures backend dies too)
    os.kill(os.getpid(), signal.SIGTERM)

if __name__ == "__main__":
    multiprocessing.freeze_support()  # ✅ REQUIRED for PyInstaller on Windows

    if len(sys.argv) > 1 and sys.argv[1] in ["-b", "-f"]:
        if sys.argv[1] == "-b":
            run_backend()
        elif sys.argv[1] == "-f":
            run_frontend()
    else:
        backend_thread = Thread(target=run_backend, daemon=True)
        backend_thread.start()

        time.sleep(0.2)

        run_frontend()

        backend_thread.join()
