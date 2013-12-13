
from global_test_case import LiveServerWriteItTestCase as TestCase
from selenium.webdriver.firefox.webdriver import WebDriver
from subdomains.utils import reverse
from selenium.webdriver.support.wait import WebDriverWait


class LoginWebTests(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.selenium = WebDriver()
        super(LoginWebTests, cls).setUpClass()

    @classmethod
    def tearDownClass(cls):
        cls.selenium.quit()
        super(LoginWebTests, cls).tearDownClass()

    def test_login(self):
        timeout = 2
        url = reverse('django.contrib.auth.views.login')
        self.selenium.get(url)
        username_input = self.selenium.find_element_by_name("username")
        username_input.send_keys('admin')
        password_input = self.selenium.find_element_by_name("password")
        password_input.send_keys('admin')
        self.selenium.find_element_by_xpath('//button[@type="submit"]').click()
        WebDriverWait(self.selenium, timeout).until(
        lambda driver: 
        driver.find_element_by_tag_name('body')

        )
        element = self.selenium.find_element_by_link_text("admin")
        self.assertTrue(element)