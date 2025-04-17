from frontend.main import PipimFrontend
from backend.main  import PipimBackend
from threading import Thread
import time
import os


def run_backend():
    backend = PipimBackend()
    backend.run(debug=True, use_reloader = False) 

def run_frontend():
    frontend = PipimFrontend()
    frontend.mainloop()

    os._exit(0)

if __name__ == "__main__":
    backend_thread = Thread(target=run_backend)
    backend_thread.start()

    time.sleep(3)

    frontend_thread = Thread(target=run_frontend)
    frontend_thread.start()

    backend_thread.join()
    frontend_thread.join()
    
    