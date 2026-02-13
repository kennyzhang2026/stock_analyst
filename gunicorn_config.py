"""
Gunicorn 配置文件
用于生产环境的 WSGI 服务器配置
"""
import multiprocessing
import os

# 服务器绑定地址
bind = "0.0.0.0:5000"

# 工作进程数（根据1H1G配置调整为2）
workers = 2

# 工作模式（gevent适合异步IO场景）
worker_class = "sync"

# 每个工作进程的线程数
threads = 2

# 超时时间
timeout = 120
keepalive = 5

# 日志配置
accesslog = "-"  # 输出到stdout
errorlog = "-"   # 输出到stderr
loglevel = "info"

# 进程名称
proc_name = "stock_analyst"

# 守护进程（True=后台运行，False=前台运行）
# 使用systemd管理时建议设为False
daemon = False

# PID文件（用于进程管理）
pidfile = "/tmp/stock_analyst.pid"

# 工作目录
chdir = os.path.dirname(os.path.abspath(__file__))

# 重启时加载的 WSGI 应用
wsgi_app = "backend.app:app"
