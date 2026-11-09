-- ============================================================
-- 单设备传感器数据监控平台 - 建库建表脚本
-- 使用方法：mysql -u<用户> -p < schema.sql
-- ============================================================

CREATE DATABASE IF NOT EXISTS device_monitor
    DEFAULT CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE device_monitor;

-- 设备信息表（设备台账）
CREATE TABLE IF NOT EXISTS devices (
    id            INT PRIMARY KEY AUTO_INCREMENT COMMENT '设备ID',
    device_name   VARCHAR(50)  NOT NULL COMMENT '设备名称',
    device_model  VARCHAR(50)  DEFAULT NULL COMMENT '设备型号',
    location      VARCHAR(100) DEFAULT NULL COMMENT '安装位置',
    temp_threshold DECIMAL(5,2) NOT NULL DEFAULT 38.00 COMMENT '温度报警阈值(℃)',
    created_at    DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间'
) ENGINE=InnoDB COMMENT='设备信息表';

-- 传感器采集数据表
CREATE TABLE IF NOT EXISTS device_datas (
    id           BIGINT PRIMARY KEY AUTO_INCREMENT COMMENT '记录ID',
    device_id    INT   NOT NULL COMMENT '设备ID（关联 devices.id）',
    temperature  DECIMAL(5,2) NOT NULL COMMENT '温度(℃)',
    pressure     DECIMAL(5,2) NOT NULL COMMENT '压力',
    collect_time DATETIME NOT NULL COMMENT '采集时间',
    status       VARCHAR(10) NOT NULL COMMENT '状态：正常/异常',
    KEY idx_device_time (device_id, collect_time),
    KEY idx_status (status),
    CONSTRAINT fk_datas_device FOREIGN KEY (device_id) REFERENCES devices (id)
) ENGINE=InnoDB COMMENT='传感器采集数据表';

-- 初始化一台演示设备
INSERT INTO devices (id, device_name, device_model, location, temp_threshold)
VALUES (1, '1号温度传感器', 'TMP-SIM-01', '车间A区', 38.00)
ON DUPLICATE KEY UPDATE device_name = VALUES(device_name);
