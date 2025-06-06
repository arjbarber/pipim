from frontend.main import PipimFrontend as PipimFrontend
from backend.main  import PipimBackend as PipimBackend
from threading import Thread
import time
import os
import sys

 
def run_backend():
    backend = PipimBackend()
    backend.run(debug=True, use_reloader = False) 

def run_frontend():
    frontend = PipimFrontend()
    frontend.mainloop()

    os._exit(0)

if __name__ == "__main__":
    if sys.argv[1] == "-b":
        run_backend()
    elif sys.argv[1] == "-f":
        run_frontend()
    else:
        backend_thread = Thread(target=run_backend)
        backend_thread.start()

        time.sleep(0.2)

        run_frontend()

        backend_thread.join()

