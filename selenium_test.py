from multiprocessing import Process 
from time import sleep 
from urllib.request import urlopen
from urllib.error import URLError

from selenium import webdriver
from app import create_app

def run_server():
    app = create_app('development')
    app.run(host='127.0.0.1', port=5000, use_reloader=False)


if __name__ == '__main__':
    server = Process(target=run_server)
    server.start()
    driver = None 

    try: 
        for _ in range(50):
            try: 
                with urlopen('http://127.0.0.1:5000',timeout=1):
                    break
            except URLError: 
                sleep(0.2) 

        else: 
            raise RuntimeError('No running server')
        driver = webdriver.Chrome()
        driver.get('http://127.0.0.1:5000')
    finally: 
        try:
            if driver is not None: 
                driver.quit()
        finally:
            server.terminate()
            server.join()


        
        
    