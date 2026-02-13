"""
Vercel Serverless 入口
此文件作为 Vercel Python runtime 的入口点
"""

from vercel_wsgi import handle_wsgi_event
from backend.app import app

# Vercel Serverless handler
def handler(event, context):
    return handle_wsgi_event(app, event, context)
