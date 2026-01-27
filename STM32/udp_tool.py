import socket
from datetime import datetime
from influx_writer import InfluxDBWriter

class UDPTool:
    def __init__(self, self_port, target_port, request_data=b"\xFF", recv_buffer_size=1024, recv_timeout=0.5,
                 influx_host="https://localhost:8181", influx_database="Wind", influx_token=None):
        self.self_port = self_port
        self.target_port = target_port
        self.request_data = request_data
        self.recv_buffer_size = recv_buffer_size
        self.recv_timeout = recv_timeout

        self.influx_host = influx_host
        self.influx_database = influx_database
        self.influx_token = influx_token

        self.influx_writer = None

    def udp_receiver(self, exit_event, shared_udp_data):
        self.influx_writer = InfluxDBWriter(
            host=self.influx_host,
            database=self.influx_database,
            token=self.influx_token
        )
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
                    self._write_to_influx(sender_ip, recv_data, recv_time)
                except socket.timeout:
                    continue  # 超时无数据，继续监听
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
                return True
            except Exception as e:
                print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]}] "
                      f"❌ 发送失败 | 目标：{ip}:{self.target_port} | 原因：{str(e)}")
                return False
            
    def _write_to_influx(self, sender_ip, recv_data, recv_time):
        self.influx_writer.write_data(
            measurement="udp_responses",
            tags={"sender_ip": sender_ip},
            fields={"data": recv_data.decode('utf-8', errors='ignore')},
            time=recv_time
        )