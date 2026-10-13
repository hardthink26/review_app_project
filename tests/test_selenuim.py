from multiprocessing import Process 
from time import sleep 
import unittest
from urllib.request import urlopen 
from urllib.error import URLError

from selenium import webdriver
from selenium.webdriver.common.by import By 
from app import create_app

def run_server():
    app = create_app('development')
    app.run(host='127.0.0.1', port=5000, use_reloader=False)


class SeleniumTestCase(unittest.TestCase): 
    @classmethod
    def setUpClass(cls): 
        cls.server = Process(target=run_server) 
        cls.server.start() 

    def setUp(self): 
        for _ in range(50):
            try: 
                with urlopen('http://127.0.0.1:5000', timeout=1):
                    print('서버가 준비되었습니다.')
                    break
            except URLError:
                sleep(0.2)
        else: 
            raise RuntimeError('No running server')
        self.driver = webdriver.Chrome()

    def test_home_page(self): 
        self.driver.get('http://127.0.0.1:5000/')
        self.driver.implicitly_wait(0.5)
        title = self.driver.title 
        heading = self.driver.find_element(By.TAG_NAME, 'h1')
        self.assertTrue('리뷰 앱' in title)
        self.assertTrue( 'Stranger!' in heading.text )
        print('테스트 성공: 제목과 Stranger! 문구를 확인했습니다.') 

    @classmethod
    def tearDownClass(cls): 
        cls.server.terminate()
        cls.server.join() 

    def tearDown(self): 
        if self.driver is not None: 
            self.driver.quit() 

        

        

        
        
