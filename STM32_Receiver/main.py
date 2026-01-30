import multiprocessing
from datetime import datetime, timedelta
from apscheduler.schedulers.blocking import BlockingScheduler
from udp_tool import UDPTool

Target_IPs = {}
Target_Port = 8081
Self_Port = 8080
Send_Interval = 5
Request_Data = b"\xFF"

def start_schedular(udp_tool, exit_event, shared_udp_data):
    scheduler = BlockingScheduler(timezone = "Asia/Shanghai")
    ip_count = len(Target_IPs)
    time_slice = Send_Interval / ip_count if ip_count > 0 else Send_Interval
    for index, ip in enumerate(Target_IPs):
        shared_udp_data[ip] = {}
        initial_delay = index * time_slice
        start_date = datetime.now() + timedelta(seconds=initial_delay)

        scheduler.add_job(
            func=udp_tool.udp_sender,
            args=[ip],
            trigger='interval',
            seconds=Send_Interval,
            next_run_time=start_date,
            id=f"udp_sender_{ip}",
            replace_existing=True
        )
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        exit_event.set()
        scheduler.shutdown()

def main():
    multiprocessing.freeze_support()

    print("="*60)
    print("UDP精准定时收发程序（含InfluxDB写入）")
    print(f"启动时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60 + "\n")

    exit_event = multiprocessing.Event()
    manager = multiprocessing.Manager()
    shared_udp_data = manager.dict()

    udp_tool = UDPTool(
        self_port=Self_Port,
        target_port=Target_Port,
        request_data=Request_Data,
        influx_host="http://localhost:8181",
        influx_database="Wind",
        influx_token="apiv3_3dK1l9XS8U5woahz6rmuIxfjT_3_0StOLWQjxilRN5OT4ph_b0ZwKWj5m4Z-pQL5u18haoq5HzzNIopBo-A-yA",
        config_file_path="../frontend/public/config.json"
    )

    recv_process = multiprocessing.Process(target=udp_tool.udp_receiver, args=(exit_event, shared_udp_data), daemon=True)
    recv_process.start()

    # 取消启动时自动创建发送进程，改为动态创建

    try:
        while True:
            multiprocessing.Event().wait(1)  # 空等，仅保持主线程存活
    except KeyboardInterrupt:
        # 优雅退出
        exit_event.set()
        recv_process.terminate()
        recv_process.join()
        print("\n" + "="*60)
        print("程序已优雅退出")
        print("="*60)

if __name__ == "__main__":
    main()