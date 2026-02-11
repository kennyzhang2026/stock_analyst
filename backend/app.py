"""
Flask Web应用
股票/ETF分析决策系统
"""

from flask import Flask, render_template, request, jsonify
from apscheduler.schedulers.background import BackgroundScheduler
import atexit

from data_fetcher import DataFetcher, DataFetchError
from analyzer import Analyzer

app = Flask(__name__, template_folder='../frontend/templates')
app.config['JSON_AS_ASCII'] = False

# 全局变量
fetcher = DataFetcher(demo_mode=False)  # 设置为True可强制使用演示模式
analyzer = Analyzer()
cached_analysis = {}
last_update_time = None
demo_mode_enabled = False  # 追踪是否使用了演示模式


def update_data():
    """定时更新数据（每15分钟）"""
    global cached_analysis, last_update_time

    print(f"[{get_current_time()}] 自动更新数据...")

    # 更新所有已缓存的标的
    symbols_to_update = list(cached_analysis.keys())

    for symbol in symbols_to_update:
        try:
            analysis = analyze_symbol(symbol)
            cached_analysis[symbol] = analysis
            print(f"  ✓ {symbol} 更新成功")
        except Exception as e:
            print(f"  ✗ {symbol} 更新失败: {e}")

    last_update_time = get_current_time()
    print(f"[{last_update_time}] 数据更新完成")


def get_current_time():
    """获取当前时间字符串"""
    from datetime import datetime
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')


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
        last_update_time = get_current_time()

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
        last_update_time = get_current_time()

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


# 启动定时器（每15分钟更新一次）
scheduler = BackgroundScheduler(daemon=True)
scheduler.add_job(update_data, 'interval', minutes=15)
scheduler.start()


# 注册退出时关闭调度器
atexit.register(lambda: scheduler.shutdown())


if __name__ == '__main__':
    # 允许局域网访问（手机可以访问）
    # debug=False 避免手机访问问题
    app.run(host='0.0.0.0', port=5000, debug=False)
