"""
Vercel Serverless 入口
此文件作为 Vercel Python runtime 的入口点
"""

import sys
import os

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# 导入 Flask app
from backend.app import app

# Vercel Python runtime 会自动查找并使用名为 'app' 的 WSGI 应用实例
# 直接使用 Flask app 对象，无需额外处理

# 导出供 Vercel 使用
__all__ = ['app']
