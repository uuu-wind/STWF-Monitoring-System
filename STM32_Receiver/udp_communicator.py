import socket
import multiprocessing
from datetime import datetime, timedelta
from apscheduler.schedulers.blocking import BlockingScheduler
from influx_writer import InfluxDBWriter

class UDPCommunicator:
    def __init__(self, target_ips, target_port, self_port, send_interval, request_data=b"\xFF",
                 recv_buffer_size=1024, recv_timeout=0.5, influx_host="https://localhost:8181", influx_database="Wind", influx_token=None):
        self.target_ips = target_ips
        self.target_port = target_port
        self.self_port = self_port
        self.send_interval = send_interval
        self.request_data = request_data
        self.recv_buffer_size = recv_buffer_size
        self.recv_timeout = recv_timeout

        self.exit_event = multiprocessing.Event()
        self.recv_process = None
        self.send_process = None
        self.influx_host = influx_host
        self.influx_database = influx_database
        self.influx_token = influx_token

        self.manager = None
        self.shared_udp_data = None

    def _udp_receiver(self):
        client = InfluxDBWriter(
            host=self.influx_host,
            database=self.influx_database,
            token=self.influx_token
        )
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as recv_sock:
            recv_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            recv_sock.bind(("", self.self_port))
            recv_sock.settimeout(self.recv_timeout)
            print(f"启动接收进程，监听端口{self.self_port}")
            while not self.exit_event.is_set():
                try:
                    recv_data, (sender_ip, sender_port) = recv_sock.recvfrom(self.recv_buffer_size)
                    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]}] "
                          f"✅ 收到回复 | 来源：{sender_ip}:{sender_port} | 数据：{recv_data.decode('utf-8', errors='ignore')}")
                    # 更新共享字典（可选，仅用于记录状态）
                    self.shared_udp_data[sender_ip] = {"recv_data": recv_data.decode('utf-8', errors='ignore'), "recv_time": datetime.now()}
                    client.write_data(
                        measurement="udp_responses",
                        tags={"sender_ip": sender_ip, "sender_port": sender_port},
                        fields={"data": recv_data.decode('utf-8', errors='ignore')}
                    )
                except socket.timeout:
                    continue  # 超时无数据，继续监听
                except Exception as e:
                    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]}] "
                          f"❌ 接收异常：{str(e)}")
                    
    def _udp_sender(self, ip):
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as send_sock:
            send_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            send_sock.bind(("", self.self_port))
            send_sock.settimeout(1)
            try:
                send_sock.sendto(self.request_data, (ip, self.target_port))
                print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]}] "
                      f"📤 发送请求 | 目标：{ip}:{self.target_port} | 数据：{self.request_data.hex().upper()}")
                # 更新共享字典（记录发送时间）
                self.shared_udp_data[ip] = {"send_time": datetime.now(), **self.shared_udp_data.get(ip, {})}
            except Exception as e:
                # 发送失败Print
                print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]}] "
                      f"❌ 发送失败 | 目标：{ip}:{self.target_port} | 原因：{str(e)}")
                
    def _start_scheduler(self):
        scheduler = BlockingScheduler(timezone = "Asia/Shanghai")
        ip_count = len(self.target_ips)
        time_slice = self.send_interval / ip_count if ip_count > 0 else self.send_interval
        for index, ip in enumerate(self.target_ips):
            initial_delay = index * time_slice
            start_date = datetime.now() + timedelta(seconds=initial_delay)

            scheduler.add_job(
                func=self._udp_sender,
                trigger='interval',
                seconds=self.send_interval,
                next_run_time=start_date,
                args=[ip],
                id=f"udp_sender_{ip}"
            )
        print("调度器启动，定时发送UDP请求")
        try:
            scheduler.start()
        except (KeyboardInterrupt, SystemExit):
            scheduler.shutdown()
            self.exit_event.set()

    def start(self):
        self.manager = multiprocessing.Manager()
        self.shared_udp_data = self.manager.dict()
        for ip in self.target_ips:
            self.shared_udp_data[ip] = {}

        self.recv_process = multiprocessing.Process(target=self._udp_receiver, daemon=True)
        self.recv_process.start()

        self.send_process = multiprocessing.Process(target=self._start_scheduler, daemon=True)
        self.send_process.start()
        print("UDP通信进程已启动")

    def stop(self):
        self.exit_event.set()
        if self.recv_process and self.recv_process.is_alive():
            self.recv_process.terminate()
            self.recv_process.join()
        if self.send_process and self.send_process.is_alive():
            self.send_process.terminate()
            self.send_process.join()
        print("UDP通信进程已停止")
    
    def get_shared_data(self):
        return dict(self.shared_udp_data)