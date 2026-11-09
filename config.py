"""全局配置：从 .env 读取数据库连接等敏感信息，避免明文密码提交到仓库。"""
import os

from dotenv import load_dotenv

load_dotenv()

# 数据库连接配置
DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": int(os.getenv("DB_PORT", "3306")),
    "user": os.getenv("DB_USER", "jr"),
    "password": os.getenv("DB_PASSWORD", ""),
    "database": os.getenv("DB_NAME", "device_monitor"),
    "charset": "utf8mb4",
}

# 连接池大小
DB_POOL_SIZE = int(os.getenv("DB_POOL_SIZE", "10"))

# 数据模拟脚本：判定"异常"的默认温度阈值（℃）
ABNORMAL_TEMP_THRESHOLD = float(os.getenv("ABNORMAL_TEMP_THRESHOLD", "38"))

# 数据模拟脚本：采样间隔（秒）
SIMULATE_INTERVAL = float(os.getenv("SIMULATE_INTERVAL", "2"))

# Flask 服务配置
FLASK_HOST = os.getenv("FLASK_HOST", "127.0.0.1")
FLASK_PORT = int(os.getenv("FLASK_PORT", "5000"))
FLASK_DEBUG = os.getenv("FLASK_DEBUG", "0") == "1"
