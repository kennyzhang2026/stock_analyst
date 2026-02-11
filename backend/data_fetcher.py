"""
数据获取模块
支持多种数据源：天天基金网API、AkShare
"""

import akshare as ak
import pandas as pd
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional


class DataFetchError(Exception):
    """数据获取异常"""
    pass


class DataFetcher:
    """数据获取器"""

    def __init__(self, demo_mode=False):
        self.missing_data = []  # 记录缺失的数据项
        self.demo_mode = demo_mode  # 演示模式
        self.timeout = 10  # 请求超时时间（秒）

        # 天天基金/东方财富API请求头
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Referer": "https://fund.eastmoney.com/"
        }

    # ==================== 演示数据 ====================

    def get_demo_data(self, symbol: str) -> Dict:
        """获取演示数据（当网络不可用时使用）"""
        import numpy as np
        np.random.seed(int(datetime.now().timestamp()))

        # 模拟一个相对合理的价格
        base_price = 0.65 + np.random.randn() * 0.02
        change_pct = np.random.randn() * 3

        return {
            'code': symbol,
            'name': '港股创新药ETF' if symbol == '513120' else f'ETF{symbol}',
            'price': round(base_price, 3),
            'change_pct': round(change_pct, 2),
            'volume': np.random.randint(50000000, 200000000),
            'turnover': np.random.randint(50000000, 150000000),
            'high': round(base_price * 1.02, 3),
            'low': round(base_price * 0.98, 3),
            'open': round(base_price * (1 + np.random.randn() * 0.01), 3),
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }

    def get_demo_kline(self) -> pd.DataFrame:
        """获取演示K线数据"""
        import numpy as np
        np.random.seed(42)

        dates = pd.date_range(end=datetime.now(), periods=60, freq='D')
        base_price = 0.650

        data = []
        price = base_price
        for i, date in enumerate(dates):
            change = np.random.randn() * 0.02
            price = price * (1 + change)

            high = price * (1 + abs(np.random.randn() * 0.01))
            low = price * (1 - abs(np.random.randn() * 0.01))
            open_price = price * (1 + np.random.randn() * 0.005)
            volume = np.random.randint(50000000, 200000000)

            data.append({
                'date': date.strftime('%Y-%m-%d'),
                'open': round(open_price, 3),
                'close': round(price, 3),
                'high': round(high, 3),
                'low': round(low, 3),
                'volume': volume,
                'turnover': volume * price
            })

        return pd.DataFrame(data)

    # ==================== 实时行情 ====================

    def get_etf_spot(self, symbol: str) -> Dict:
        """
        获取ETF实时行情
        优先使用天天基金网API，失败后尝试AkShare

        Args:
            symbol: ETF代码，如 '513120'

        Returns:
            包含实时行情信息的字典
        """
        if self.demo_mode:
            return self.get_demo_data(symbol)

        # 方法1: 东方财富实时行情API
        try:
            print("  [方法1] 东方财富实时行情API...")
            url = f"https://quote.eastmoney.com/api/qt/ulist.np/get?fltt=2&invt=2&fields=f12,f13,f14,f2,f3,f4,f5,f6,f7,f15,f16,f17&secids=1.{symbol}"
            response = requests.get(url, headers=self.headers, timeout=self.timeout)

            if response.status_code == 200:
                data = response.json()
                if data.get('data') and data['data'].get('diff'):
                    item = data['data']['diff'][0]
                    price = item.get('f2', 0) / 100 if item.get('f2') else 0
                    print(f"  ✓ 成功: {item.get('f14', '')} ¥{price:.3f}")
                    return {
                        'code': symbol,
                        'name': item.get('f14', f'ETF{symbol}'),
                        'price': price,
                        'change_pct': item.get('f3', 0) / 100 if item.get('f3') else 0,
                        'volume': item.get('f5', 0),
                        'turnover': item.get('f6', 0),
                        'high': item.get('f15', 0) / 100 if item.get('f15') else 0,
                        'low': item.get('f16', 0) / 100 if item.get('f16') else 0,
                        'open': item.get('f17', 0) / 100 if item.get('f17') else 0,
                        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    }
        except Exception as e:
            print(f"  ✗ 失败: {str(e)[:60]}...")

        # 方法2: AkShare
        try:
            print("  [方法2] AkShare...")
            df = ak.fund_etf_spot_em()
            etf = df[df['代码'] == symbol]

            if not etf.empty:
                print(f"  ✓ 成功: {etf['名称'].values[0]}")
                return {
                    'code': symbol,
                    'name': etf['名称'].values[0],
                    'price': float(etf['最新价'].values[0]),
                    'change_pct': float(etf['涨跌幅'].values[0]),
                    'volume': float(etf['成交量'].values[0]),
                    'turnover': float(etf['成交额'].values[0]),
                    'high': float(etf['最高'].values[0]) if '最高' in etf.columns else 0,
                    'low': float(etf['最低'].values[0]) if '最低' in etf.columns else 0,
                    'open': float(etf['今开'].values[0]) if '今开' in etf.columns else 0,
                    'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }
        except Exception as e:
            print(f"  ✗ 失败: {str(e)[:60]}...")

        # 都失败，使用演示数据
        print("  ⚠️ 使用演示数据")
        self.missing_data.append("所有实时行情数据源均失败，使用演示数据")
        return self.get_demo_data(symbol)

    # ==================== K线数据 ====================

    def get_kline(self, symbol: str, days: int = 252) -> pd.DataFrame:
        """
        获取K线数据
        优先使用东方财富API，失败后尝试AkShare

        Args:
            symbol: ETF代码
            days: 获取天数

        Returns:
            K线数据DataFrame
        """
        if self.demo_mode:
            return self.get_demo_kline()

        end_date = datetime.now().strftime('%Y%m%d')
        start_date = (datetime.now() - timedelta(days=days * 2)).strftime('%Y%m%d')

        # 方法1: 东方财富K线API
        try:
            print("  [方法1] 东方财富K线API...")
            secid = f"1.{symbol}"
            url = f"https://push2his.eastmoney.com/api/qt/stock/kline/get?secid={secid}&fields1=f1,f2,f3,f4,f5,f6&fields2=f51,f52,f53,f54,f55,f56&klt=101&fqt=1&beg={start_date}&end={end_date}"

            response = requests.get(url, headers=self.headers, timeout=self.timeout)

            if response.status_code == 200:
                data = response.json()
                if data.get('data') and data['data'].get('klines'):
                    klines = data['data']['klines']
                    df_data = []
                    for k in klines:
                        parts = k.split(',')
                        df_data.append({
                            'date': parts[0],
                            'open': float(parts[1]),
                            'close': float(parts[2]),
                            'high': float(parts[3]),
                            'low': float(parts[4]),
                            'volume': float(parts[5]),
                            'turnover': float(parts[6]) if len(parts) > 6 else 0
                        })
                    print(f"  ✓ 成功: {len(df_data)} 条K线数据")
                    return pd.DataFrame(df_data)
        except Exception as e:
            print(f"  ✗ 失败: {str(e)[:60]}...")

        # 方法2: AkShare K线
        try:
            print("  [方法2] AkShare K线...")
            df = ak.fund_etf_hist_em(
                symbol=symbol,
                period="daily",
                start_date=start_date,
                end_date=end_date,
                adjust="qfq"
            )

            if not df.empty:
                df = df.rename(columns={
                    '日期': 'date',
                    '开盘': 'open',
                    '收盘': 'close',
                    '最高': 'high',
                    '最低': 'low',
                    '成交量': 'volume',
                    '成交额': 'turnover'
                })
                print(f"  ✓ 成功: {len(df)} 条K线数据")
                return df
        except Exception as e:
            print(f"  ✗ 失败: {str(e)[:60]}...")

        # 都失败，使用演示数据
        print("  ⚠️ 使用演示数据")
        self.missing_data.append("所有K线数据源均失败，使用演示数据")
        return self.get_demo_kline()

    # ==================== 技术指标计算 ====================

    def get_ma(self, df: pd.DataFrame, period: int = 20) -> float:
        """计算移动平均线"""
        if len(df) < period:
            return 0
        return df['close'].tail(period).mean()

    def get_year_high_low(self, df: pd.DataFrame) -> Dict:
        """获取年内高低点"""
        if df.empty:
            return {'high': 0, 'low': 0}

        df['date'] = pd.to_datetime(df['date'])
        current_year = datetime.now().year
        year_data = df[df['date'].dt.year == current_year]

        if year_data.empty:
            year_data = df

        return {
            'high': year_data['high'].max(),
            'low': year_data['low'].min()
        }

    def get_5_day_change(self, df: pd.DataFrame) -> float:
        """获取近5日涨跌幅"""
        if len(df) < 5:
            return 0

        recent = df.tail(5)
        start_price = recent.iloc[0]['close']
        end_price = recent.iloc[-1]['close']

        if start_price == 0:
            return 0

        return ((end_price - start_price) / start_price) * 100

    def check_volume_trend(self, df: pd.DataFrame) -> str:
        """检查量能配合情况"""
        if len(df) < 5:
            return 'unknown'

        recent = df.tail(5)
        avg_volume = df['volume'].mean()
        recent_avg_volume = recent['volume'].mean()

        price_change = (recent.iloc[-1]['close'] - recent.iloc[0]['close']) / recent.iloc[0]['close']

        if price_change > 0 and recent_avg_volume > avg_volume * 1.2:
            return 'up'
        elif price_change > 0:
            return 'up_low_volume'
        else:
            return 'down'

    # ==================== 工具方法 ====================

    def get_missing_data_report(self) -> List[str]:
        """获取缺失数据报告"""
        return self.missing_data

    def clear_missing_data(self):
        """清空缺失数据记录"""
        self.missing_data = []
