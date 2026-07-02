# -*- coding: utf-8 -*-
"""测试用例详情页 Page Object"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from config import BASE_URL, EXPLICIT_WAIT


class CaseDetailPage:
    """测试管理 > 功能测试 > 测试用例 > 详情页"""

    # 定位器（el-descriptions 渲染为 table，用 td.el-descriptions-item__content 按索引取值）
    # 布局：[用例名称, 优先级] [用例类型, 状态] [前置条件] [预期结果] [实际结果]
    # 索引：   0           1        2          3       4          5         6
    ALL_CONTENT_CELLS = (By.CSS_SELECTOR, 'td.el-descriptions-item__content')
    BTN_BACK = (By.CSS_SELECTOR, 'button.el-button--default.el-button--mini')
    STEP_ROWS = (By.CSS_SELECTOR, '.el-table__body-wrapper .el-table__row')
    DETAIL_CARD = (By.CSS_SELECTOR, '.el-card')

    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, EXPLICIT_WAIT)

    def open(self, case_id):
        """通过用例 ID 打开详情页"""
        self.driver.get(f"{BASE_URL}/test/functional/case/detail/{case_id}")
        self.wait.until(EC.presence_of_element_located(self.DETAIL_CARD))
        return self

    def _get_content_cells(self):
        """获取所有描述内容单元格"""
        return self.driver.find_elements(*self.ALL_CONTENT_CELLS)

    def get_case_name(self):
        """获取用例名称（索引0）"""
        cells = self._get_content_cells()
        return cells[0].text if len(cells) > 0 else ""

    def get_level(self):
        """获取优先级（索引1）"""
        cells = self._get_content_cells()
        return cells[1].text if len(cells) > 1 else ""

    def get_case_type(self):
        """获取用例类型（索引2）"""
        cells = self._get_content_cells()
        return cells[2].text if len(cells) > 2 else ""

    def get_status(self):
        """获取状态（索引3）"""
        cells = self._get_content_cells()
        return cells[3].text if len(cells) > 3 else ""

    def get_precondition(self):
        """获取前置条件（索引4）"""
        cells = self._get_content_cells()
        return cells[4].text if len(cells) > 4 else ""

    def get_expected(self):
        """获取预期结果（索引5）"""
        cells = self._get_content_cells()
        return cells[5].text if len(cells) > 5 else ""

    def get_actual_result(self):
        """获取实际结果（索引6）"""
        cells = self._get_content_cells()
        return cells[6].text if len(cells) > 6 else ""

    def get_step_list(self):
        """获取测试步骤列表，返回 list[dict]"""
        rows = self.driver.find_elements(*self.STEP_ROWS)
        steps = []
        for row in rows:
            cells = row.find_elements(By.CSS_SELECTOR, '.cell')
            if len(cells) >= 4:
                steps.append({
                    "step": cells[0].text.strip(),
                    "stepDesc": cells[1].text.strip(),
                    "expected": cells[2].text.strip(),
                    "actualResult": cells[3].text.strip(),
                })
        return steps

    def click_back(self):
        """点击返回按钮"""
        self.driver.find_element(*self.BTN_BACK).click()
        return self

    def is_loaded(self):
        """详情页是否已加载"""
        try:
            return self.driver.find_element(*self.DETAIL_CARD).is_displayed()
        except:
            return False


if __name__ == "__main__":
    """独立运行：新增用例 → 打开详情页 → 验证字段 → 清理"""
    import time
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.chrome.service import Service
    from webdriver_manager.chrome import ChromeDriverManager
    from config import USERNAME, PASSWORD
    from pages.login_page import LoginPage
    from pages.case_list_page import CaseListPage

    options = Options()
    options.add_argument("--no-sandbox")
    options.add_argument("--window-size=1920,1080")
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    driver.implicitly_wait(10)

    test_name = f"DetailTest_{int(time.time() * 1000)}"

    try:
        # 登录
        LoginPage(driver).open().login(USERNAME, PASSWORD)
        print("[OK] 登录成功")

        # 先新增一个用例（详情页需要有数据）
        list_page = CaseListPage(driver)
        list_page.open()
        list_page.click_add()
        list_page.fill_case_form({
            "caseName": test_name,
            "level": "P0",
            "caseType": "功能测试",
            "expected": "详情页验证",
        })
        list_page.submit_form()
        list_page.get_success_message()
        print(f"[OK] 测试用例已创建：{test_name}")

        # 打开详情页
        detail = CaseDetailPage(driver)
        # 从列表点击详情进入
        list_page.click_detail_by_name(test_name)
        time.sleep(1)

        # 验证详情页
        assert detail.is_loaded(), "详情页未加载"
        print(f"[OK] 用例名称：{detail.get_case_name()}")
        print(f"[OK] 优先级：{detail.get_level()}")
        print(f"[OK] 状态：{detail.get_status()}")

        # 返回列表页清理
        detail.click_back()
        time.sleep(0.5)
        list_page.open()
        list_page.search_by_name(test_name)
        list_page.click_delete_by_name(test_name)
        list_page.confirm_delete()

        print("[PASS] case_detail_page 测试通过")
    except Exception as e:
        print(f"[FAIL] {e}")
        try:
            list_page = CaseListPage(driver)
            list_page.open()
            list_page.search_by_name(test_name)
            if list_page.has_case(test_name):
                list_page.click_delete_by_name(test_name)
                list_page.confirm_delete()
        except:
            pass
    finally:
        driver.quit()
