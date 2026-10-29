import pymysql
import csv
def co():
    conn=pymysql.connect(
            host='localhost',
            user='jr',
            password='123456',
            database='device_monitor',
            charset='utf8mb4'
    )
    return conn
def export_to_csv(data_list,file_name):
    headers=["id","device_id","temperature","pressure","collect_time","status"]
    with open(file_name,"w",encoding="utf-8-sig",newline="") as f:
        writer=csv.writer(f)
        writer.writerow(headers)
        writer.writerows(data_list)
        print(f"文件{file_name}导出成功")
def alldatas():
    try:
        conn=co()
        cursor=conn.cursor(pymysql.cursors.DictCursor)
        sql="select * from device_datas;"
        cursor.execute(sql)
        result=cursor.fetchall()
        for row in result:
            print(row)
        cursor.close()
        conn.close()
        return result
    except Exception as e:
        print("alldatas报错了: ",e)
        return None

def tem():
    try:
        conn=co()
        cursor=conn.cursor(pymysql.cursors.DictCursor)
        sql="select MAX(temperature)as MAX,MIN(temperature)as MIN,AVG(temperature)as AVG from device_datas;"
        cursor.execute(sql)
        result=cursor.fetchone()
        print(f"最高温度{result['MAX']:.2f}")
        print(f"最低温度{result['MIN']:.2f}")
        print(f"平均温度{result['AVG']:.2f}")
        cursor.close()
        conn.close()
        return result
    except Exception as e:
        print("tem报错: ",e)
        return None

def cor():
    try:
        conn=co()
        cursor=conn.cursor(pymysql.cursors.DictCursor)
        sql="select * from device_datas where status = '正常';"
        cursor.execute(sql)
        result=cursor.fetchall()
        for row in result:
            print(row)
        cursor.close()
        conn.close()
        return result
    except Exception as e:
        print("cor报错: ",e)
        return None
def err():
    try:
        conn=co()
        cursor=conn.cursor(pymysql.cursors.DictCursor)
        sql="select * from device_datas where status = '异常';"
        cursor.execute(sql)
        result=cursor.fetchall()
        for row in result:
            print(row)
        cursor.close()
        conn.close()
        return result
    except Exception as e:
        print("err报错: ",e)
        return None
def error_count():
    try:
        conn=co()
        cursor=conn.cursor(pymysql.cursors.DictCursor)
        sql="select count(*) as cnt from device_datas where status = '异常';"
        cursor.execute(sql)
        result=cursor.fetchone()
        print(f"异常记录有{result['cnt']}条")
        cursor.close()
        conn.close()
        return result["cnt"]
    except Exception as e:
        print("se报错了: ",e)
        return None
def error_datas():
    conn=co()
    cursor=conn.cursor()
    sql="select * from device_datas where status = '异常';"
    cursor.execute(sql)
    result=cursor.fetchall()
    export_to_csv(result,'error.csv')
    cursor.close()
    conn.close()


def all_datas():
    conn=co()
    cursor=conn.cursor()
    sql="select * from device_datas ;"
    cursor.execute(sql)
    result=cursor.fetchall()
    export_to_csv(result,"all_datas_csv")
    cursor.close()
    conn.close()
def selected_time(start_time,end_time,is_err=False,file_name="output.csv"):
    conn=co()
    cursor=conn.cursor()
    if is_err==True:
        sql="select*from device_datas where collect_time between %s And %s And status=%s;"
        param=(start_time,end_time,"异常")
    else:
        sql="select * from device_datas where collect_time between %s And %s;"
        param=(start_time,end_time)
    cursor.execute(sql,param)
    result=cursor.fetchall()
    export_to_csv(result,file_name)
    cursor.close()
    conn.close()

if __name__ == "__main__":

    tem()
    cor()
    err()
    error_count()
    error_datas()
    all_datas()
    alldatas()
    selected_time("2026-10-16 00:00:00","2026-10-22 00:00:00",is_err=False,file_name="all_time_datas.csv")
    


