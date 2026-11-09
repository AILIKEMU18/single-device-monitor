"""查询层：所有业务 SQL 集中在这里，供命令行脚本和 Flask 接口共用。

设计要点：
- 全部使用参数化查询（%s），防止 SQL 注入
- 统一走 db.get_cursor 连接池，异常时连接自动归还
- 时间范围查询做了参数校验和日期边界处理
- 多表查询：device_datas JOIN devices，异常判定以 devices.temp_threshold 为准
"""
import datetime

from db import get_cursor

ERR_STATUS = "异常"        # 状态字符串集中定义，避免魔法字符串散落各处
OK_STATUS = "正常"


def _parse_dt(value, name):
    """解析时间参数，支持 'YYYY-MM-DD' 和 'YYYY-MM-DD HH:MM:SS' 两种格式。"""
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{name} 不能为空")
    text = value.strip()
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d"):
        try:
            return datetime.datetime.strptime(text, fmt)
        except ValueError:
            continue
    raise ValueError(f"{name} 时间格式错误，应为 YYYY-MM-DD 或 YYYY-MM-DD HH:MM:SS")


def temperature_stat():
    """全局温度统计：极值、均值（保留两位小数）、总数、异常数。

    空表时返回 None，由调用方决定提示语。
    """
    sql = (
        "select max(temperature) as max_tem, min(temperature) as min_tem, "
        "round(avg(temperature), 2) as avg_tem, count(*) as total, "
        "sum(status = %s) as err_total from device_datas"
    )
    with get_cursor(dictionary=True) as cur:
        cur.execute(sql, (ERR_STATUS,))
        row = cur.fetchone()
    if row is None or row["total"] == 0:
        return None
    return row


def stat_by_device():
    """按设备聚合统计（JOIN + GROUP BY），体现多表聚合。"""
    sql = (
        "select v.id as device_id, v.device_name, v.temp_threshold, "
        "max(d.temperature) as max_tem, min(d.temperature) as min_tem, "
        "round(avg(d.temperature), 2) as avg_tem, count(*) as total, "
        "sum(d.status = %s) as err_total "
        "from device_datas d join devices v on d.device_id = v.id "
        "group by v.id, v.device_name, v.temp_threshold "
        "order by v.id"
    )
    with get_cursor(dictionary=True) as cur:
        cur.execute(sql, (ERR_STATUS,))
        return cur.fetchall()


def error_list(limit=100):
    """异常数据列表，按时间倒序，limit 防止全表返回。"""
    sql = (
        "select d.id, d.device_id, v.device_name, d.temperature, d.pressure, "
        "d.collect_time, d.status "
        "from device_datas d join devices v on d.device_id = v.id "
        "where d.status = %s order by d.collect_time desc limit %s"
    )
    with get_cursor(dictionary=True) as cur:
        cur.execute(sql, (ERR_STATUS, int(limit)))
        return cur.fetchall()


def error_count():
    """异常记录总数；无数据返回 0。"""
    sql = "select count(*) as cnt from device_datas where status = %s"
    with get_cursor(dictionary=True) as cur:
        cur.execute(sql, (ERR_STATUS,))
        return cur.fetchone()["cnt"]


def list_all(limit=1000):
    """全量数据（限制条数），按时间正序。"""
    sql = (
        "select d.id, d.device_id, v.device_name, d.temperature, d.pressure, "
        "d.collect_time, d.status "
        "from device_datas d join devices v on d.device_id = v.id "
        "order by d.collect_time limit %s"
    )
    with get_cursor(dictionary=True) as cur:
        cur.execute(sql, (int(limit),))
        return cur.fetchall()


def list_by_time(start_time, end_time, only_error=False, limit=1000):
    """按时间范围查询。

    - 支持传日期（自动取整点边界）或完整时间
    - 边界用 >= start 且 < end，避免 BETWEEN 在 end 为日期时漏掉当天数据
    - only_error=True 时只返回异常数据
    """
    start_dt = _parse_dt(start_time, "start_time")
    end_dt = _parse_dt(end_time, "end_time")
    if start_dt >= end_dt:
        raise ValueError("start_time 必须早于 end_time")

    sql = (
        "select d.id, d.device_id, v.device_name, d.temperature, d.pressure, "
        "d.collect_time, d.status "
        "from device_datas d join devices v on d.device_id = v.id "
        "where d.collect_time >= %s and d.collect_time < %s"
    )
    params = [start_dt, end_dt]
    if only_error:
        sql += " and d.status = %s"
        params.append(ERR_STATUS)
    sql += " order by d.collect_time limit %s"
    params.append(int(limit))

    with get_cursor(dictionary=True) as cur:
        cur.execute(sql, params)
        return cur.fetchall()


def list_over_threshold(threshold=None):
    """温度超标查询。

    Args:
        threshold: 指定阈值；为 None 时使用各设备在 devices 表中配置的阈值
                   （JOIN 实现按设备阈值判超标）。
    """
    if threshold is not None:
        threshold = float(threshold)
        sql = (
            "select d.id, d.device_id, v.device_name, d.temperature, d.pressure, "
            "d.collect_time, d.status, %s as threshold "
            "from device_datas d join devices v on d.device_id = v.id "
            "where d.temperature > %s order by d.temperature desc limit 500"
        )
        params = (threshold, threshold)
    else:
        sql = (
            "select d.id, d.device_id, v.device_name, d.temperature, d.pressure, "
            "d.collect_time, d.status, v.temp_threshold as threshold "
            "from device_datas d join devices v on d.device_id = v.id "
            "where d.temperature > v.temp_threshold "
            "order by d.temperature desc limit 500"
        )
        params = ()

    with get_cursor(dictionary=True) as cur:
        cur.execute(sql, params)
        return cur.fetchall()
