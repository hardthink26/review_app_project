from multiprocessing import Process 
from time import sleep 
import unittest
from urllib.request import urlopen 
from urllib.error import URLError

from selenium import webdriver
from selenium.webdriver.common.by import By 
from selenium.webdriver.support.wait import WebDriverWait
from app import create_app, db, fake 
from app.models import User, Role 


def run_server():
    app = create_app('testing')
    with app.app_context():
        db.create_all()
        Role.add_roles()

        admin = User(
            email = 'admin@example.com',
            username = 'testAdmin',
            password = 'cat',
            role = Role.query.filter_by(name='Admin').first(),
            confirmed=True,
        )
        db.session.add(admin)
        db.session.commit()
        fake.users(10)
        fake.posts(10)

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

    def test_admin_home_page(self): 
        # navigate to home page
        self.driver.get('http://127.0.0.1:5000/auth/login')
        register_text = self.driver.find_element(By.TAG_NAME, 'h1')
        self.assertTrue('Login' in register_text.text)
        print('테스트 성공: 로그인 화면 출력!')

        #logged in 
        self.driver.find_element(By.NAME, 'email').send_keys('admin@example.com')
        self.driver.find_element(By.NAME, 'password').send_keys('cat')
        self.driver.find_element(By.NAME, 'submit').click()

        WebDriverWait(self.driver, 10).until(lambda driver: '/auth/login' not in
                                             driver.current_url)
        title = self.driver.find_element(By.TAG_NAME, 'h1')
        self.assertTrue('testAdmin!' in title.text)
        print('테스트 성공: 관리자가 로그인에 성공하였습니다.')

        #navigate to the user's profile page 
        self.driver.find_element(By.LINK_TEXT, 'Profile').click()
        WebDriverWait(self.driver, 10).until(lambda driver: '/main/index' not in 
                                             driver.current_url)
        title = self.driver.find_element(By.TAG_NAME, 'a')
        self.assertTrue('Home' in title.text)
        print('테스트 성공: 관리자가 user_profile 페이지에 진입') 

    @classmethod
    def tearDownClass(cls): 
        cls.server.terminate()
        cls.server.join() 

    def tearDown(self): 
        if self.driver is not None: 
            self.driver.quit() 

    

        

        

        
        
