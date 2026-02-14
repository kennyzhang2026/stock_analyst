"""
SQLite数据库管理模块
用于存储分析结果和定时任务日志
"""

import os
import sqlite3
import json
from datetime import datetime
from typing import Optional, Dict, List, Any
from contextlib import contextmanager


# 数据库文件路径
DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'stock_analyst.db')


class Database:
    """SQLite数据库管理类"""

    def __init__(self, db_path: str = DB_PATH):
        """初始化数据库连接"""
        self.db_path = db_path
        self._init_database()

    @contextmanager
    def _get_connection(self):
        """获取数据库连接的上下文管理器"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def _init_database(self):
        """初始化数据库表结构"""
        with self._get_connection() as conn:
            cursor = conn.cursor()

            # 创建分析结果表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS analyses (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    symbol TEXT NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    data_json TEXT NOT NULL
                )
            """)

            # 创建索引
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_symbol_timestamp
                ON analyses (symbol, timestamp DESC)
            """)

            # 创建定时更新日志表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS scheduled_updates (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    run_time DATETIME NOT NULL,
                    is_trading_hours BOOLEAN NOT NULL,
                    symbols_updated INTEGER DEFAULT 0,
                    errors TEXT
                )
            """)

            # 创建索引
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_run_time
                ON scheduled_updates (run_time DESC)
            """)

            # 创建系统配置表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS system_config (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)

    def save_analysis(self, symbol: str, analysis: Dict[str, Any]) -> int:
        """
        保存分析结果

        Args:
            symbol: 标的代码
            analysis: 分析结果字典

        Returns:
            插入记录的ID
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO analyses (symbol, data_json)
                VALUES (?, ?)
                """,
                (symbol, json.dumps(analysis, ensure_ascii=False))
            )
            return cursor.lastrowid

    def get_latest_analysis(self, symbol: str) -> Optional[Dict[str, Any]]:
        """
        获取指定标的的最新分析结果

        Args:
            symbol: 标的代码

        Returns:
            最新分析结果字典，如果不存在则返回None
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT data_json FROM analyses
                WHERE symbol = ?
                ORDER BY timestamp DESC
                LIMIT 1
                """,
                (symbol,)
            )
            row = cursor.fetchone()
            if row:
                return json.loads(row['data_json'])
            return None

    def get_all_symbols(self) -> List[str]:
        """
        获取数据库中所有不重复的标的代码

        Returns:
            标的代码列表
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT DISTINCT symbol FROM analyses
                ORDER BY symbol
            """)
            return [row['symbol'] for row in cursor.fetchall()]

    def get_recent_analyses(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        获取最近的分析记录

        Args:
            limit: 返回记录数量

        Returns:
            分析记录列表
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT symbol, timestamp, data_json
                FROM analyses
                ORDER BY timestamp DESC
                LIMIT ?
                """,
                (limit,)
            )
            results = []
            for row in cursor.fetchall():
                results.append({
                    'symbol': row['symbol'],
                    'timestamp': row['timestamp'],
                    'data': json.loads(row['data_json'])
                })
            return results

    def save_scheduled_update_log(
        self,
        run_time: datetime,
        is_trading_hours: bool,
        symbols_updated: int = 0,
        errors: Optional[str] = None
    ) -> int:
        """
        保存定时任务执行日志

        Args:
            run_time: 执行时间
            is_trading_hours: 是否在交易时间
            symbols_updated: 成功更新的标的数量
            errors: 错误信息（如果有）

        Returns:
            插入记录的ID
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO scheduled_updates (run_time, is_trading_hours, symbols_updated, errors)
                VALUES (?, ?, ?, ?)
                """,
                (run_time.isoformat(), is_trading_hours, symbols_updated, errors)
            )
            return cursor.lastrowid

    def get_scheduled_update_logs(self, limit: int = 20) -> List[Dict[str, Any]]:
        """
        获取定时任务执行日志

        Args:
            limit: 返回记录数量

        Returns:
            日志记录列表
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT run_time, is_trading_hours, symbols_updated, errors
                FROM scheduled_updates
                ORDER BY run_time DESC
                LIMIT ?
                """,
                (limit,)
            )
            results = []
            for row in cursor.fetchall():
                results.append({
                    'run_time': row['run_time'],
                    'is_trading_hours': bool(row['is_trading_hours']),
                    'symbols_updated': row['symbols_updated'],
                    'errors': row['errors']
                })
            return results

    def get_config(self, key: str, default: Optional[str] = None) -> Optional[str]:
        """
        获取系统配置值

        Args:
            key: 配置键
            default: 默认值

        Returns:
            配置值
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT value FROM system_config WHERE key = ?
                """,
                (key,)
            )
            row = cursor.fetchone()
            return row['value'] if row else default

    def set_config(self, key: str, value: str) -> None:
        """
        设置系统配置值

        Args:
            key: 配置键
            value: 配置值
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT OR REPLACE INTO system_config (key, value, updated_at)
                VALUES (?, ?, CURRENT_TIMESTAMP)
                """,
                (key, value)
            )


# 全局数据库实例
db = Database()
