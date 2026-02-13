"""
Vercel Serverless 入口
此文件作为 Vercel Python runtime 的入口点
"""

import sys
import os

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# 导入 Flask app 和所有依赖
# Vercel 需要在此文件中能够访问到一个名为 'app' 的 WSGI 应用实例
from backend.app import app as application

# Vercel Python runtime 会自动使用这个 'app' 变量
# 或者查找名为 'application' 的 WSGI 应用
app = application

# 导出供 Vercel 使用
__all__ = ['app']
