"""模拟传感器采集数据并写入 MySQL。

修复记录：
- 原 bug：insert 语句缩进在 else 分支内，导致"异常"数据永远不会入库，
  且异常分支没有 sleep 会空转。现在每条数据都会入库。
- 逻辑封装为 run() 函数，支持 KeyboardInterrupt 优雅退出。
"""
import datetime
import random
import time

from config import ABNORMAL_TEMP_THRESHOLD, SIMULATE_INTERVAL
from db import get_cursor

DEVICE_ID = 1
INSERT_SQL = (
    "insert into device_datas(device_id, temperature, pressure, collect_time, status) "
    "values (%s, %s, %s, %s, %s)"
)


def generate_record(device_id=DEVICE_ID):
    """生成一条模拟采集记录：(device_id, temperature, pressure, collect_time, status)。"""
    temperature = round(random.uniform(35, 42), 2)
    pressure = round(random.uniform(100, 110), 2)
    collect_time = datetime.datetime.now()
    status = "异常" if temperature > ABNORMAL_TEMP_THRESHOLD else "正常"
    return (device_id, temperature, pressure, collect_time, status)


def run(interval=SIMULATE_INTERVAL, rounds=None):
    """持续模拟采集并入库。

    Args:
        interval: 每条数据间隔秒数
        rounds: 采集条数上限，None 表示一直运行（Ctrl+C 退出）
    """
    count = 0
    try:
        while rounds is None or count < rounds:
            record = generate_record()
            with get_cursor(commit=True) as cur:
                cur.execute(INSERT_SQL, record)
            count += 1
            print(f"第{count}条 已插入：温度 {record[1]:.2f}℃，压力 {record[2]:.2f}，状态 {record[4]}")
            time.sleep(interval)
    except KeyboardInterrupt:
        print(f"\n手动停止，共插入 {count} 条数据")
    except Exception as e:
        print(f"插入失败：{e}")
        raise


if __name__ == "__main__":
    run()
