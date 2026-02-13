import socket
from datetime import datetime

# 注释掉InfluxDB相关导入，以便在没有依赖的情况下测试
# from influx_writer import InfluxDBWriter

# 导入数据处理器
# 注释掉顶部导入，避免循环导入
# from data_processor import init_data_processor, process_udp_response

import multiprocessing

class UDPTool:
    def __init__(self, self_port, target_port, request_data=b"\xFF", recv_buffer_size=1024, recv_timeout=0.5,
                 influx_host="https://localhost:8181", influx_database="Wind", influx_token=None, config_file_path=None):
        self.self_port = self_port
        self.target_port = target_port
        self.request_data = request_data
        self.recv_buffer_size = recv_buffer_size
        self.recv_timeout = recv_timeout

        self.influx_host = influx_host
        self.influx_database = influx_database
        self.influx_token = influx_token
        self.config_file_path = config_file_path

        self.influx_writer = None
        self.scheduler = None  # 移到udp_receiver方法内部创建
        self.exit_event = None
        self.shared_udp_data = None

    def udp_receiver(self, exit_event, shared_udp_data):
        # 导入scheduler模块
        from apscheduler.schedulers.background import BackgroundScheduler
        
        # 导入数据处理器
        from data_processor import init_data_processor
        
        # 初始化数据处理器
        if self.config_file_path:
            init_data_processor(self.config_file_path)
            print(f"✅ 数据处理器初始化成功，配置文件: {self.config_file_path}")
        
        # 导入InfluxDBWriter
        try:
            from influx_writer import InfluxDBWriter
            # 初始化InfluxDBWriter
            self.influx_writer = InfluxDBWriter(
                host=self.influx_host,
                database=self.influx_database,
                token=self.influx_token
            )
            print(f"✅ InfluxDBWriter初始化成功，数据库: {self.influx_database}")
        except ImportError:
            print("⚠️ InfluxDBWriter导入失败，将使用模拟实现")
            # 创建模拟的InfluxDBWriter实例
            class MockInfluxDBWriter:
                def write_data(self, measurement, tags=None, fields=None, time=None):
                    print(f"模拟写入数据:")
                    print(f"  测量: {measurement}")
                    print(f"  标签: {tags}")
                    print(f"  字段: {fields}")
                    print(f"  时间: {time}")
                    return True
            self.influx_writer = MockInfluxDBWriter()
        
        # 在进程内部创建scheduler实例
        self.scheduler = BackgroundScheduler(timezone="Asia/Shanghai")
        self.scheduler.start()
        
        self.exit_event = exit_event
        self.shared_udp_data = shared_udp_data
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as recv_sock:
            recv_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            recv_sock.bind(("", self.self_port))
            recv_sock.settimeout(self.recv_timeout)
            print(f"启动接收进程，监听端口{self.self_port}")
            while not exit_event.is_set():
                try:
                    recv_data, (sender_ip, sender_port) = recv_sock.recvfrom(self.recv_buffer_size)
                    recv_time = datetime.now()
                    shared_udp_data[sender_ip] = {"recv_data": recv_data, "recv_time": recv_time}
                    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]}] "
                          f"✅ 收到回复 | 来源：{sender_ip}:{sender_port} | 数据：{recv_data.decode('utf-8', errors='ignore')}")
                    self.deal_recv_data(sender_ip, recv_data, recv_time)
                except socket.timeout:
                    # 超时无数据，检查所有已存在的IP超时情况
                    self.check_timeouts()
                    continue
                except Exception as e:
                    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]}] "
                          f"❌ 接收异常：{str(e)}")

    def udp_sender(self, ip):
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as send_sock:
            send_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            send_sock.bind(("", self.self_port))
            send_sock.settimeout(1)
            try:
                send_sock.sendto(self.request_data, (ip, self.target_port))
                print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]}] "
                      f"📤 发送请求 | 目标：{ip}:{self.target_port} | 数据：{self.request_data.hex().upper()}")
                
                # 发送后递增超时计数
                import main
                if ip in main.Target_IPs and len(main.Target_IPs[ip]) >= 3:
                    main.Target_IPs[ip][2] += 1
                    # 检查是否超时
                    if main.Target_IPs[ip][2] >= 5:
                        if f"udp_sender_{ip}" in [job.id for job in self.scheduler.get_jobs()]:
                            self.scheduler.remove_job(f"udp_sender_{ip}")
                        del main.Target_IPs[ip]
                        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]}] "
                              f"⚠️ 目标 {ip} 5次无回复，已删除并取消发送任务")
                return True
            except Exception as e:
                print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]}] "
                      f"❌ 发送失败 | 目标：{ip}:{self.target_port} | 原因：{str(e)}")
                return False
            
    # 注释掉InfluxDB写入方法，以便在没有依赖的情况下测试
    # def _write_to_influx(self, sender_ip, recv_data, recv_time):
    #     self.influx_writer.write_data(
    #         measurement="udp_responses",
    #         tags={"sender_ip": sender_ip},
    #         fields={"data": recv_data.decode('utf-8', errors='ignore')},
    #         time=recv_time
    #     )

    def check_timeouts(self):
        # 超时检查已移至udp_sender方法中，每次发送请求后检查
        pass

    def deal_recv_data(self, sender_ip, recv_data, recv_time):
        # 处理接收到的数据
        # 这里可以添加自定义的逻辑，例如解析数据、存储到数据库等
        import main
        recv_list = list(recv_data)
        if(recv_list[0] == 1):
            # 客户端的回复数据
            # 导入数据处理函数
            from data_processor import process_udp_response
            
            # 处理并写入数据
            if self.influx_writer:
                success = process_udp_response(self.influx_writer, recv_list, recv_time)
                if success:
                    print(f"✅ 数据写入成功 | 来源：{sender_ip}")
                else:
                    print(f"❌ 数据写入失败 | 来源：{sender_ip}")
            
            # 重置超时计数
            if sender_ip in main.Target_IPs and len(main.Target_IPs[sender_ip]) >= 3:
                main.Target_IPs[sender_ip][2] = 0
        elif(recv_list[0] == 2):
            # 客户端的呼叫数据
            # 解析数据：recv_list[2]是十位，recv_list[3]是个位
            tens_digit = recv_list[2]
            units_digit = recv_list[3]
            recovered_integer = tens_digit * 10 + units_digit
            
            # 添加到Target_IPs字典
            main.Target_IPs[sender_ip] = [recovered_integer, 0, 0]  # [数据, 保留字段, 超时计数]
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]}] "
                  f"📋 新目标添加 | IP：{sender_ip} | 数据：{recovered_integer}")
            
            # 初始化shared_udp_data
            if sender_ip not in self.shared_udp_data:
                self.shared_udp_data[sender_ip] = {}
            
            # 创建发送任务，每5秒发送一次
            job_id = f"udp_sender_{sender_ip}"
            if job_id not in [job.id for job in self.scheduler.get_jobs()]:
                self.scheduler.add_job(
                    func=self.udp_sender,
                    args=[sender_ip],
                    trigger='interval',
                    seconds=5,
                    id=job_id,
                    replace_existing=True
                )
                print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]}] "
                      f"🔄 发送任务创建 | 目标：{sender_ip} | 间隔：5秒")