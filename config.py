# -*- coding: utf-8 -*-
"""全局配置"""

# 基础 URL
BASE_URL = "http://localhost:8088"
LOGIN_URL = f"{BASE_URL}/login"
CASE_URL = f"{BASE_URL}/test/functional/case"

# 登录账号
USERNAME = "admin"
PASSWORD = "admin123"

# 超时配置（秒）
IMPLICIT_WAIT = 10
EXPLICIT_WAIT = 15
PAGE_LOAD_TIMEOUT = 30
