# RuoYi UI 自动化测试

基于 Pytest + Selenium 的 RuoYi-Vue 前后端分离项目 UI 自动化测试框架。

## 功能覆盖

- **登录模块** — 用户登录流程自动化验证
- **测试用例管理** — 功能测试用例的增删改查操作验证
- **测试计划管理** — 测试计划的创建与执行跟踪验证
- **接口调试** — 在线接口调试页面操作验证

## 技术栈

| 技术 | 用途 |
|------|------|
| Python | 测试脚本语言 |
| Pytest | 测试框架 |
| Selenium | 浏览器自动化 |
| Page Object Model | 页面对象设计模式 |

## 快速开始

```bash
# 安装依赖
pip install -r requirements.txt

# 运行测试
pytest -v
```

## 项目结构

```
├── config.py                  # 测试配置（URL、账号等）
├── conftest.py                # Pytest fixtures
├── pages/                     # Page Object 页面对象
│   ├── login_page.py          # 登录页面
│   ├── case_list_page.py      # 用例列表页面
│   └── case_detail_page.py    # 用例详情页面
├── tests/                     # 测试用例
│   └── test_functional_case.py
├── pytest.ini                 # Pytest 配置
└── requirements.txt           # 依赖清单
```
