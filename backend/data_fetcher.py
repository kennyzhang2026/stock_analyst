"""
数据获取模块
使用 AkShare 获取 A股/基金 数据
"""

import akshare as ak
import pandas as pd
import requests
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional


class DataFetchError(Exception):
    """数据获取异常"""
    pass


class DataFetcher:
    """数据获取器"""

    def __init__(self, demo_mode=False):
        self.missing_data = []  # 记录缺失的数据项
        self.retry_count = 3  # 重试次数
        self.retry_delay = 3  # 重试间隔（秒）
        self.timeout = 30  # 请求超时时间
        self.demo_mode = demo_mode  # 演示模式

    def get_demo_data(self, symbol: str) -> Dict:
        """
        获取演示数据（当网络不可用时使用）
        """
        print("  [演示模式] 使用模拟数据")
        return {
            'code': symbol,
            'name': '港股创新药ETF' if symbol == '513120' else f'ETF{symbol}',
            'price': 0.656,
            'change_pct': 2.15,
            'volume': 125000000,
            'turnover': 82000000,
            'amplitude': 3.2,
            'high': 0.668,
            'low': 0.645,
            'open': 0.650,
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
            # 模拟价格波动
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

    def _test_network(self):
        """测试网络连接"""
        try:
            response = requests.get("https://www.baidu.com", timeout=5)
            return True
        except:
            return False

    def _retry_request(self, func, *args, **kwargs):
        """带重试的请求"""
        last_error = None
        for attempt in range(self.retry_count):
            try:
                print(f"  正在获取数据... (尝试 {attempt + 1}/{self.retry_count})")
                result = func(*args, **kwargs)
                print(f"  ✓ 数据获取成功")
                return result
            except Exception as e:
                last_error = e
                error_msg = str(e)
                print(f"  ✗ 请求失败: {error_msg[:100]}...")

                if attempt < self.retry_count - 1:
                    print(f"  等待 {self.retry_delay} 秒后重试...")
                    time.sleep(self.retry_delay)
                else:
                    print(f"  重试 {self.retry_count} 次后仍然失败")

                    # 检查是否是网络问题
                    if "Connection" in error_msg or "Network" in error_msg or "connect" in error_msg.lower():
                        print("  ⚠️ 可能是网络连接问题，请检查:")
                        print("     - 网络是否正常")
                        print("     - 是否需要配置代理")
                        print("     - 防火墙是否阻止Python访问网络")

        raise last_error

    def get_etf_spot(self, symbol: str) -> Dict:
        """
        获取ETF实时行情

        Args:
            symbol: ETF代码，如 '513120'

        Returns:
            包含实时行情信息的字典
        """
        # 如果是演示模式，直接返回模拟数据
        if self.demo_mode:
            return self.get_demo_data(symbol)

        def _fetch():
            # 尝试获取ETF实时行情
            try:
                df = ak.fund_etf_spot_em()
            except Exception as e:
                raise DataFetchError(f"AkShare获取ETF列表失败: {e}")

            etf = df[df['代码'] == symbol]

            if etf.empty:
                raise DataFetchError(f"未找到ETF代码: {symbol}")

            return {
                'code': symbol,
                'name': etf['名称'].values[0],
                'price': float(etf['最新价'].values[0]),
                'change_pct': float(etf['涨跌幅'].values[0]),
                'volume': float(etf['成交量'].values[0]),
                'turnover': float(etf['成交额'].values[0]),
                'amplitude': float(etf['振幅'].values[0]) if '振幅' in etf.columns else 0,
                'high': float(etf['最高'].values[0]) if '最高' in etf.columns else 0,
                'low': float(etf['最低'].values[0]) if '最低' in etf.columns else 0,
                'open': float(etf['今开'].values[0]) if '今开' in etf.columns else 0,
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }

        try:
            return self._retry_request(_fetch)
        except Exception as e:
            # 网络失败时自动切换到演示模式
            print("  ⚠️ 网络获取失败，切换到演示模式")
            self.missing_data.append(f"ETF实时行情: {str(e)} - 使用演示数据")
            return self.get_demo_data(symbol)

    def get_kline(self, symbol: str, days: int = 252) -> pd.DataFrame:
        """
        获取K线数据（默认获取约一年的交易日数据）

        Args:
            symbol: ETF代码
            days: 获取天数

        Returns:
            K线数据DataFrame
        """
        # 如果是演示模式，直接返回模拟数据
        if self.demo_mode:
            return self.get_demo_kline()

        def _fetch():
            end_date = datetime.now().strftime('%Y%m%d')
            start_date = (datetime.now() - timedelta(days=days * 2)).strftime('%Y%m%d')

            df = ak.fund_etf_hist_em(
                symbol=symbol,
                period="daily",
                start_date=start_date,
                end_date=end_date,
                adjust="qfq"  # 前复权
            )

            if df.empty:
                raise DataFetchError(f"未获取到K线数据: {symbol}")

            # 确保数据列名统一
            df = df.rename(columns={
                '日期': 'date',
                '开盘': 'open',
                '收盘': 'close',
                '最高': 'high',
                '最低': 'low',
                '成交量': 'volume',
                '成交额': 'turnover'
            })

            return df

        try:
            return self._retry_request(_fetch)
        except Exception as e:
            # 网络失败时自动切换到演示模式
            print("  ⚠️ K线数据获取失败，切换到演示模式")
            self.missing_data.append(f"K线数据: {str(e)} - 使用演示数据")
            return self.get_demo_kline()

    def get_ma(self, df: pd.DataFrame, period: int = 20) -> float:
        """
        计算移动平均线

        Args:
            df: K线数据
            period: 周期

        Returns:
            MA值
        """
        if len(df) < period:
            return 0
        return df['close'].tail(period).mean()

    def get_year_high_low(self, df: pd.DataFrame) -> Dict:
        """
        获取年内高低点

        Args:
            df: K线数据

        Returns:
            {'high': 年内最高, 'low': 年内最低}
        """
        if df.empty:
            return {'high': 0, 'low': 0}

        # 获取今年的数据
        df['date'] = pd.to_datetime(df['date'])
        current_year = datetime.now().year
        year_data = df[df['date'].dt.year == current_year]

        if year_data.empty:
            # 如果今年数据不足，用全部数据
            year_data = df

        return {
            'high': year_data['high'].max(),
            'low': year_data['low'].min()
        }

    def get_5_day_change(self, df: pd.DataFrame) -> float:
        """
        获取近5日涨跌幅

        Args:
            df: K线数据

        Returns:
            近5日涨跌幅（百分比）
        """
        if len(df) < 5:
            return 0

        recent = df.tail(5)
        start_price = recent.iloc[0]['close']
        end_price = recent.iloc[-1]['close']

        if start_price == 0:
            return 0

        return ((end_price - start_price) / start_price) * 100

    def check_volume_trend(self, df: pd.DataFrame) -> str:
        """
        检查量能配合情况

        Args:
            df: K线数据

        Returns:
            'up' (放量上涨), 'down' (缩量或其他)
        """
        if len(df) < 5:
            return 'unknown'

        recent = df.tail(5)
        avg_volume = df['volume'].mean()
        recent_avg_volume = recent['volume'].mean()

        price_change = (recent.iloc[-1]['close'] - recent.iloc[0]['close']) / recent.iloc[0]['close']

        # 价格上涨且量能放大
        if price_change > 0 and recent_avg_volume > avg_volume * 1.2:
            return 'up'
        elif price_change > 0:
            return 'up_low_volume'
        else:
            return 'down'

    def get_missing_data_report(self) -> List[str]:
        """
        获取缺失数据报告

        Returns:
            缺失数据列表
        """
        return self.missing_data

    def clear_missing_data(self):
        """清空缺失数据记录"""
        self.missing_data = []
