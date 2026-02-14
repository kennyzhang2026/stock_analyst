"""
定时任务工具函数
包含交易时间判断、标的列表管理等
"""

import os
from datetime import datetime, time
from typing import List, Optional


def is_trading_hours(check_time: Optional[datetime] = None) -> bool:
    """
    判断当前时间是否在交易时间内

    交易时间定义:
    - 交易日: 周一至周五 (0=周一, 6=周日)
    - 交易时段: 09:00-15:00

    Args:
        check_time: 要检查的时间，如果为None则使用当前时间

    Returns:
        True如果在交易时间内，否则为False
    """
    if check_time is None:
        check_time = datetime.now()

    # 检查是否为工作日 (周一=0, 周五=4)
    if check_time.weekday() >= 5:
        return False

    # 检查是否在交易时段 09:00-15:00
    current_time = check_time.time()
    return time(9, 0) <= current_time < time(15, 0)


def get_scheduled_symbols() -> List[str]:
    """
    获取需要定时更新的标的列表

    当前实现: 从数据库中获取所有有分析记录的标的
    也可以从配置文件或系统配置中读取

    Returns:
        标的代码列表
    """
    try:
        from .database import db
        symbols = db.get_all_symbols()
        return symbols if symbols else []
    except Exception as e:
        print(f"[{get_current_time()}] 获取定时标的列表失败: {e}")
        return []


def get_current_time() -> str:
    """
    获取格式化的当前时间字符串

    Returns:
        格式为 YYYY-MM-DD HH:MM:SS 的时间字符串
    """
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def log_scheduled_update(
    is_trading_hours: bool,
    symbols_updated: int = 0,
    errors: Optional[str] = None
) -> None:
    """
    记录定时更新日志到数据库和控制台

    Args:
        is_trading_hours: 是否在交易时间
        symbols_updated: 成功更新的标的数量
        errors: 错误信息（如果有）
    """
    run_time = datetime.now()
    time_str = get_current_time()

    # 控制台输出
    if is_trading_hours:
        status_msg = f"[{time_str}] 交易时间更新完成 - 更新 {symbols_updated} 个标的"
        if errors:
            status_msg += f" | 错误: {errors}"
        print(status_msg)
    else:
        print(f"[{time_str}] 非交易时间，跳过更新")

    # 保存到数据库
    try:
        from .database import db
        db.save_scheduled_update_log(
            run_time=run_time,
            is_trading_hours=is_trading_hours,
            symbols_updated=symbols_updated,
            errors=errors
        )
    except Exception as e:
        print(f"[{time_str}] 保存日志到数据库失败: {e}")


def get_next_update_time() -> Optional[datetime]:
    """
    获取下一次定时更新时间

    Returns:
        下次更新时间，如果今天没有更多更新则返回None
    """
    now = datetime.now()

    # 如果是周末，返回下周一9:00
    if now.weekday() >= 5:
        days_until_monday = (7 - now.weekday()) % 7 or 7
        next_update = now.replace(hour=9, minute=0, second=0, microsecond=0)
        return next_update.replace(day=now.day + days_until_monday)

    # 检查今天是否还有更新时间点
    scheduled_hours = list(range(9, 15))  # 9, 10, 11, 12, 13, 14
    current_hour = now.hour

    for hour in scheduled_hours:
        if hour > current_hour or (hour == current_hour and now.minute == 0):
            return now.replace(hour=hour, minute=0, second=0, microsecond=0)

    # 今天没有更多更新，返回明天9:00
    tomorrow = now.replace(day=now.day + 1, hour=9, minute=0, second=0, microsecond=0)
    return tomorrow


def format_time_until_update(update_time: datetime) -> str:
    """
    格式化距离下次更新的时间

    Args:
        update_time: 下次更新时间

    Returns:
        格式化的时间字符串，如 "2小时30分钟后"
    """
    now = datetime.now()
    delta = update_time - now

    hours = int(delta.total_seconds() // 3600)
    minutes = int((delta.total_seconds() % 3600) // 60)

    if hours > 0 and minutes > 0:
        return f"{hours}小时{minutes}分钟后"
    elif hours > 0:
        return f"{hours}小时后"
    else:
        return f"{minutes}分钟后"


# 用于SSE通知的全局变量
_last_update_notification = None


def notify_update():
    """设置更新通知标志"""
    global _last_update_notification
    _last_update_notification = datetime.now()


def has_new_update(since: Optional[datetime] = None) -> bool:
    """
    检查是否有新的更新

    Args:
        since: 检查的起始时间，如果为None则使用上次通知时间

    Returns:
        True如果有新更新
    """
    global _last_update_notification
    if since is None:
        since = _last_update_notification
    return _last_update_notification is not None and (
        since is None or _last_update_notification > since
    )
