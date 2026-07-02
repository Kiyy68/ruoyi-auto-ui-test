# -*- coding: utf-8 -*-
"""测试用例列表页 Page Object — 基于 Playwright 录制结果修正"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from config import CASE_URL, EXPLICIT_WAIT


class CaseListPage:
    """测试管理 > 功能测试 > 测试用例 列表页"""

    # ── 搜索表单定位器（来自 Playwright 录制 + SelectorsHub） ──
    INPUT_CASE_NAME = (By.CSS_SELECTOR, 'input[placeholder="请输入用例名称"]')
    BTN_SEARCH = (By.CSS_SELECTOR, 'button.el-button--primary.el-button--small')
    BTN_RESET = (By.CSS_SELECTOR, 'button.el-button--default.el-button--small')

    # ── 工具栏定位器 ──
    BTN_ADD = (By.CSS_SELECTOR, 'button.el-button--primary.el-button--medium.is-plain')
    BTN_BATCH_DELETE = (By.CSS_SELECTOR, 'button.el-button--danger.el-button--medium.is-plain')

    # ── 表格定位器 ──
    TABLE = (By.CSS_SELECTOR, '.el-table')
    TABLE_ROWS = (By.CSS_SELECTOR, '.el-table__body-wrapper .el-table__row')
    TABLE_HEADER = (By.CSS_SELECTOR, '.el-table__header-wrapper th .cell')

    # ── 对话框定位器 ──
    DIALOG_VISIBLE = (By.CSS_SELECTOR, '.el-dialog__wrapper:not([style*="display: none"])')
    INPUT_CASE_TITLE = (By.CSS_SELECTOR, 'input[placeholder="请输入用例标题"]')
    INPUT_PRECONDITION = (By.CSS_SELECTOR, 'textarea[placeholder="请输入前置条件"]')
    INPUT_EXPECTED = (By.CSS_SELECTOR, 'textarea[placeholder="请输入预期结果"]')
    INPUT_ACTUAL_RESULT = (By.CSS_SELECTOR, 'textarea[placeholder="请输入实际结果"]')
    BTN_SUBMIT = (By.CSS_SELECTOR, '.el-dialog__wrapper:not([style*="display: none"]) .el-dialog__footer button.el-button--primary')
    BTN_CANCEL = (By.CSS_SELECTOR, '.el-dialog__wrapper:not([style*="display: none"]) .el-dialog__footer button.el-button--default')

    # ── 步骤表格定位器（对话框内） ──
    STEP_ROWS = (By.CSS_SELECTOR, '.el-dialog .el-table__body-wrapper .el-table__row')
    STEP_INPUT_DESC = (By.CSS_SELECTOR, 'input[placeholder="输入操作描述"]')
    STEP_INPUT_EXPECTED = (By.CSS_SELECTOR, 'input[placeholder="输入预期结果"]')
    STEP_INPUT_ACTUAL = (By.CSS_SELECTOR, 'input[placeholder="输入实际结果"]')

    # ── 分页定位器 ──
    PAGINATION = (By.CSS_SELECTOR, '.el-pagination')

    # ── 消息提示定位器 ──
    SUCCESS_MSG = (By.CSS_SELECTOR, '.el-message--success')
    ERROR_MSG = (By.CSS_SELECTOR, '.el-message--error')

    # ── 确认弹窗定位器（Playwright: name="确定"，无空格） ──
    CONFIRM_BTN = (By.CSS_SELECTOR, '.el-message-box__btns .el-button--primary')

    # ── 下拉选项定位器（Playwright 用 listitem role） ──
    DROPDOWN_ITEM = (By.CSS_SELECTOR, '.el-select-dropdown__item')

    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, EXPLICIT_WAIT)

    def open(self):
        """打开测试用例列表页"""
        self.driver.get(CASE_URL)
        self.wait.until(EC.presence_of_element_located(self.TABLE))
        time.sleep(0.5)
        return self

    # ── 搜索操作 ──

    def search_by_name(self, name):
        """按用例名称搜索"""
        el = self.wait.until(EC.element_to_be_clickable(self.INPUT_CASE_NAME))
        el.clear()
        el.send_keys(name)
        self.driver.find_element(*self.BTN_SEARCH).click()
        time.sleep(0.5)
        return self

    def search_by_level(self, level):
        """按优先级搜索"""
        # Playwright: 点击 el-select__caret → 选 listitem
        carets = self.driver.find_elements(By.CSS_SELECTOR,
            '.el-form .el-select .el-input__suffix .el-select__caret')
        if carets:
            carets[0].click()
            time.sleep(0.5)
            self._select_dropdown_item(level)
        self.driver.find_element(*self.BTN_SEARCH).click()
        time.sleep(0.5)
        return self

    def search_by_status(self, status):
        """按状态搜索"""
        carets = self.driver.find_elements(By.CSS_SELECTOR,
            '.el-form .el-select .el-input__suffix .el-select__caret')
        if len(carets) >= 2:
            carets[1].click()
            time.sleep(0.5)
            self._select_dropdown_item(status)
        self.driver.find_element(*self.BTN_SEARCH).click()
        time.sleep(0.5)
        return self

    def reset_search(self):
        """重置搜索条件"""
        self.driver.find_element(*self.BTN_RESET).click()
        time.sleep(0.5)
        return self

    # ── 新增操作 ──

    def click_add(self):
        """点击新增按钮"""
        self.driver.find_element(*self.BTN_ADD).click()
        self.wait.until(EC.visibility_of_element_located(self.DIALOG_VISIBLE))
        time.sleep(0.5)
        return self

    def fill_case_form(self, data):
        """填写用例表单
        data: dict, keys: caseName, level, caseType, precondition, expected, actualResult
        """
        if "caseName" in data:
            el = self.driver.find_element(*self.INPUT_CASE_TITLE)
            el.clear()
            el.send_keys(data["caseName"])

        if "level" in data:
            # Playwright: 点击第一个 el-select__caret → 选 listitem
            self._select_form_dropdown(0, data["level"])

        if "caseType" in data:
            # Playwright: 点击第二个 el-select__caret → 选 listitem
            self._select_form_dropdown(1, data["caseType"])

        if "precondition" in data:
            el = self.driver.find_element(*self.INPUT_PRECONDITION)
            el.clear()
            el.send_keys(data["precondition"])

        if "expected" in data:
            el = self.driver.find_element(*self.INPUT_EXPECTED)
            el.clear()
            el.send_keys(data["expected"])

        if "actualResult" in data:
            el = self.driver.find_element(*self.INPUT_ACTUAL_RESULT)
            el.clear()
            el.send_keys(data["actualResult"])

        return self

    def _select_form_dropdown(self, index, text):
        """点击对话框内第 index 个下拉框的 caret 图标，再选择选项"""
        # Playwright 方式：找 el-select__caret 图标点击
        visible_dialogs = self.driver.find_elements(*self.DIALOG_VISIBLE)
        for dialog in visible_dialogs:
            carets = dialog.find_elements(By.CSS_SELECTOR,
                '.el-select .el-input__suffix .el-select__caret')
            if index < len(carets):
                carets[index].click()
                time.sleep(0.5)
                self._select_dropdown_item(text)
                break

    def _select_dropdown_item(self, text):
        """从已打开的下拉列表中选择指定文本的选项（Playwright: listitem role）"""
        items = self.driver.find_elements(*self.DROPDOWN_ITEM)
        for item in items:
            if text in item.text:
                item.click()
                break
        time.sleep(0.3)

    def add_step(self, step_desc, expected=""):
        """添加一条测试步骤"""
        self.driver.find_elements(By.CSS_SELECTOR,
            '.el-dialog button.el-button--primary.el-button--mini')
        time.sleep(0.3)
        desc_inputs = self.driver.find_elements(*self.STEP_INPUT_DESC)
        expect_inputs = self.driver.find_elements(*self.STEP_INPUT_EXPECTED)
        if desc_inputs:
            desc_inputs[-1].clear()
            desc_inputs[-1].send_keys(step_desc)
        if expect_inputs and expected:
            expect_inputs[-1].clear()
            expect_inputs[-1].send_keys(expected)
        return self

    def submit_form(self):
        """提交表单（Playwright: name="确 定"，中间有空格）"""
        self.driver.find_element(*self.BTN_SUBMIT).click()
        time.sleep(0.5)
        return self

    def cancel_form(self):
        """取消表单"""
        self.driver.find_element(*self.BTN_CANCEL).click()
        time.sleep(0.3)
        return self

    def is_dialog_open(self):
        """对话框是否打开"""
        try:
            return self.driver.find_element(*self.DIALOG_VISIBLE).is_displayed()
        except:
            return False

    def get_dialog_title(self):
        """获取当前可见对话框的标题"""
        visible_dialogs = self.driver.find_elements(*self.DIALOG_VISIBLE)
        for dialog in visible_dialogs:
            titles = dialog.find_elements(By.CSS_SELECTOR, '.el-dialog__title')
            for t in titles:
                if t.text.strip():
                    return t.text.strip()
        return ""

    # ── 表格操作 ──

    def get_table_data(self):
        """获取表格所有行数据（第1列是复选框，数据从第2列开始）"""
        rows = self.driver.find_elements(*self.TABLE_ROWS)
        data = []
        for row in rows:
            cells = row.find_elements(By.CSS_SELECTOR, '.cell')
            if len(cells) >= 7:
                data.append({
                    "caseName": cells[1].text.strip(),
                    "level": cells[2].text.strip(),
                    "caseType": cells[3].text.strip(),
                    "status": cells[4].text.strip(),
                    "createTime": cells[5].text.strip(),
                })
        return data

    def get_table_headers(self):
        """获取表头文本"""
        headers = self.driver.find_elements(*self.TABLE_HEADER)
        return [h.text.strip() for h in headers]

    def _find_row_by_name(self, name):
        """根据用例名称找到表格行（名称在第2列）"""
        rows = self.driver.find_elements(*self.TABLE_ROWS)
        for row in rows:
            cells = row.find_elements(By.CSS_SELECTOR, '.cell')
            if len(cells) >= 2 and name in cells[1].text:
                return row
        return None

    def click_edit_by_name(self, name):
        """按名称找到行并点击修改（操作列第2个按钮）"""
        row = self._find_row_by_name(name)
        if row:
            btns = row.find_elements(By.CSS_SELECTOR, 'button.el-button--text.el-button--mini')
            if len(btns) >= 2:
                btns[1].click()
                self.wait.until(EC.visibility_of_element_located(self.DIALOG_VISIBLE))
                time.sleep(0.3)
        return self

    def click_delete_by_name(self, name):
        """按名称找到行并点击删除（操作列第3个按钮）"""
        row = self._find_row_by_name(name)
        if row:
            btns = row.find_elements(By.CSS_SELECTOR, 'button.el-button--text.el-button--mini')
            if len(btns) >= 3:
                btns[2].click()
                time.sleep(0.3)
        return self

    def click_detail_by_name(self, name):
        """按名称找到行并点击详情（操作列第1个按钮）"""
        row = self._find_row_by_name(name)
        if row:
            btns = row.find_elements(By.CSS_SELECTOR, 'button.el-button--text.el-button--mini')
            if btns:
                btns[0].click()
                time.sleep(0.5)
        return self

    def select_row_by_name(self, name):
        """选中指定行的复选框"""
        row = self._find_row_by_name(name)
        if row:
            checkbox = row.find_element(By.CSS_SELECTOR, '.el-checkbox__input')
            checkbox.click()
            time.sleep(0.2)
        return self

    def click_batch_delete(self):
        """点击工具栏删除按钮（批量删除）"""
        self.driver.find_element(*self.BTN_BATCH_DELETE).click()
        time.sleep(0.3)
        return self

    def confirm_delete(self):
        """确认删除弹窗（Playwright: name="确定"，无空格）"""
        self.wait.until(EC.element_to_be_clickable(self.CONFIRM_BTN)).click()
        time.sleep(0.5)
        return self

    # ── 消息获取 ──

    def get_success_message(self):
        """获取成功提示消息"""
        try:
            el = self.wait.until(EC.visibility_of_element_located(self.SUCCESS_MSG))
            return el.text
        except:
            return ""

    def get_error_message(self):
        """获取错误提示消息"""
        try:
            el = self.wait.until(EC.visibility_of_element_located(self.ERROR_MSG))
            return el.text
        except:
            return ""

    def has_case(self, name):
        """表格中是否存在指定名称的用例"""
        return self._find_row_by_name(name) is not None

    def get_case_count(self):
        """获取当前页表格行数"""
        return len(self.driver.find_elements(*self.TABLE_ROWS))


if __name__ == "__main__":
    """独立运行：登录 → 打开用例列表 → 新增 → 验证 → 清理"""
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.chrome.service import Service
    from webdriver_manager.chrome import ChromeDriverManager
    from config import USERNAME, PASSWORD
    from pages.login_page import LoginPage

    options = Options()
    options.add_argument("--no-sandbox")
    options.add_argument("--window-size=1920,1080")
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    driver.implicitly_wait(10)

    test_name = f"PageTest_{int(time.time() * 1000)}"

    try:
        LoginPage(driver).open().login(USERNAME, PASSWORD)
        print("[OK] 登录成功")

        page = CaseListPage(driver)
        page.open()
        print(f"[OK] 用例列表已打开，共 {page.get_case_count()} 条数据")

        headers = page.get_table_headers()
        print(f"[OK] 表头：{headers}")

        page.click_add()
        page.fill_case_form({"caseName": test_name, "level": "P1", "caseType": "功能测试"})
        page.submit_form()
        msg = page.get_success_message()
        print(f"[OK] 新增结果：{msg}")
        time.sleep(1)
        assert page.has_case(test_name), "新增的用例未在表格中找到"

        page.click_delete_by_name(test_name)
        page.confirm_delete()
        msg = page.get_success_message()
        print(f"[OK] 删除结果：{msg}")

        print("[PASS] case_list_page 测试通过")
    except Exception as e:
        print(f"[FAIL] {e}")
        try:
            page = CaseListPage(driver)
            page.open()
            if page.has_case(test_name):
                page.click_delete_by_name(test_name)
                page.confirm_delete()
        except:
            pass
    finally:
        driver.quit()
