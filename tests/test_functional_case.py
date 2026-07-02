# -*- coding: utf-8 -*-
"""
测试管理 > 功能测试 > 测试用例 UI 自动化测试

每个测试用例完全独立，可单独运行：
  pytest tests/test_functional_case.py::TestFunctionalCase::test_add_case -v

10 个测试用例：
1. test_add_case           - 新增测试用例
2. test_list_cases          - 用例列表加载
3. test_search_by_name      - 按名称搜索
4. test_search_by_level     - 按优先级搜索
5. test_reset_search        - 重置搜索
6. test_edit_case           - 修改用例
7. test_detail_navigation   - 详情页跳转
8. test_add_and_delete_case - 新增后删除
9. test_batch_delete        - 批量删除
10. test_add_validation     - 表单校验
"""
import time
import pytest
from pages.case_list_page import CaseListPage


def _unique_name(prefix="UI"):
    """生成带时间戳的唯一用例名称"""
    return f"{prefix}_{int(time.time() * 1000)}"


def _cleanup_case(case_page, name):
    """安全清理：搜索并删除指定名称的用例"""
    try:
        case_page.reset_search()
        case_page.search_by_name(name)
        if case_page.has_case(name):
            case_page.click_delete_by_name(name)
            case_page.confirm_delete()
        case_page.reset_search()
    except:
        pass


class TestFunctionalCase:
    """测试用例功能测试 —— 每个用例完全独立"""

    # ─────────────────────────────────────────────
    # 1. 新增测试用例
    # ─────────────────────────────────────────────
    def test_add_case(self, case_page: CaseListPage):
        """新增一个测试用例，验证成功提示和表格中出现新用例"""
        name = _unique_name("新增")
        try:
            case_page.click_add()
            assert case_page.is_dialog_open(), "新增对话框未打开"
            assert case_page.get_dialog_title() == "新增测试用例"

            case_page.fill_case_form({
                "caseName": name,
                "level": "P1",
                "caseType": "功能测试",
                "precondition": "用户已登录系统",
                "expected": "操作成功",
            })
            case_page.submit_form()

            msg = case_page.get_success_message()
            assert "新增成功" in msg, f"期望'新增成功'，实际：{msg}"
            time.sleep(1)  # 等待表格刷新
            assert case_page.has_case(name), f"表格中未找到新增的用例：{name}"
        finally:
            _cleanup_case(case_page, name)

    # ─────────────────────────────────────────────
    # 2. 用例列表加载
    # ─────────────────────────────────────────────
    def test_list_cases(self, case_page: CaseListPage):
        """验证列表页正常加载，表头正确"""
        from selenium.webdriver.common.by import By

        headers = case_page.get_table_headers()
        expected_headers = ["用例名称", "优先级", "类型", "状态", "创建时间", "操作"]
        for h in expected_headers:
            assert h in headers, f"表头缺少：{h}"

        pagination = case_page.driver.find_elements(By.CSS_SELECTOR, '.el-pagination')
        assert len(pagination) > 0, "分页组件未找到"

    # ─────────────────────────────────────────────
    # 3. 按名称搜索
    # ─────────────────────────────────────────────
    def test_search_by_name(self, case_page: CaseListPage):
        """先新增用例，再按名称搜索，验证只显示匹配结果"""
        name = _unique_name("搜索")
        try:
            # 新增
            case_page.click_add()
            case_page.fill_case_form({"caseName": name, "level": "P0"})
            case_page.submit_form()
            case_page.get_success_message()

            # 搜索
            case_page.search_by_name(name)
            time.sleep(1)
            data = case_page.get_table_data()

            assert len(data) >= 1, "搜索结果为空"
            assert all(name in row["caseName"] for row in data), \
                "搜索结果包含不匹配的用例"
        finally:
            _cleanup_case(case_page, name)

    # ─────────────────────────────────────────────
    # 4. 按优先级搜索
    # ─────────────────────────────────────────────
    def test_search_by_level(self, case_page: CaseListPage):
        """按优先级 P0 搜索，验证所有结果优先级均为 P0"""
        try:
            case_page.search_by_level("P0")
            data = case_page.get_table_data()

            if len(data) > 0:
                for row in data:
                    assert "P0" in row["level"], f"优先级不匹配：{row['level']}"
        finally:
            case_page.reset_search()

    # ─────────────────────────────────────────────
    # 5. 重置搜索
    # ─────────────────────────────────────────────
    def test_reset_search(self, case_page: CaseListPage):
        """输入搜索条件后重置，验证搜索框清空"""
        from selenium.webdriver.common.by import By

        case_page.search_by_name("随便输入的内容")
        case_page.reset_search()

        el = case_page.driver.find_element(*CaseListPage.INPUT_CASE_NAME)
        assert el.get_attribute("value") == "", "搜索框未清空"

    # ─────────────────────────────────────────────
    # 6. 修改用例
    # ─────────────────────────────────────────────
    def test_edit_case(self, case_page: CaseListPage):
        """新增用例后修改标题，验证修改成功"""
        name = _unique_name("改前")
        new_name = _unique_name("改后")
        try:
            # 新增
            case_page.click_add()
            case_page.fill_case_form({"caseName": name, "level": "P2"})
            case_page.submit_form()
            case_page.get_success_message()

            # 修改
            case_page.click_edit_by_name(name)
            assert case_page.get_dialog_title() == "修改测试用例"
            case_page.fill_case_form({"caseName": new_name})
            case_page.submit_form()

            msg = case_page.get_success_message()
            assert "修改成功" in msg, f"期望'修改成功'，实际：{msg}"
            time.sleep(1)  # 等待表格刷新
            assert case_page.has_case(new_name), "修改后的用例未在表格中找到"
        finally:
            _cleanup_case(case_page, new_name)
            _cleanup_case(case_page, name)

    # ─────────────────────────────────────────────
    # 7. 详情页跳转
    # ─────────────────────────────────────────────
    def test_detail_navigation(self, case_page: CaseListPage, detail_page):
        """新增用例后点击详情，验证跳转到详情页"""
        name = _unique_name("详情")
        try:
            case_page.click_add()
            case_page.fill_case_form({
                "caseName": name,
                "level": "P1",
                "caseType": "功能测试",
                "expected": "详情页显示正确",
            })
            case_page.submit_form()
            case_page.get_success_message()
            time.sleep(1)  # 等待表格刷新

            case_page.click_detail_by_name(name)

            assert "/test/functional/case/detail/" in case_page.driver.current_url, \
                f"未跳转到详情页，当前URL：{case_page.driver.current_url}"

            assert detail_page.is_loaded(), "详情页未加载"
            detail_name = detail_page.get_case_name()
            assert name in detail_name, f"详情页用例名称不匹配：{detail_name}"

            detail_page.click_back()
            time.sleep(0.5)
        finally:
            # 返回列表页后清理
            case_page.open()
            _cleanup_case(case_page, name)

    # ─────────────────────────────────────────────
    # 8. 新增后删除
    # ─────────────────────────────────────────────
    def test_add_and_delete_case(self, case_page: CaseListPage):
        """新增用例后删除，验证删除成功"""
        name = _unique_name("删测")
        try:
            case_page.click_add()
            case_page.fill_case_form({"caseName": name, "level": "P3"})
            case_page.submit_form()
            case_page.get_success_message()
            time.sleep(1)  # 等待表格刷新

            case_page.click_delete_by_name(name)
            case_page.confirm_delete()

            msg = case_page.get_success_message()
            assert "删除成功" in msg, f"期望'删除成功'，实际：{msg}"
            time.sleep(0.5)
            assert not case_page.has_case(name), f"删除后用例仍存在：{name}"
        finally:
            _cleanup_case(case_page, name)

    # ─────────────────────────────────────────────
    # 9. 批量删除
    # ─────────────────────────────────────────────
    def test_batch_delete(self, case_page: CaseListPage):
        """新增两个用例后批量删除"""
        name1 = _unique_name("批A")
        name2 = _unique_name("批B")
        try:
            case_page.click_add()
            case_page.fill_case_form({"caseName": name1, "level": "P2"})
            case_page.submit_form()
            case_page.get_success_message()
            time.sleep(1)  # 等待表格刷新

            case_page.click_add()
            case_page.fill_case_form({"caseName": name2, "level": "P2"})
            case_page.submit_form()
            case_page.get_success_message()
            time.sleep(1)  # 等待表格刷新

            case_page.select_row_by_name(name1)
            case_page.select_row_by_name(name2)
            case_page.click_batch_delete()
            case_page.confirm_delete()

            msg = case_page.get_success_message()
            assert "删除成功" in msg, f"期望'删除成功'，实际：{msg}"
        finally:
            _cleanup_case(case_page, name1)
            _cleanup_case(case_page, name2)

    # ─────────────────────────────────────────────
    # 10. 表单校验
    # ─────────────────────────────────────────────
    def test_add_validation(self, case_page: CaseListPage):
        """不填写必填字段直接提交，验证校验错误提示"""
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        from config import EXPLICIT_WAIT

        try:
            case_page.click_add()
            case_page.submit_form()

            wait = WebDriverWait(case_page.driver, EXPLICIT_WAIT)
            error_el = wait.until(EC.visibility_of_element_located(
                (By.CSS_SELECTOR, '.el-form-item__error')
            ))
            error_text = error_el.text
            assert "不能为空" in error_text or "请选择" in error_text, \
                f"未检测到校验错误提示：{error_text}"
        finally:
            case_page.cancel_form()
