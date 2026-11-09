"""数据库连通性自检脚本：验证 .env 配置和连接池是否正常。"""
from db import get_cursor


def main():
    with get_cursor(dictionary=True) as cur:
        cur.execute("select version() as version, database() as db")
        row = cur.fetchone()
        print(f"连接成功：MySQL {row['version']}，当前库 {row['db']}")

        cur.execute("select count(*) as cnt from device_datas")
        print(f"device_datas 表共 {cur.fetchone()['cnt']} 条记录")

        cur.execute("select count(*) as cnt from devices")
        print(f"devices 表共 {cur.fetchone()['cnt']} 条记录")


if __name__ == "__main__":
    main()
