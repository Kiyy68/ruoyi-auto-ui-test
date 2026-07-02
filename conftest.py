# -*- coding: utf-8 -*-
"""pytest fixtures - 浏览器初始化、登录、页面对象"""
import time
import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

from config import IMPLICIT_WAIT, USERNAME, PASSWORD, CASE_URL
from pages.login_page import LoginPage
from pages.case_list_page import CaseListPage
from pages.case_detail_page import CaseDetailPage


@pytest.fixture(scope="session")
def browser():
    """初始化 Chrome 浏览器，整个测试会话共享"""
    options = ChromeOptions()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    # 如需无头模式取消下行注释
    # options.add_argument("--headless=new")

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    driver.implicitly_wait(IMPLICIT_WAIT)
    driver.maximize_window()

    yield driver
    driver.quit()


@pytest.fixture(scope="session")
def login(browser):
    """通过页面登录（验证码已在数据库中关闭）"""
    page = LoginPage(browser)
    page.open()
    page.login(USERNAME, PASSWORD)
    assert page.is_logged_in(), "登录失败，请检查验证码是否已关闭"
    return browser


@pytest.fixture(autouse=True)
def _ensure_clean_state(login):
    """每个测试前确保处于列表页干净状态（无弹窗、无搜索条件）"""
    driver = login
    # 如果当前不在列表页，先导航回去
    if "/test/functional/case" not in driver.current_url or "detail" in driver.current_url:
        driver.get(CASE_URL)
    # 关闭可能残留的对话框
    try:
        from selenium.webdriver.common.by import By
        dialogs = driver.find_elements(By.CSS_SELECTOR, '.el-dialog__wrapper[style*="display: none"]')
        close_btns = driver.find_elements(By.CSS_SELECTOR, '.el-dialog__headerbtn')
        for btn in close_btns:
            if btn.is_displayed():
                btn.click()
                time.sleep(0.2)
    except:
        pass
    # 关闭可能残留的消息提示
    try:
        from selenium.webdriver.common.by import By
        msgs = driver.find_elements(By.CSS_SELECTOR, '.el-message .el-icon-close')
        for m in msgs:
            try:
                m.click()
            except:
                pass
    except:
        pass
    yield
    # 测试结束后不做额外操作，每个测试自己负责清理


@pytest.fixture
def case_page(login):
    """打开测试用例列表页"""
    page = CaseListPage(login)
    page.open()
    return page


@pytest.fixture
def detail_page(login):
    """测试用例详情页"""
    return CaseDetailPage(login)
