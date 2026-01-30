import json
import os
from influx_writer import InfluxDBWriter

class DataProcessor:
    def __init__(self, config_file_path):
        self.config_file_path = config_file_path
        self.config_data = self.load_config()
    
    def load_config(self):
        if not os.path.exists(self.config_file_path):
            raise FileNotFoundError(f"配置文件不存在: {self.config_file_path}")
        
        with open(self.config_file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def get_class_config(self, class_id):
        if str(class_id) not in self.config_data:
            raise ValueError(f"配置文件中不存在类ID: {class_id}")
        return self.config_data[str(class_id)]
    
    def process_udp_data(self, influx_writer, recv_list, recv_time):
        if len(recv_list) < 4:
            return False
        
        # 获取数据
        turbine_id = recv_list[2]
        class_id = recv_list[3]
        
        # 获取配置
        try:
            class_config = self.get_class_config(class_id)
        except ValueError as e:
            print(f"配置错误: {e}")
            return False
        
        database_name = class_config['database']
        channels = class_config['channels']
        
        # 提取8个通道的数据
        fields = {}
        for i in range(8):
            if i >= len(channels):
                break
            
            channel_config = channels[i]
            if not channel_config or 'column' not in channel_config:
                continue
            
            if channel_config['column'] == "":
                continue
            
            # 计算数据索引
            high_idx = 4 + i * 2
            low_idx = 5 + i * 2
            
            if high_idx >= len(recv_list) or low_idx >= len(recv_list):
                continue
            
            # 组合高低位数据
            high = recv_list[high_idx]
            low = recv_list[low_idx]
            value = (high << 8) | low
            
            # 应用数据范围
            if 'range' in channel_config:
                min_val = channel_config['range'].get('min', 0)
                max_val = channel_config['range'].get('max', 65535)
                value = value / 4096.0 * (max_val - min_val) + min_val
            
            fields[channel_config['column']] = value
        
        # 写入InfluxDB
        if fields:
            measurement = database_name
            tags = {
                "turbine_id": str(turbine_id)
            }
            
            return influx_writer.write_data(
                measurement=measurement,
                tags=tags,
                fields=fields,
                time=recv_time
            )
        
        return False

# 全局实例，方便udp_tool.py调用
_data_processor = None

def init_data_processor(config_file_path):
    global _data_processor
    _data_processor = DataProcessor(config_file_path)

def get_data_processor():
    return _data_processor

def process_udp_response(influx_writer, recv_list, recv_time):
    if _data_processor is None:
        print("数据处理器未初始化")
        return False
    
    return _data_processor.process_udp_data(influx_writer, recv_list, recv_time)
