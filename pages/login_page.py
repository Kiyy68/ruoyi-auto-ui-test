# -*- coding: utf-8 -*-
"""登录页 Page Object"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from config import LOGIN_URL, EXPLICIT_WAIT


class LoginPage:
    """RuoYi 登录页"""

    # 定位器
    INPUT_USERNAME = (By.CSS_SELECTOR, 'input[placeholder="账号"]')
    INPUT_PASSWORD = (By.CSS_SELECTOR, 'input[placeholder="密码"]')
    BTN_LOGIN = (By.CSS_SELECTOR, 'button.el-button--primary')
    # 验证码关闭后不再有验证码输入框

    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, EXPLICIT_WAIT)

    def open(self):
        """打开登录页"""
        self.driver.get(LOGIN_URL)
        self.wait.until(EC.presence_of_element_located(self.INPUT_USERNAME))
        return self

    def login(self, username, password):
        """输入用户名密码并点击登录"""
        # 清空并输入用户名
        el_user = self.wait.until(EC.element_to_be_clickable(self.INPUT_USERNAME))
        el_user.clear()
        el_user.send_keys(username)

        # 清空并输入密码
        el_pwd = self.driver.find_element(*self.INPUT_PASSWORD)
        el_pwd.clear()
        el_pwd.send_keys(password)

        # 点击登录按钮
        btn = self.driver.find_element(*self.BTN_LOGIN)
        btn.click()

        # 等待登录成功（页面跳转离开 /login）
        self.wait.until(EC.url_changes(LOGIN_URL))
        return self

    def is_logged_in(self):
        """判断是否已登录（URL 不再是 /login）"""
        return "/login" not in self.driver.current_url


if __name__ == "__main__":
    """独立运行：验证登录页能否正常打开和登录"""
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.chrome.service import Service
    from webdriver_manager.chrome import ChromeDriverManager
    from config import USERNAME, PASSWORD

    options = Options()
    options.add_argument("--no-sandbox")
    options.add_argument("--window-size=1920,1080")
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    driver.implicitly_wait(10)

    try:
        page = LoginPage(driver)
        page.open()
        print("[OK] 登录页已打开")
        page.login(USERNAME, PASSWORD)
        print(f"[OK] 登录成功，当前URL：{driver.current_url}")
        assert page.is_logged_in(), "登录失败"
        print("[PASS] login_page 测试通过")
    except Exception as e:
        print(f"[FAIL] {e}")
    finally:
        driver.quit()
