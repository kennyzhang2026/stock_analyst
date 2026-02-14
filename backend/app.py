"""
Flask Web应用
股票/ETF分析决策系统
"""

import os
import time
from datetime import datetime
from flask import Flask, render_template, request, jsonify, Response

# 只在非 serverless 环境中导入 APScheduler
IS_SERVERLESS = os.environ.get('VERCEL') or os.environ.get('AWS_LAMBDA_FUNCTION_VERSION')

if not IS_SERVERLESS:
    from apscheduler.schedulers.background import BackgroundScheduler
    from apscheduler.triggers.cron import CronTrigger
    import atexit

from .data_fetcher import DataFetcher, DataFetchError
from .analyzer import Analyzer
from .database import db
from . import scheduler_utils

app = Flask(__name__, template_folder='../frontend/templates')
app.config['JSON_AS_ASCII'] = False

# 全局变量
fetcher = DataFetcher(demo_mode=False)  # False=尝试真实数据，True=强制演示模式
analyzer = Analyzer()
cached_analysis = {}
last_update_time = None
demo_mode_enabled = False  # 追踪是否使用了演示模式


def update_data():
    """交易时间定时更新数据（每小时 9:00-15:00）"""
    global cached_analysis, last_update_time

    current_time = scheduler_utils.get_current_time()

    # 检查是否在交易时间
    if not scheduler_utils.is_trading_hours():
        scheduler_utils.log_scheduled_update(is_trading_hours=False, symbols_updated=0)
        return

    # 从数据库获取需要更新的标的列表
    symbols = scheduler_utils.get_scheduled_symbols()

    if not symbols:
        print(f"[{current_time}] 没有需要更新的标的")
        scheduler_utils.log_scheduled_update(is_trading_hours=True, symbols_updated=0)
        return

    print(f"[{current_time}] 开始更新数据，共 {len(symbols)} 个标的...")

    updated_count = 0
    errors = []

    for symbol in symbols:
        try:
            analysis = analyze_symbol(symbol)
            cached_analysis[symbol] = analysis
            updated_count += 1
            print(f"  ✓ {symbol} 更新成功")
        except Exception as e:
            error_msg = f"{symbol}: {str(e)}"
            errors.append(error_msg)
            print(f"  ✗ {error_msg}")

    last_update_time = current_time

    # 记录日志
    scheduler_utils.log_scheduled_update(
        is_trading_hours=True,
        symbols_updated=updated_count,
        errors="; ".join(errors) if errors else None
    )

    # 通知前端有更新
    scheduler_utils.notify_update()

    print(f"[{current_time}] 数据更新完成 - 成功 {updated_count} 个，失败 {len(errors)} 个")


def analyze_symbol(symbol: str) -> dict:
    """分析单个标的"""
    # 获取实时行情
    spot = fetcher.get_etf_spot(symbol)

    # 获取K线数据
    kline = fetcher.get_kline(symbol, days=252)

    # 计算各项指标
    ma20 = fetcher.get_ma(kline, 20)
    year_high_low = fetcher.get_year_high_low(kline)
    day5_change = fetcher.get_5_day_change(kline)
    volume_trend = fetcher.check_volume_trend(kline)

    # 执行分析
    analysis = analyzer.analyze(
        symbol=symbol,
        spot=spot,
        kline_data=kline,
        ma20=ma20,
        year_high_low=year_high_low,
        day5_change=day5_change,
        volume_trend=volume_trend
    )

    # 保存到数据库
    try:
        db.save_analysis(symbol, analysis)
    except Exception as e:
        print(f"  ⚠️ {symbol} 保存到数据库失败: {e}")

    return analysis


@app.route('/')
def index():
    """主页"""
    return render_template('index.html',
                         cached_analysis=cached_analysis,
                         last_update_time=last_update_time)


@app.route('/api/analyze', methods=['POST'])
def api_analyze():
    """分析接口"""
    global cached_analysis, last_update_time

    data = request.get_json()
    symbol = data.get('symbol', '').strip()

    if not symbol:
        return jsonify({'error': '请输入标的代码'}), 400

    try:
        # 执行分析
        analysis = analyze_symbol(symbol)
        cached_analysis[symbol] = analysis
        last_update_time = scheduler_utils.get_current_time()

        return jsonify({
            'success': True,
            'data': analysis
        })

    except DataFetchError as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'分析失败: {str(e)}'
        }), 500


@app.route('/api/refresh', methods=['POST'])
def api_refresh():
    """刷新指定标的"""
    global last_update_time

    data = request.get_json()
    symbol = data.get('symbol', '').strip()

    if not symbol or symbol not in cached_analysis:
        return jsonify({'error': '标的代码无效或未分析过'}), 400

    try:
        analysis = analyze_symbol(symbol)
        cached_analysis[symbol] = analysis
        last_update_time = scheduler_utils.get_current_time()

        return jsonify({
            'success': True,
            'data': analysis
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400


@app.route('/api/health')
def health():
    """健康检查"""
    return jsonify({
        'status': 'ok',
        'cached_count': len(cached_analysis),
        'last_update': last_update_time
    })


@app.route('/api/events')
def sse_stream():
    """Server-Sent Events端点，用于推送更新通知"""
    def event_stream():
        last_notification = None
        while True:
            # 检查是否有新的更新
            if scheduler_utils.has_new_update(last_notification):
                last_notification = datetime.now()
                yield f"data: {jsonify({'type': 'update', 'time': scheduler_utils.get_current_time()}).get_data(as_text=True)}\n\n"

            time.sleep(1)  # 每秒检查一次

    return Response(event_stream(), mimetype="text/event-stream")


# 启动定时器（工作日9:00-15:00每小时更新一次）
# 只在非 serverless 环境中启动
if not IS_SERVERLESS:
    scheduler = BackgroundScheduler(daemon=True)

    # 使用CronTrigger实现交易时间定时任务
    # day_of_week: 'mon-fri' 表示周一到周五
    # hour: '9-14' 表示9点到14点（15点收盘不更新）
    # minute: '0' 表示整点执行
    scheduler.add_job(
        update_data,
        CronTrigger(day_of_week='mon-fri', hour='9-14', minute='0'),
        id='trading_hours_update',
        replace_existing=True
    )

    scheduler.start()

    # 注册退出时关闭调度器
    atexit.register(lambda: scheduler.shutdown())


if __name__ == '__main__':
    # 允许局域网访问（手机可以访问）
    # debug=False 避免手机访问问题
    app.run(host='0.0.0.0', port=5000, debug=False)
