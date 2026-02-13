"""
Vercel Serverless 入口
Vercel 会自动识别名为 'app' 的 Flask 实例
"""

# 导入我们的 Flask app（命名为 app 供 Vercel 识别）
from backend.app import app

# Vercel 会自动处理这个 app 变量
# 不需要额外的 handler 或 main 代码
