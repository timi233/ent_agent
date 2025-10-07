from datetime import datetime, timezone

def now_utc() -> datetime:
    """
    获取带时区的UTC当前时间对象
    使用统一入口，便于后续集中管理与替换
    """
    return datetime.now(timezone.utc)