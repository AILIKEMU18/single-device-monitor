from flask import Flask,jsonify,make_response
import csv
from io import StringIO
from device_status import co,tem,err,error_count,alldatas
app=Flask(__name__)
@app.route("/api/stat")
def api_stat():
    
    stat_data=tem()
    err_count=error_count()
    if stat_data is None or err_count is None:
        return jsonify({
            "code":500,
            "msg":"统计数据查询失败",
            "data":None
        })
    
    res={
            "code":200,
            "msg":"ok",
            "data":{

                "max_tem":stat_data["MAX"],
                "min_tem":stat_data["MIN"],
                "avg_tem":stat_data["AVG"],
                "err_total":err_count
            }
    }
    return jsonify(res)
@app.route("/api/error_list")
def api_error():
    
    error_list=err()
    if error_list is None:
        return jsonify({
            "code":500,
            "msg":"异常列表查询失败",
            "data":[]
        })
    
    res={
            "code":200,
            "msg":"ok",
            "data":error_list
        }
    return jsonify(res)
@app.route("/api/download_err")
def download_err():
    error_csv=err()
    output=StringIO()
    writer=csv.DictWriter(output,fieldnames=["id","device_id","temperature","pressure","collect_time","status"])
    writer.writeheader()
    writer.writerows(error_csv)
    resp=make_response(output.getvalue().encode("utf-8-sig"))
    resp.headers["Content-Disposition"]="attachment;filename=err_data.csv"
    resp.headers["Content-type"]="text/csv"
    return resp
@app.route("/api/download_alldatas")
def download_alldatas():
    alldatas_csv=alldatas()
    output=StringIO()
    writer=csv.DictWriter(output,fieldnames=["id","device_id","temperature","pressure","collect_time","status"])
    writer.writeheader()
    writer.writerows(alldatas_csv)
    resp=make_response(output.getvalue().encode("utf-8-sig"))
    resp.headers["Content-Disposition"]="attachment;filename=all_datas.csv"
    resp.headers["Content-type"]="text/csv"
    return resp

if __name__ == "__main__":
    app.run(host="0.0.0.0",port=5000,debug=True)


