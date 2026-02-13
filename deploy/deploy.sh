#!/bin/bash
# 股票分析系统 - 云端部署脚本
# 适用于主机屋或类似配置的云服务器 (1H1G5M)

set -e  # 遇到错误立即退出

echo "=========================================="
echo "   Stock Analyst 云端部署脚本 v1.0"
echo "=========================================="

# 配置变量
APP_DIR="/opt/stock_analyst"
APP_USER="www-data"
NGINX_CONF="/etc/nginx/sites-available/stock_analyst"
SYSTEMD_SERVICE="/etc/systemd/system/stock_analyst.service"

# 检查是否为root用户
if [ "$EUID" -ne 0 ]; then
    echo "❌ 请使用 sudo 运行此脚本"
    exit 1
fi

echo ""
echo "📦 步骤 1/8: 更新系统包..."
apt update && apt upgrade -y

echo ""
echo "📦 步骤 2/8: 安装系统依赖..."
apt install -y python3 python3-pip python3-venv nginx

echo ""
echo "📦 步骤 3/8: 创建应用目录..."
mkdir -p $APP_DIR

echo ""
echo "📦 步骤 4/8: 创建Python虚拟环境..."
python3 -m venv $APP_DIR/venv
source $APP_DIR/venv/bin/activate

echo ""
echo "📦 步骤 5/8: 安装Python依赖..."
# 假设requirements.txt在当前目录
if [ -f "requirements.txt" ]; then
    pip install --upgrade pip
    pip install -r requirements.txt
    echo "✅ 依赖安装完成"
else
    echo "❌ 找不到 requirements.txt，请确保在项目根目录运行此脚本"
    exit 1
fi

echo ""
echo "📦 步骤 6/8: 复制项目文件..."
cp -r backend $APP_DIR/
cp -r frontend $APP_DIR/
cp gunicorn_config.py $APP_DIR/
cp requirements.txt $APP_DIR/

echo ""
echo "📦 步骤 7/8: 配置Nginx..."
if [ -f "deploy/nginx.conf" ]; then
    # 替换域名（用户需要手动修改）
    sed "s/your-domain.com/_/g" deploy/nginx.conf > $NGINX_CONF
    ln -sf $NGINX_CONF /etc/nginx/sites-enabled/stock_analyst
    # 删除默认站点（可选）
    # rm -f /etc/nginx/sites-enabled/default
    nginx -t
    systemctl restart nginx
    echo "✅ Nginx配置完成"
else
    echo "⚠️  Nginx配置文件不存在，跳过"
fi

echo ""
echo "📦 步骤 8/8: 配置Systemd服务..."
if [ -f "deploy/stock_analyst.service" ]; then
    cp deploy/stock_analyst.service $SYSTEMD_SERVICE
    systemctl daemon-reload
    systemctl enable stock_analyst
    systemctl start stock_analyst
    echo "✅ Systemd服务配置完成"
else
    echo "⚠️  Systemd服务文件不存在，跳过"
fi

echo ""
echo "=========================================="
echo "   🎉 部署完成！"
echo "=========================================="
echo ""
echo "📊 服务状态检查："
echo "   systemctl status stock_analyst"
echo ""
echo "📋 查看日志："
echo "   journalctl -u stock_analyst -f"
echo ""
echo "🔄 重启服务："
echo "   systemctl restart stock_analyst"
echo ""
echo "⚙️  修改Nginx配置后重载："
echo "   nginx -s reload"
echo ""
