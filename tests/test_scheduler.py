"""
定时任务模块单元测试
测试交易时间判断和数据库操作
"""

import pytest
import os
import sys
import tempfile
from datetime import datetime, time

# 添加项目根目录到路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


class TestTradingHours:
    """交易时间判断测试"""

    def test_is_trading_hours_weekday_morning(self):
        """测试工作日上午9点"""
        from backend.scheduler_utils import is_trading_hours

        # 周一上午9点
        test_time = datetime(2026, 2, 14, 9, 0, 0)  # 周一
        assert is_trading_hours(test_time) is True

    def test_is_trading_hours_weekday_afternoon(self):
        """测试工作日下午2点"""
        from backend.scheduler_utils import is_trading_hours

        # 周三下午2点
        test_time = datetime(2026, 2, 12, 14, 0, 0)  # 周三
        assert is_trading_hours(test_time) is True

    def test_is_trading_hours_weekday_early_morning(self):
        """测试工作日上午8点（非交易时间）"""
        from backend.scheduler_utils import is_trading_hours

        test_time = datetime(2026, 2, 14, 8, 59, 59)  # 周一 8:59:59
        assert is_trading_hours(test_time) is False

    def test_is_trading_hours_weekday_after_close(self):
        """测试工作日下午3点及之后（非交易时间）"""
        from backend.scheduler_utils import is_trading_hours

        test_time = datetime(2026, 2, 14, 15, 0, 0)  # 周一 15:00:00
        assert is_trading_hours(test_time) is False

    def test_is_trading_hours_saturday(self):
        """测试周六（非交易日）"""
        from backend.scheduler_utils import is_trading_hours

        # 周六上午10点（虽然时间在9-15之间，但不是交易日）
        test_time = datetime(2026, 2, 15, 10, 0, 0)  # 周六
        assert is_trading_hours(test_time) is False

    def test_is_trading_hours_sunday(self):
        """测试周日（非交易日）"""
        from backend.scheduler_utils import is_trading_hours

        test_time = datetime(2026, 2, 16, 10, 0, 0)  # 周日
        assert is_trading_hours(test_time) is False


class TestDatabaseOperations:
    """数据库操作测试"""

    @pytest.fixture
    def temp_db(self):
        """创建临时数据库"""
        # 创建临时数据库文件
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
            temp_db_path = f.name

        # 导入并初始化数据库
        from backend.database import Database
        db = Database(temp_db_path)

        yield db

        # 清理
        os.unlink(temp_db_path)

    def test_database_initialization(self, temp_db):
        """测试数据库表创建"""
        import sqlite3

        conn = sqlite3.connect(temp_db.db_path)
        cursor = conn.cursor()

        # 检查表是否存在
        cursor.execute("""
            SELECT name FROM sqlite_master
            WHERE type='table'
            ORDER BY name
        """)

        tables = [row[0] for row in cursor.fetchall()]
        assert 'analyses' in tables
        assert 'scheduled_updates' in tables
        assert 'system_config' in tables

        conn.close()

    def test_save_and_get_analysis(self, temp_db):
        """测试保存和获取分析结果"""
        sample_analysis = {
            'symbol': '513120',
            'name': '港股创新药ETF',
            'current_price': 1.234,
            'change_pct': 2.5,
            'technical': {'score': 30, 'max_score': 40},
            'fundamental': {'score': 25, 'max_score': 40},
            'sentiment': {'score': 15, 'max_score': 20},
            'total_score': 70,
            'timestamp': '2026-02-14 10:30:00'
        }

        # 保存分析结果
        record_id = temp_db.save_analysis('513120', sample_analysis)
        assert record_id > 0

        # 获取最新分析结果
        retrieved = temp_db.get_latest_analysis('513120')
        assert retrieved is not None
        assert retrieved['symbol'] == '513120'
        assert retrieved['current_price'] == 1.234

    def test_get_all_symbols(self, temp_db):
        """测试获取所有标的"""
        # 添加多个标的
        for symbol in ['513120', '512690', '159915']:
            temp_db.save_analysis(symbol, {
                'symbol': symbol,
                'current_price': 1.0
            })

        # 获取所有标的
        symbols = temp_db.get_all_symbols()
        assert len(symbols) == 3
        assert '513120' in symbols
        assert '512690' in symbols
        assert '159915' in symbols

    def test_save_scheduled_update_log(self, temp_db):
        """测试保存定时任务日志"""
        run_time = datetime(2026, 2, 14, 10, 0, 0)

        record_id = temp_db.save_scheduled_update_log(
            run_time=run_time,
            is_trading_hours=True,
            symbols_updated=3,
            errors=None
        )

        assert record_id > 0

        # 获取日志
        logs = temp_db.get_scheduled_update_logs(limit=1)
        assert len(logs) == 1
        assert logs[0]['is_trading_hours'] is True
        assert logs[0]['symbols_updated'] == 3

    def test_config_operations(self, temp_db):
        """测试配置读写"""
        # 设置配置
        temp_db.set_config('test_key', 'test_value')

        # 获取配置
        value = temp_db.get_config('test_key')
        assert value == 'test_value'

        # 获取不存在的配置
        default_value = temp_db.get_config('non_existent_key', 'default')
        assert default_value == 'default'


class TestGetNextUpdateTime:
    """获取下次更新时间测试"""

    def test_next_update_same_day(self):
        """测试当天还有更新的情况"""
        from backend.scheduler_utils import get_next_update_time

        # 周一上午10点，下次应该是11点
        test_time = datetime(2026, 2, 14, 10, 0, 0)

        # Mock datetime.now() 返回固定时间
        import backend.scheduler_utils
        original_now = datetime.now
        datetime.now = lambda: test_time

        try:
            next_update = backend.scheduler_utils.get_next_update_time()
            assert next_update.hour == 11
            assert next_update.minute == 0
        finally:
            datetime.now = original_now

    def test_next_update_next_day(self):
        """测试当天没有更新的情况"""
        from backend.scheduler_utils import get_next_update_time

        # 周一下午2点半，今天没有更多更新，应该是明天9点
        test_time = datetime(2026, 2, 14, 14, 30, 0)

        import backend.scheduler_utils
        original_now = datetime.now
        datetime.now = lambda: test_time

        try:
            next_update = backend.scheduler_utils.get_next_update_time()
            assert next_update.day == 15  # 第二天
            assert next_update.hour == 9
            assert next_update.minute == 0
        finally:
            datetime.now = original_now


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
