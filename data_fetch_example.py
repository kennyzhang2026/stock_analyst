"""
A股数据获取示例
支持多种数据源: AkShare, Tushare, BaoStock
"""

import akshare as ak
import pandas as pd
from datetime import datetime, timedelta


class StockDataFetcher:
    """股票数据获取器"""

    def get_stock_info(self, symbol: str) -> dict:
        """获取股票基本信息"""
        try:
            # A股实时行情
            if symbol.startswith('5') or symbol.startswith('6'):  # 上海
                df = ak.stock_zh_a_spot_em()
            else:  # 深圳
                df = ak.stock_zh_a_spot_em()

            stock = df[df['代码'] == symbol]
            if not stock.empty:
                return {
                    'code': symbol,
                    'name': stock['名称'].values[0],
                    'price': stock['最新价'].values[0],
                    'change_pct': stock['涨跌幅'].values[0],
                    'volume': stock['成交量'].values[0],
                    'turnover': stock['成交额'].values[0],
                }
        except Exception as e:
            print(f"获取 {symbol} 信息失败: {e}")
        return {}

    def get_etf_info(self, symbol: str) -> dict:
        """获取ETF信息"""
        try:
            # ETF实时行情
            df = ak.fund_etf_spot_em()
            etf = df[df['代码'] == symbol]
            if not etf.empty:
                return {
                    'code': symbol,
                    'name': etf['名称'].values[0],
                    'price': etf['最新价'].values[0],
                    'change_pct': etf['涨跌幅'].values[0],
                    'volume': etf['成交量'].values[0],
                    'turnover': etf['成交额'].values[0],
                }
        except Exception as e:
            print(f"获取ETF {symbol} 信息失败: {e}")
        return {}

    def get_kline(self, symbol: str, period: str = 'daily', days: int = 60) -> pd.DataFrame:
        """
        获取K线数据
        period: daily, weekly, monthly
        """
        try:
            end_date = datetime.now().strftime('%Y%m%d')
            start_date = (datetime.now() - timedelta(days=days)).strftime('%Y%m%d')

            if symbol.isdigit() and len(symbol) == 6:
                # A股
                df = ak.stock_zh_a_hist(
                    symbol=symbol,
                    period=period,
                    start_date=start_date,
                    end_date=end_date,
                    adjust="qfq"  # 前复权
                )
            else:
                print(f"不支持的代码格式: {symbol}")
                return pd.DataFrame()

            return df
        except Exception as e:
            print(f"获取K线数据失败: {e}")
            return pd.DataFrame()

    def get_financial(self, symbol: str) -> dict:
        """获取基本面数据"""
        try:
            # 财务指标
            df = ak.stock_financial_analysis_indicator(symbol=symbol)
            if not df.empty:
                latest = df.iloc[-1]
                return {
                    'pe': latest.get('市盈率', 0),
                    'pb': latest.get('市净率', 0),
                    'roe': latest.get('净资产收益率', 0),
                    'revenue_growth': latest.get('营业总收入同比增长', 0),
                    'profit_growth': latest.get('净利润同比增长', 0),
                }
        except Exception as e:
            print(f"获取财务数据失败: {e}")
        return {}

    def get_etf_holdings(self, symbol: str) -> list:
        """获取ETF持仓"""
        try:
            # 这里需要根据具体ETF获取持仓
            # 不同数据源接口不同，需要单独处理
            holdings = []
            # TODO: 实现ETF持仓获取
            return holdings
        except Exception as e:
            print(f"获取ETF持仓失败: {e}")
        return []


def analyze_example_513120():
    """分析示例: 港股创新药ETF 513120"""
    fetcher = StockDataFetcher()

    print("=" * 50)
    print("港股创新药ETF 513120 分析")
    print("=" * 50)

    # 获取ETF信息
    etf_info = fetcher.get_etf_info('513120')
    if etf_info:
        print(f"\n【基本信息】")
        print(f"代码: {etf_info['code']}")
        print(f"名称: {etf_info['name']}")
        print(f"最新价: {etf_info['price']}")
        print(f"涨跌幅: {etf_info['change_pct']:.2f}%")

    # 获取K线数据
    print(f"\n【技术分析】")
    kline = fetcher.get_kline('513120', days=60)
    if not kline.empty:
        latest = kline.iloc[-1]
        ma5 = kline['收盘'].tail(5).mean()
        ma20 = kline['收盘'].tail(20).mean()
        ma60 = kline['收盘'].tail(60).mean()

        print(f"收盘价: {latest['收盘']:.3f}")
        print(f"MA5: {ma5:.3f}")
        print(f"MA20: {ma20:.3f}")
        print(f"MA60: {ma60:.3f}")

        # 简单趋势判断
        if latest['收盘'] > ma5 > ma20 > ma60:
            trend = "多头排列，趋势向上"
        elif latest['收盘'] < ma5 < ma20 < ma60:
            trend = "空头排列，趋势向下"
        else:
            trend = "震荡整理，趋势不明"
        print(f"趋势: {trend}")

    print(f"\n【决策建议】")
    # TODO: 实现完整的决策逻辑


if __name__ == "__main__":
    # 安装依赖: pip install akshare pandas
    analyze_example_513120()
