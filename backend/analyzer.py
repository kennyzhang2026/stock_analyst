"""
分析模块
实现简化版评分算法：技术面(40) + 基本面(40) + 情绪面(20)
"""

from typing import Dict, List, Tuple
import pandas as pd


class Analyzer:
    """股票/ETF分析器"""

    def __init__(self):
        self.missing_analysis = []  # 记录缺失的分析项
        self.warnings = []  # 风险提示

    def analyze_technical(self, spot: Dict, ma20: float, year_high_low: Dict,
                          day5_change: float) -> Dict:
        """
        技术面分析 (40分)

        指标：
        1. 趋势方向 (15分) - 当前价 vs MA20
        2. 位置高低 (15分) - 在年内高低点的位置
        3. 短期动量 (10分) - 近5日涨跌幅
        """
        scores = {}
        reasons = []
        current_price = spot.get('price', 0)

        # 1. 趋势方向 (15分)
        if ma20 > 0:
            ratio = (current_price - ma20) / ma20 * 100
            if ratio > 2:  # MA20上方超过2%
                scores['trend'] = 15
                reasons.append(f"价格在MA20上方 {ratio:.1f}%，趋势向上")
            elif ratio > -2:  # MA20附近±2%
                scores['trend'] = 10
                reasons.append(f"价格在MA20附近 ({ratio:.1f}%)，震荡整理")
            else:  # MA20下方超过2%
                scores['trend'] = 5
                reasons.append(f"价格在MA20下方 {abs(ratio):.1f}%，趋势偏弱")
        else:
            scores['trend'] = 0
            reasons.append("⚠️ 无法计算MA20，数据不足")
            self.missing_analysis.append("趋势方向分析（MA20数据不足）")

        # 2. 位置高低 (15分)
        high = year_high_low.get('high', 0)
        low = year_high_low.get('low', 0)

        if high > 0 and low > 0:
            position = (current_price - low) / (high - low) * 100 if high != low else 50

            if position < 20:  # 接近年内低点
                scores['position'] = 15
                reasons.append(f"处于年内低位 ({position:.0f}%分位)，安全边际高")
            elif position < 50:  # 中下半区
                scores['position'] = 10
                reasons.append(f"处于年内中低位 ({position:.0f}%分位)")
            elif position < 80:  # 中上半区
                scores['position'] = 5
                reasons.append(f"处于年内中高位 ({position:.0f}%分位)")
            else:  # 接近年内高点
                scores['position'] = 0
                reasons.append(f"处于年内高位 ({position:.0f}%分位)，追高风险大")
        else:
            scores['position'] = 0
            reasons.append("⚠️ 无法判断年内高低点")
            self.missing_analysis.append("位置高低分析（年内高低点数据不足）")

        # 3. 短期动量 (10分)
        if day5_change != 0:
            if day5_change > 5:
                scores['momentum'] = 10
                reasons.append(f"近5日上涨 {day5_change:.1f}%，动能强劲")
            elif day5_change > 0:
                scores['momentum'] = 5
                reasons.append(f"近5日上涨 {day5_change:.1f}%，动能一般")
            elif day5_change > -5:
                scores['momentum'] = 3
                reasons.append(f"近5日下跌 {abs(day5_change):.1f}%，动能偏弱")
            else:
                scores['momentum'] = 0
                reasons.append(f"近5日下跌 {abs(day5_change):.1f}%，动能疲弱")
        else:
            scores['momentum'] = 5
            reasons.append("近5日数据不足，动量分析中性")

        technical_score = sum(scores.values())
        max_score = 40

        return {
            'score': technical_score,
            'max_score': max_score,
            'detail': scores,
            'reasons': reasons
        }

    def analyze_fundamental(self, spot: Dict, year_high_low: Dict,
                           is_etf: bool = True) -> Dict:
        """
        基本面分析 (40分)

        MVP阶段针对ETF简化：
        1. 估值水平 (20分) - 用从高点回撤幅度估算
        2. 板块景气 (20分) - 固定评分（可后续调整）
        """
        scores = {}
        reasons = []
        current_price = spot.get('price', 0)

        # 1. 估值水平 (20分) - 用回撤幅度估算
        high = year_high_low.get('high', 0)

        if high > 0 and current_price > 0:
            drawdown = (high - current_price) / high * 100

            if drawdown > 50:
                scores['valuation'] = 20
                reasons.append(f"从高点回撤 {drawdown:.0f}%，估值处于历史低位")
            elif drawdown > 30:
                scores['valuation'] = 15
                reasons.append(f"从高点回撤 {drawdown:.0f}%，估值偏低")
            elif drawdown > 15:
                scores['valuation'] = 10
                reasons.append(f"从高点回撤 {drawdown:.0f}%，估值中性")
            else:
                scores['valuation'] = 5
                reasons.append(f"从高点回撤 {drawdown:.0f}%，估值偏高")
        else:
            scores['valuation'] = 10
            reasons.append("⚠️ 无法计算历史高点，估值评分中性")
            self.missing_analysis.append("估值水平分析（历史高点数据不足）")

        # 2. 板块景气 (20分) - MVP阶段固定评分，后续可调整
        # 对于港股创新药ETF，给予中等偏上的评分
        # 可以根据用户持有的不同ETF设置不同分数
        scores['sentiment'] = 15
        reasons.append("创新药长期逻辑清晰（老龄化+国产替代），但短期有政策波动")

        fundamental_score = sum(scores.values())

        return {
            'score': fundamental_score,
            'max_score': 40,
            'detail': scores,
            'reasons': reasons
        }

    def analyze_sentiment(self, volume_trend: str, day5_change: float) -> Dict:
        """
        情绪面分析 (20分)

        指标：
        1. 资金流向 (20分) - 近5日涨跌 + 量能配合
        """
        reasons = []

        if volume_trend == 'up':  # 放量上涨
            score = 20
            reasons.append(f"放量上涨，资金流入积极")
        elif volume_trend == 'up_low_volume' and day5_change > 0:  # 缩量上涨
            score = 10
            reasons.append(f"缩量上涨，资金追涨意愿谨慎")
        elif volume_trend == 'down':
            score = 5
            reasons.append(f"资金流出或观望情绪浓")
        else:
            score = 10
            reasons.append(f"市场情绪中性")

        return {
            'score': score,
            'max_score': 20,
            'reasons': reasons
        }

    def get_recommendation(self, total_score: int, spot: Dict) -> Dict:
        """
        根据总分给出操作建议

        风险偏好：中长期，可接受一定损失，低吸高卖
        """
        # 低位时更积极
        if total_score >= 70:
            action = "买入 / 增持"
            color = "green"
            level = 1
        elif total_score >= 50:
            action = "持有"
            color = "yellow"
            level = 2
        elif total_score >= 30:
            action = "观望 / 轻仓"
            color = "orange"
            level = 3
        else:
            action = "卖出 / 减持"
            color = "red"
            level = 4

        # 添加风险提示
        if '创新药' in spot.get('name', ''):
            self.warnings.append("⚠️ 高波动品种：创新药ETF波动较大，注意仓位控制")

        return {
            'action': action,
            'color': color,
            'level': level,
            'total_score': total_score
        }

    def analyze(self, symbol: str, spot: Dict, kline_data: pd.DataFrame,
                ma20: float, year_high_low: Dict, day5_change: float,
                volume_trend: str) -> Dict:
        """
        综合分析

        Returns:
            完整的分析结果
        """
        self.missing_analysis = []
        self.warnings = []

        # 三维分析
        technical = self.analyze_technical(spot, ma20, year_high_low, day5_change)
        fundamental = self.analyze_fundamental(spot, year_high_low, is_etf=True)
        sentiment = self.analyze_sentiment(volume_trend, day5_change)

        # 计算总分
        total_score = technical['score'] + fundamental['score'] + sentiment['score']

        # 获取建议
        recommendation = self.get_recommendation(total_score, spot)

        # 汇总理由
        all_reasons = []
        all_reasons.extend([f"技术面: {r}" for r in technical['reasons']])
        all_reasons.extend([f"基本面: {r}" for r in fundamental['reasons']])
        all_reasons.extend([f"情绪面: {r}" for r in sentiment['reasons']])

        return {
            'symbol': symbol,
            'name': spot.get('name', ''),
            'current_price': spot.get('price', 0),
            'change_pct': spot.get('change_pct', 0),
            'timestamp': spot.get('timestamp', ''),
            'technical': technical,
            'fundamental': fundamental,
            'sentiment': sentiment,
            'total_score': total_score,
            'recommendation': recommendation,
            'reasons': all_reasons,
            'missing_analysis': self.missing_analysis.copy(),
            'warnings': self.warnings.copy()
        }

    def get_score_display(self, score: int, max_score: int) -> str:
        """格式化分数显示"""
        return f"{score}/{max_score}"
