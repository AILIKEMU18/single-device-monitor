import pymysql
import random
import datetime
import time
def co():
    conn=pymysql.connect(
            host='localhost',
            user='jr',
            password='123456',
            database='device_monitor',
            charset='utf8mb4'
            )
    return conn
if __name__ == '__main__':
    conn=co()
    cursor=conn.cursor()
try:
    while True:
        temperature=random.uniform(35,42)
        pressure=random.uniform(100,110)
        collect_time=datetime.datetime.now()
        if temperature>38:
            status="异常"
        else:
            status="正常"
            sql="insert into device_datas(device_id,temperature,pressure,collect_time,status)values(%s,%s,%s,%s,%s)"
            params=(1,temperature,pressure,collect_time,status)
            cursor.execute(sql,params)
            conn.commit()
            print(f"成功插入：温度{temperature:.2f},压力{pressure:.2f},状态{status}")
            time.sleep(2)
except Exception as e:
    print("出错了：",e)
    conn.rollback()
finally:
    cursor.close()
    conn.close()

