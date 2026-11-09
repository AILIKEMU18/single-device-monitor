"""Flask 接口层。

设计要点：
- 全局异常捕获：所有未处理异常统一返回 JSON 500，参数校验错误返回 400
- JSON 返回格式统一为 {code, msg, data}，且携带正确的 HTTP 状态码
- CSV 导出统一走 _csv_response，带 None 保护，utf-8-sig 兼容 Excel
- debug 开关、监听地址、端口全部从 .env 读取，不再写死
"""
import csv
from io import StringIO

from flask import Flask, jsonify, make_response, request

import device_status as ds
from config import FLASK_DEBUG, FLASK_HOST, FLASK_PORT

app = Flask(__name__)

CSV_FIELDS = ["id", "device_id", "device_name", "temperature", "pressure",
              "collect_time", "status"]


def ok(data=None, msg="ok"):
    return jsonify({"code": 200, "msg": msg, "data": data})


def fail(msg, http_status=500, code=None):
    return jsonify({"code": code or http_status, "msg": msg, "data": None}), http_status


def _csv_response(rows, filename):
    """把查询结果打包成 CSV 下载响应（utf-8-sig 保证 Excel 打开不乱码）。"""
    if rows is None:
        rows = []
    output = StringIO()
    writer = csv.DictWriter(output, fieldnames=CSV_FIELDS, extrasaction="ignore")
    writer.writeheader()
    writer.writerows(rows)
    resp = make_response(output.getvalue().encode("utf-8-sig"))
    resp.headers["Content-Disposition"] = f"attachment; filename={filename}"
    resp.headers["Content-Type"] = "text/csv; charset=utf-8"
    return resp


# ---------------- 全局异常处理 ----------------

@app.errorhandler(ValueError)
def handle_value_error(e):
    """查询层的参数校验错误 -> 400。"""
    return fail(str(e), http_status=400)


@app.errorhandler(404)
def handle_404(e):
    return fail("接口不存在", http_status=404)


@app.errorhandler(Exception)
def handle_exception(e):
    """兜底异常处理：任何未捕获异常都不会让服务直接返回 HTML 错误页。"""
    app.logger.exception("服务器内部错误: %s", e)
    return fail("服务器内部错误", http_status=500)


# ---------------- 查询接口 ----------------

@app.route("/api/stat", methods=["GET"])
def api_stat():
    """全局统计：温度极值/均值 + 异常总数。"""
    stat_data = ds.temperature_stat()
    if stat_data is None:
        return ok(data={"max_tem": None, "min_tem": None, "avg_tem": None,
                        "total": 0, "err_total": 0}, msg="暂无数据")
    return ok({
        "max_tem": stat_data["max_tem"],
        "min_tem": stat_data["min_tem"],
        "avg_tem": stat_data["avg_tem"],
        "total": stat_data["total"],
        "err_total": stat_data["err_total"],
    })


@app.route("/api/stat/devices", methods=["GET"])
def api_stat_devices():
    """按设备聚合统计（JOIN devices + GROUP BY）。"""
    return ok(ds.stat_by_device())


@app.route("/api/error_list", methods=["GET"])
def api_error_list():
    """异常数据列表，可用 limit 参数控制条数（默认 100）。"""
    try:
        limit = int(request.args.get("limit", 100))
    except ValueError:
        return fail("limit 必须是整数", http_status=400)
    return ok(ds.error_list(limit=limit))


@app.route("/api/records", methods=["GET"])
def api_records():
    """按时间范围查询。参数：start_time、end_time、only_error（可选）。"""
    start_time = request.args.get("start_time")
    end_time = request.args.get("end_time")
    only_error = request.args.get("only_error", "0") == "1"
    rows = ds.list_by_time(start_time, end_time, only_error=only_error)
    return ok(rows)


@app.route("/api/records/over", methods=["GET"])
def api_records_over():
    """温度超标查询。参数：threshold（可选，不传则按各设备配置阈值判断）。"""
    threshold = request.args.get("threshold")
    return ok(ds.list_over_threshold(threshold))


# ---------------- CSV 下载接口 ----------------

@app.route("/api/download_err", methods=["GET"])
def api_download_err():
    """异常数据 CSV 导出。"""
    return _csv_response(ds.error_list(limit=100000), "err_data.csv")


@app.route("/api/download_all", methods=["GET"])
def api_download_all():
    """全量数据 CSV 导出。"""
    return _csv_response(ds.list_all(limit=100000), "all_datas.csv")


@app.route("/api/download_time", methods=["GET"])
def api_download_time():
    """按时间范围导出 CSV。参数同 /api/records。"""
    start_time = request.args.get("start_time")
    end_time = request.args.get("end_time")
    only_error = request.args.get("only_error", "0") == "1"
    rows = ds.list_by_time(start_time, end_time, only_error=only_error)
    return _csv_response(rows, "time_range_datas.csv")


if __name__ == "__main__":
    # debug 由 .env 控制，生产环境必须为 0；不再绑定 0.0.0.0 暴露调试器
    app.run(host=FLASK_HOST, port=FLASK_PORT, debug=FLASK_DEBUG)
