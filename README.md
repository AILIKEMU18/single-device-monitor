# 单设备传感器数据监控平台

> Python + Flask + MySQL 实现的工业传感器数据监控后端：模拟采集 → 入库 → 多维查询 → 报表导出 → Web API。

## 项目功能

1. **数据模拟采集**：Python 脚本持续生成温度（35~42℃）、压力（100~110）数据并写入 MySQL，超阈值自动标记"异常"
2. **统计查询**：温度极值/均值统计、按设备聚合统计（JOIN + GROUP BY）、异常数据筛选、按时间范围查询、温度超标查询
3. **CSV 报表导出**：内存级 StringIO 生成，`utf-8-sig` 编码，Excel 直接打开不乱码
4. **Flask RESTful API**：统一 JSON 格式 `{code, msg, data}`、正确的 HTTP 状态码、全局异常捕获、参数校验
5. **工程化**：DBUtils 连接池、.env 环境变量管理敏感配置、参数化查询防 SQL 注入

## 项目结构

```
single-device-monitor/
├── schema.sql          # 建库建表脚本（devices 设备表 + device_datas 数据表 + 索引）
├── config.py           # 配置加载（从 .env 读取，敏感信息不入库）
├── db.py               # DBUtils PooledDB 连接池 + 上下文管理器
├── device_insert.py    # 数据模拟采集脚本
├── device_status.py    # 查询层（统计 / 异常筛选 / 时间范围 / 阈值超标）
├── app.py              # Flask 接口层
├── requirements.txt    # 依赖清单
├── .env.example        # 环境变量模板（复制为 .env 使用）
└── db_test.py          # 数据库连通性自检脚本
```

## 快速开始

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 建库建表（MySQL 中执行）
mysql -u<用户名> -p < schema.sql

# 3. 配置环境变量
cp .env.example .env   # 编辑 .env 填入数据库账号密码

# 4. 启动数据模拟采集（Ctrl+C 优雅退出）
python device_insert.py

# 5. 启动 Flask 服务
python app.py
```

## API 一览

| 方法 | 路径 | 说明 |
|---|---|---|
| GET | `/api/stat` | 全局统计：温度最大/最小/均值、总数、异常数 |
| GET | `/api/stat/devices` | 按设备聚合统计（JOIN devices + GROUP BY） |
| GET | `/api/error_list?limit=100` | 异常数据列表（按时间倒序） |
| GET | `/api/records?start_time=2026-10-16&end_time=2026-10-22&only_error=0` | 按时间范围查询 |
| GET | `/api/records/over?threshold=38` | 温度超标查询（不传 threshold 则按设备配置阈值） |
| GET | `/api/download_err` | 异常数据 CSV 下载 |
| GET | `/api/download_all` | 全量数据 CSV 下载 |
| GET | `/api/download_time?start_time=...&end_time=...` | 按时间范围导出 CSV |

返回格式统一为：

```json
{"code": 200, "msg": "ok", "data": []}
```

## 技术栈

Python 3 / Flask / pymysql / DBUtils 连接池 / MySQL / WSL-Linux / Git

## 排障记录（踩坑笔记）

- **异常数据不入库**：insert 语句缩进在 else 分支内导致"异常"记录被静默丢弃，且该分支缺少 sleep 造成空转——修复后每条数据均入库
- **聚合空值崩溃**：空表时 `MAX/MIN/AVG` 返回 NULL，格式化输出抛 `NoneType` 异常——增加空表判断
- **Excel 中文乱码**：CSV 用 `utf-8-sig`（带 BOM）编码解决
- **BETWEEN 边界遗漏**：`end_time` 传日期时只覆盖到当天 0 点——改为 `>= start AND < end` 语义
