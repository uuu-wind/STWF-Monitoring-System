#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试数据处理器的功能
"""

from data_processor import DataProcessor
from datetime import datetime

# 测试配置文件路径
config_file = "config.json"

# 创建数据处理器实例
processor = DataProcessor(config_file)

# 测试获取类配置
print("测试获取类配置:")
try:
    class_0_config = processor.get_class_config(0)
    print(f"类0配置: {class_0_config}")
    
    class_1_config = processor.get_class_config(1)
    print(f"类1配置: {class_1_config}")
except Exception as e:
    print(f"错误: {e}")

# 测试处理UDP数据
print("\n测试处理UDP数据:")

# 尝试导入真正的InfluxDBWriter
try:
    from influx_writer import InfluxDBWriter
    # 创建真正的InfluxDBWriter实例（仅用于测试，不会实际写入）
    influx_writer = InfluxDBWriter(
        host="http://localhost:8181",
        database="windfarm",
        token= "apiv3_q7RPi0zeY1bWYCuPnbgrlMZSvyGqXHzhJ8iFhLQBZdIxk3CFuxSqerS89l6GdeQMGgM0ICCPYB42oiOszt1l4Q"
    )
    print("使用真正的InfluxDBWriter")
except ImportError:
    # 模拟一个InfluxDBWriter类，用于测试
    class MockInfluxDBWriter:
        def write_data(self, measurement, tags=None, fields=None, time=None):
            print(f"模拟写入数据:")
            print(f"  测量: {measurement}")
            print(f"  标签: {tags}")
            print(f"  字段: {fields}")
            print(f"  时间: {time}")
            return True
    
    # 创建模拟的InfluxDBWriter实例
    influx_writer = MockInfluxDBWriter()
    print("使用模拟的InfluxDBWriter")

# 模拟UDP数据
# 格式: [1, 0, turbine_id, class_id, channel_0_high, channel_0_low, channel_1_high, channel_1_low, ...]
recv_list = [1, 0, 123, 1, 0x01, 0x23, 0x04, 0x56, 0x07, 0x89, 0xAB, 0xCD, 0xEF, 0x01, 0x23, 0x45, 0x67, 0x89]

# 测试处理数据
recv_time = datetime.now()
success = processor.process_udp_data(influx_writer, recv_list, recv_time)
print(f"处理结果: {'成功' if success else '失败'}")

print("\n测试完成!")
