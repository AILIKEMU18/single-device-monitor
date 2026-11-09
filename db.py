"""数据库访问层：基于 DBUtils PooledDB 的连接池 + 上下文管理器。

- 连接从池中获取，用完自动归还，避免频繁建立 TCP 连接
- 异常路径下连接也会归还，杜绝连接泄漏
- 所有查询统一走 get_cursor，DictCursor / 普通 Cursor 由参数控制
"""
from contextlib import contextmanager

import pymysql
from dbutils.pooled_db import PooledDB

from config import DB_CONFIG, DB_POOL_SIZE

_pool = None


def _get_pool():
    """懒加载全局连接池（单例）。"""
    global _pool
    if _pool is None:
        _pool = PooledDB(
            creator=pymysql,       # 底层驱动
            maxconnections=DB_POOL_SIZE,
            mincached=2,           # 初始化时空闲连接数
            maxcached=5,           # 池中最多缓存的空闲连接数
            blocking=True,         # 连接耗尽时等待而不是报错
            ping=1,                # 每次取连接时 ping 检活
            **DB_CONFIG,
        )
    return _pool


@contextmanager
def get_cursor(dictionary=False, commit=False):
    """获取一个游标，退出时自动关闭游标并归还连接。

    Args:
        dictionary: True 时返回 DictCursor（查询结果为 dict 列表）
        commit: True 时在正常退出前 commit（写操作使用）
    """
    conn = _get_pool().connection()
    try:
        cursor_class = pymysql.cursors.DictCursor if dictionary else pymysql.cursors.Cursor
        cur = conn.cursor(cursor_class)
        try:
            yield cur
            if commit:
                conn.commit()
        finally:
            cur.close()
    finally:
        conn.close()
