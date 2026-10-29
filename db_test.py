import pymysql
conn=pymysql.connect(
        host='localhost',
        user='jr',
        password='123456',
        database='device_monitor',
        charset='utf8mb4'
)
cursor=conn.cursor()
sql='select * from device_datas;'
cursor.execute(sql)
results=cursor.fetchall()
for row in results:
    print(row)
cursor.close()
conn.close()
