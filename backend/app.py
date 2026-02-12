from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from influxdb_client_3 import (
    InfluxDBClient3, InfluxDBError, Point, WritePrecision,
    WriteOptions, write_client_options
)
import os
import json
from dotenv import load_dotenv
import pandas as pd
from pydantic import BaseModel
from typing import List, Dict, Optional
import datetime
import random

# 加载环境变量
load_dotenv()

# InfluxDB 连接配置
INFLUXDB_URL = "http://localhost:8181"
INFLUXDB_TOKEN = "apiv3_q7RPi0zeY1bWYCuPnbgrlMZSvyGqXHzhJ8iFhLQBZdIxk3CFuxSqerS89l6GdeQMGgM0ICCPYB42oiOszt1l4Q"
INFLUXDB_BUCKET = "windfarm"

# Silicon 相关配置
SILICON_API_URL = "http://localhost:8000"

# 创建 FastAPI 应用
app = FastAPI(
    title="Wind Farm Intelligent Monitoring Platform API",
    description="Backend API for wind power monitoring system based on FastAPI and InfluxDB",
    version="1.0.0"
)

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 在生产环境中应该设置具体的前端地址
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

write_options = WriteOptions(batch_size=1,
                             flush_interval=1_000,
                             jitter_interval=0,
                             retry_interval=5_000,
                             max_retries=3,
                             max_retry_delay=30_000,
                             exponential_base=2)

def success(self, data: str):
    print(f"Write succeeded: {data}")

def error(self, data: str, exception: InfluxDBError):
    print(f"Write failed: {data}, error: {exception}")

def retry(self, data: str, exception: InfluxDBError):
    print(f"Write retrying: {data}, error: {exception}")

wco = write_client_options(success_callback = success,
                            error_callback = error,
                            retry_callback = retry,
                            write_options = write_options)
# 创建 InfluxDB 客户端
client = InfluxDBClient3(host=INFLUXDB_URL, token=INFLUXDB_TOKEN, database=INFLUXDB_BUCKET, write_client_options=wco)

# 数据模型
class TurbineBase(BaseModel):
    id: str
    name: str
    location: str

class TurbineInfo(TurbineBase):
    bladeLength: float
    rotorDiameter: float
    ratedPower: float
    hubHeight: float
    bladeCount: int
    speedRange: str

class RuntimeData(BaseModel):
    dailyGeneration: float
    activePower: float
    status: str


class SystemInfo(BaseModel):
    model: str
    manufacturer: str
    installationDate: str
    runHours: float
    maintenanceCycle: int
    status: str
    statusText: str

class WindData(BaseModel):
    turbine_id: str
    speed: float
    direction: float

class WarningStats(BaseModel):
    error: int
    warning: int

class PowerTrend(BaseModel):
    power: List[float]

class DailyStats(BaseModel):
    totalGeneration: float
    avgPower: float
    maxPower: float
    runTime: float
    avgEfficiency: float

class Warning(BaseModel):
    id: str
    title: str
    description: str
    type: str
    timestamp: str

class FaultDistribution(BaseModel):
    name: str
    value: int

class DailyFaults(BaseModel):
    dates: List[str]
    counts: List[int]

class PowerComparison(BaseModel):
    hours: List[str]
    actual: List[float]
    predicted: List[float]

class Turbine(TurbineBase):
    status: str
    power: float
    windSpeed: float
    temperature: float
    vibration: float
    lastMaintenance: str
    efficiency: float

# 模拟数据（在InfluxDB未就绪时使用）
mock_turbines = [
    {
        "id": "T001",
        "name": "NW1",
        "location": "IM_Zone_A",
        "status": "running",
        "power": 2500,
        "windSpeed": 12.5,
        "temperature": 28,
        "vibration": 1.2,
        "lastMaintenance": "2026-01-10",
        "efficiency": 92
    },
    {
        "id": "T002",
        "name": "NW2",
        "location": "IM_Zone_A",
        "status": "warning",
        "power": 1800,
        "windSpeed": 15.2,
        "temperature": 32,
        "vibration": 3.5,
        "lastMaintenance": "2026-01-05",
        "efficiency": 78
    },
    {
        "id": "T003",
        "name": "NW3",
        "location": "IM_Zone_B",
        "status": "running",
        "power": 2200,
        "windSpeed": 10.8,
        "temperature": 26,
        "vibration": 0.8,
        "lastMaintenance": "2026-01-15",
        "efficiency": 88
    },
    {
        "id": "T004",
        "name": "NW4",
        "location": "IM_Zone_B",
        "status": "stopped",
        "power": 0.0,
        "windSpeed": 8.5,
        "temperature": 24.0,
        "vibration": 0.0,
        "lastMaintenance": "2026-01-01",
        "efficiency": 0.0
    },
    {
        "id": "T005",
        "name": "NW5",
        "location": "IM_Zone_C",
        "status": "running",
        "power": 2000,
        "windSpeed": 9.2,
        "temperature": 27,
        "vibration": 1.0,
        "lastMaintenance": "2026-01-12",
        "efficiency": 85
    }
]

mock_daily_stats = {
    "totalGeneration": 85600,
    "avgPower": 2850,
    "maxPower": 3200,
    "runTime": 24,
    "avgEfficiency": 89.5
}

mock_warnings = [
    {
        "turbine_id": "T001",
        "title": "Gearbox Temperature Too High",
        "description": "NW2 turbine gearbox temperature exceeds threshold, current temperature: 75°C",
        "type": "warning",
        "timestamp": "2026-01-18 14:30"
    },
    {
        "turbine_id": "T002",
        "title": "Abnormal Vibration Value",
        "description": "NW2 turbine vibration value exceeds safe range, current value: 4.5mm/s",
        "type": "warning",
        "timestamp": "2026-01-18 14:45"
    },
    {
        "turbine_id": "T005",
        "title": "Wind Speed Sensor Failure",
        "description": "NW5 turbine wind speed sensor not responding, please check",
        "type": "error",
        "timestamp": "2026-01-18 15:00"
    },
    {
        "turbine_id": "T003",
        "title": "Generator Temperature Too High",
        "description": "NW3 turbine generator temperature is high, current temperature: 65°C",
        "type": "warning",
        "timestamp": "2026-01-18 15:15"
    }
]

mock_fault_distribution = [
    {"name": "Sensor_Failure", "value": 25},
    {"name": "Gearbox_Failure", "value": 15},
    {"name": "Generator_Failure", "value": 10},
    {"name": "Blade_Failure", "value": 8},
    {"name": "Other_Failures", "value": 12}
]

mock_daily_faults = {
    "dates": ["1-13", "1-14", "1-15", "1-16", "1-17", "1-18"],
    "counts": [12, 8, 15, 10, 7, 14]
}

mock_power_comparison = {
    "hours": ["00", "02", "04", "06", "08", "10", "12", "14", "16", "18", "20", "22"],
    "actual": [850, 720, 680, 1200, 2100, 2800, 3100, 2900, 2700, 2200, 1500, 1000],
    "predicted": [900, 800, 700, 1300, 2000, 2700, 3000, 2800, 2600, 2300, 1600, 1100]
}

mock_turbine_info = [
    {
        "id": "T001",
        "name": "NW1",
        "location": "IM_Zone_A",
        "bladeLength": 55,
        "rotorDiameter": 112,
        "ratedPower": 2500,
        "hubHeight": 120,
        "bladeCount": 3,
        "speedRange": "3-20 RPM",
        "model": "WTG-2.5MW"
    },
    {
        "id": "T002",
        "name": "NW2",
        "location": "IM_Zone_A",
        "bladeLength": 55,
        "rotorDiameter": 112,
        "ratedPower": 2500,
        "hubHeight": 120,
        "bladeCount": 3,
        "speedRange": "3-20 RPM",
        "model": "WTG-2.5MW"
    }
]

mock_system_info = [
    {
        "model": "WTG-2.5MW",
        "manufacturer": "New Energy Technology Co., Ltd.",
        "installationDate": "2024-03-15",
        "runHours": 8640,
        "maintenanceCycle": 90,
        "status": "running",
        "statusText": "Running"
    },
    {
        "model": "WTG-2.5MW",
        "manufacturer": "New Energy Technology Co., Ltd.",
        "installationDate": "2024-03-15",
        "runHours": 8640,
        "maintenanceCycle": 90,
        "status": "running",
        "statusText": "Running"
    }
]

mock_wind_data = [
    {
        "turbine_id": "T001",
        "speed": 12.5,
        "direction": 135
    },
    {
        "turbine_id": "T002",
        "speed": 12.5,
        "direction": 135
    },
    {
        "turbine_id": "T003",
        "speed": 12.5,
        "direction": 135
    },
    {
        "turbine_id": "T004",
        "speed": 12.5,
        "direction": 135
    },
    {
        "turbine_id": "T005",
        "speed": 12.5,
        "direction": 135
    }
]

mock_alert_stats = {
    "critical": 0,
    "major": 2,
    "minor": 5
}

mock_power_trend = {
    "hours": ["00", "02", "04", "06", "08", "10", "12", "14", "16", "18", "20", "22"],
    "power": [850, 720, 680, 1200, 2100, 2800, 3100, 2900, 2700, 2200, 1500, 1000]
}

# 健康检查
@app.get("/")
def read_root():
    return {"message": "Wind Farm Intelligent Monitoring Platform API is running"}

# 风机相关API
@app.get("/api/turbines", response_model=List[Turbine])
def get_turbines(status: Optional[str] = None):
    """Get turbine list, supports status filtering"""
    try:
        # Try to query from InfluxDB
        query = f'SELECT * FROM turbine WHERE status = "{status}"' if status else f'SELECT * FROM turbine'
        # query = f'from(bucket: "{INFLUXDB_BUCKET}") |> range(start: -1h) |> filter(fn: (r) => r._measurement == "turbine")'
        # if status:
        #     query += f' |> filter(fn: (r) => r.status == "{status}")'
        # query += ' |> last()'
        
        result = client.query(query=query, mode="pandas")
        turbines = []
        
        for index, row in result.iterrows():
            turbine = Turbine(
                id=row["turbine_id"],
                name=row["name"],
                location=row["location"],
                status=row["status"],
                power=float(row["power"]),
                windSpeed=float(row["windSpeed"]),
                temperature=float(row["temperature"]),
                vibration=float(row["vibration"]),
                lastMaintenance=row["lastMaintenance"],
                efficiency=float(row["efficiency"])
            )
            turbines.append(turbine)
        
        if turbines:
            return turbines
        else:
            return []
    except Exception as e:
        print(f"InfluxDB query failed: {e}")
        return []
    
    # # 使用模拟数据
    # if status:
    #     return [t for t in mock_turbines if t["status"] == status]
    # return mock_turbines

@app.get("/api/turbines/{turbine_id}", response_model=TurbineInfo)
def get_turbine_info(turbine_id: str):
    """Get detailed information for specified turbine"""
    try:
        # Try to query from InfluxDB
        query = f"SELECT * FROM turbine_info WHERE turbine_id = '{turbine_id}'"
        # query = f'from(bucket: "{INFLUXDB_BUCKET}") |> range(start: -1h) |> filter(fn: (r) => r._measurement == "turbine" and r.turbine_id == "{turbine_id}") |> last()'
        result = client.query(query=query, mode="pandas")
        
        for index, row in result.iterrows():
            info = TurbineInfo(
                id=row["turbine_id"],
                name=row["name"],
                location=row["location"],
                bladeLength=float(row["bladeLength"]),
                rotorDiameter=float(row["rotorDiameter"]),
                ratedPower=float(row["ratedPower"]),
                hubHeight=float(row["hubHeight"]),
                bladeCount=int(row["bladeCount"]),
                speedRange=row["speedRange"]
            )
            return info
    except Exception as e:
        print(f"InfluxDB query failed: {e}")
    
    # # 使用模拟数据
    # if turbine_id == "T001":
    #     return mock_turbine_info
    # raise HTTPException(status_code=404, detail="Turbine not found")

@app.get("/api/turbines/{turbine_id}/runtime", response_model=RuntimeData)
def get_turbine_runtime(turbine_id: str):
    """Get turbine runtime data"""
    try:
        tz_bj = datetime.timezone(datetime.timedelta(hours=8))
        today_start_bj = datetime.datetime.now(tz_bj).replace(hour=0, minute=0, second=0, microsecond=0)
        start_utc_str = today_start_bj.astimezone(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
        # Try to query from InfluxDB
        query = f"SELECT SUM(power) as dailygeneration FROM turbine WHERE time >= '{start_utc_str}' AND time <= now() AND turbine_id = '{turbine_id}'"
        result_1 = client.query(query=query, mode="pandas")
        if result_1.empty or result_1["dailygeneration"].isna().all():
            daily_gen = 0.0
        else:
            # 明确访问列名，并取第一个值
            daily_gen = float(result_1["dailygeneration"].iloc[0])
        daily_gen = daily_gen * 5.0 / 3600.0

        query = f"SELECT power, status FROM turbine WHERE time >= '{start_utc_str}' AND time <= now() AND turbine_id = '{turbine_id}' ORDER BY time DESC LIMIT 1"
        result_2 = client.query(query=query, mode="pandas")
        if result_2.empty:
            # 如果没查到状态，给个默认值防止崩溃
            data = RuntimeData(dailyGeneration=daily_gen, activePower=0.0, status="Unknown")
        else:
            row = result_2.iloc[0]
            data = RuntimeData(
                dailyGeneration=daily_gen,
                activePower=float(row["power"]),
                status=row["status"]
            )
        return data
    except Exception as e:
        print(f"InfluxDB query failed: {e}")

@app.get("/api/turbines/{turbine_id}/system", response_model=SystemInfo)
def get_turbine_system(turbine_id: str):
    """Get turbine system information"""
    try:
        # Try to query from InfluxDB
        query = f"SELECT model FROM turbine_info WHERE turbine_id = '{turbine_id}'"
        result = client.query(query=query, mode="pandas")
        model = result.iloc[0]["model"]

        query = f"SELECT * FROM system_info WHERE model = '{model}'"
        result = client.query(query=query, mode="pandas")
        
        for index, row in result.iterrows():
            info = SystemInfo(
                    model=row["model"],
                    manufacturer=row["manufacturer"],
                    installationDate=row["installationDate"],
                    runHours=float(row["runHours"]),
                    maintenanceCycle=int(row["maintenanceCycle"]),
                    status=row["status"],
                    statusText=row["statusText"]
                )
            return info
    except Exception as e:
        print(f"InfluxDB query failed: {e}")
    
    # 使用模拟数据
    return mock_system_info

@app.get("/api/turbines/{turbine_id}/wind", response_model=WindData)
def get_turbine_wind(turbine_id: str):
    """Get wind speed and direction data"""
    try:
        # Try to query from InfluxDB
        query = f"SELECT * FROM wind WHERE turbine_id = '{turbine_id}' ORDER BY time DESC LIMIT 1"
        result = client.query(query=query, mode="pandas")

        row = result.iloc[0]
        data = WindData(
            turbine_id=row["turbine_id"],
            speed=float(row["speed"]),
            direction=float(row["direction"])
        )
        return data

    except Exception as e:
        print(f"InfluxDB query failed: {e}")

@app.get("/api/turbines/{turbine_id}/alerts", response_model=WarningStats)
def get_turbine_alerts(turbine_id: str):
    """Get turbine alert statistics"""
    try:
        # Try to query from InfluxDB
        query = f"SELECT * FROM warnings WHERE turbine_id = '{turbine_id}'"
        result = client.query(query=query, mode="pandas")
        
        stats = {"error": 0, "warning": 0}
        for index, row in result.iterrows():
            severity = row["type"]
            if severity in stats:
                stats[severity] += 1
        
        return WarningStats(**stats)
    except Exception as e:
        print(f"InfluxDB query failed: {e}")

@app.get("/api/turbines/{turbine_id}/power/trend", response_model=PowerTrend)
def get_turbine_power_trend(turbine_id: str):
    """Get power generation trend data"""
    try:
        query = f"SELECT * FROM turbine WHERE time > now() - INTERVAL '10min' AND turbine_id = '{turbine_id}' ORDER BY 'time' DESC"
        result = client.query(query=query, mode="pandas")
        
        power = []
        for index, row in result.iterrows():
            power.append(float(row["power"]))
        
        while len(power) < 120:
            power.append(0.0)
        
        return PowerTrend(power=power[:120])
    except Exception as e:
        print(f"InfluxDB query failed: {e}")

# 统计数据API
@app.get("/api/stats/daily", response_model=DailyStats)
def get_daily_stats():
    """Get daily power generation statistics"""
    try:
        # Try to query from InfluxDB
        query = f"SELECT * FROM daily_stats ORDER BY 'time' DESC LIMIT 1"
        # query = f'from(bucket: "{INFLUXDB_BUCKET}") |> range(start: -24h) |> filter(fn: (r) => r._measurement == "daily_stats") |> last()'
        result = client.query(query=query, mode="pandas")
        
        for index, row in result.iterrows():
            stats = DailyStats(
                totalGeneration=float(row["totalGeneration"]),
                avgPower=float(row["avgPower"]),
                maxPower=float(row["maxPower"]),
                runTime=float(row["runTime"]),
                avgEfficiency=float(row["avgEfficiency"])
            )
            return stats
    except Exception as e:
        print(f"InfluxDB query failed: {e}")

# 警告信息API
@app.get("/api/warnings", response_model=List[Warning])
def get_warnings():
    """Get latest warning information"""
    try:
        # Try to query from InfluxDB
        query = f"SELECT * FROM warnings WHERE time > now() - INTERVAL '6hour'"
        result = client.query(query=query, mode="pandas")
        
        warnings = []
        for index, row in result.iterrows():
            warning = Warning(
                id=row["turbine_id"],
                title=row["title"],
                description=row["description"],
                type=row["type"],
                timestamp=row["timestamp"]
            )
            warnings.append(warning)
        
        if warnings:
            return warnings
    except Exception as e:
        print(f"InfluxDB query failed: {e}")

# 故障相关API
@app.get("/api/faults/distribution", response_model=List[FaultDistribution])
def get_fault_distribution():
    """Get fault distribution data"""
    try:
        # Try to query from InfluxDB
        query = f"SELECT * FROM warnings WHERE time > now() - INTERVAL '6hour'"
        result = client.query(query=query, mode="pandas")
        
        distribution = []
        warnings = {}
        for index, row in result.iterrows():
            if row["title"] not in warnings:
                warnings[row["title"]] = 0
            warnings[row["title"]] += 1
        for key in warnings.keys():
            fault = FaultDistribution(
                name=key,
                value=warnings[key]
            )
            distribution.append(fault)
        
        if distribution:
            return distribution
    except Exception as e:
        print(f"InfluxDB query failed: {e}")

@app.get("/api/faults/daily", response_model=DailyFaults)
def get_daily_faults():
    """Get daily fault count data"""
    try:
        # 1. 计算时间边界（北京时间 CST）
        # 假设当前是北京时间，获取今天的 00:00:00
        tz_bj = datetime.timezone(datetime.timedelta(hours=8))
        now_bj = datetime.datetime.now(tz_bj)
        today_start_bj = now_bj.replace(hour=0, minute=0, second=0, microsecond=0)
        
        # 包含今天在内的最近 10 天起始点 (例如今天 10 号，起点就是 1 号)
        start_date_bj = today_start_bj - datetime.timedelta(days=9)
        # 统计终点：明天的 00:00:00（左闭右开区间）
        end_date_bj = today_start_bj + datetime.timedelta(days=1)

        # 转换为字符串用于 SQL (InfluxDB 3 接受 TIMESTAMP 格式)
        start_utc_str = start_date_bj.astimezone(datetime.timezone.utc).strftime('%Y-%m-%d %H:%M:%S')
        end_utc_str = end_date_bj.astimezone(datetime.timezone.utc).strftime('%Y-%m-%d %H:%M:%S')

        query = f"""
        SELECT 
            CAST(date_bin(interval '1 day', time + interval '8 hours') AS TIMESTAMP) as time_bucket, 
            COUNT(time) as total_warnings 
        FROM 'warnings' 
        WHERE time >= TIMESTAMP '{start_utc_str}'
          AND time < TIMESTAMP '{end_utc_str}'
        GROUP BY 1 
        ORDER BY 1 ASC
        """
        result = client.query(query=query, mode="pandas")

        idx = pd.date_range(start=start_date_bj, periods=10, freq='D', tz=tz_bj)

        if result.empty:
            return DailyFaults(
                dates=[d.strftime("%Y-%m-%d") for d in idx], 
                counts=[0] * len(idx)
            )

        result["time_bucket"] = pd.to_datetime(result["time_bucket"])

        if result["time_bucket"].dt.tz is None:
            result["time_bucket"] = result["time_bucket"].dt.tz_localize(tz_bj)
        else:
            result["time_bucket"] = result["time_bucket"].dt.tz_convert(tz_bj)

        result.set_index("time_bucket", inplace=True)
        result_final = result.reindex(idx, fill_value=0)

        dates = []
        counts = []
        for index, row in result_final.iterrows():
            date = index.strftime("%Y-%m-%d")
            dates.append(date)
            counts.append(int(row["total_warnings"]))

        return DailyFaults(dates=dates, counts=counts)
        
        # dates = []
        # counts = []
        # for index, row in result.iterrows():
        #     date = row["date"]
        #     if date:
        #         dates.append(date)
        #         counts.append(int(row["_value"]))
        
        # if dates and counts:
        #     return DailyFaults(dates=dates, counts=counts)
    except Exception as e:
        print(f"InfluxDB query failed: {e}")

# 发电相关API
@app.get("/api/power/comparison", response_model=PowerComparison)
def get_power_comparison():
    """Get daily power generation comparison data"""
    try:
        now_utc = pd.Timestamp.now(tz='UTC')
        
        # 1. 调整时间边界：
        # 结束点设为当前小时的顶格（例如 14:30 -> 15:00）
        # 这样才能包含正在进行的这一小时
        end_time_ceil = now_utc.ceil('h')
        # 起始点往前推 11 小时，得到总共 12 个时间槽
        start_time = end_time_ceil - pd.Timedelta(hours=11)
        # Try to query from InfluxDB
        query = f"""
            SELECT
                date_bin(interval '1 hour', time) as time_bucket,
                SUM(power) as total_power
            FROM 'turbine'
            WHERE time >= '{start_time.isoformat()}'
            AND time < '{end_time_ceil.isoformat()}'
            GROUP BY 1
            ORDER BY 1 ASC
        """
        result = client.query(query=query, mode="pandas")
        full_range = pd.date_range(start=start_time, end=end_time_ceil - pd.Timedelta(hours=1), freq='h', tz='UTC')
        if result.empty:
            return PowerComparison(
                hours=[d.tz_convert('Asia/Shanghai').strftime("%H:%M") for d in full_range],
                actual=[0.0] * 12,
                predicted=[0.0] * 12
            )

        result["time_bucket"] = pd.to_datetime(result["time_bucket"])
        if result["time_bucket"].dt.tz is None:
            result["time_bucket"] = result["time_bucket"].dt.tz_localize('UTC')
        result.set_index("time_bucket", inplace=True)

        result_final = result.reindex(full_range, fill_value=0)

        hours = []
        actual = []
        predicted = []
        for index, row in result_final.iterrows():
            local_hour = index.tz_convert('Asia/Shanghai').strftime("%H:%M")
            hours.append(local_hour)

            actual.append(round(5 * float(row["total_power"]) / 1000000, 2))
            predicted.append(0)
        
        return PowerComparison(hours=hours, actual=actual, predicted=predicted)
    except Exception as e:
        print(f"InfluxDB query failed: {e}")
        return PowerComparison(hours=[], actual=[], predicted=[])

# # 分析相关API
# @app.get("/api/analysis/overview")
# def get_analysis_overview():
#     """Get analysis overview data"""
#     return {
#         "totalTurbines": len(mock_turbines),
#         "runningTurbines": len([t for t in mock_turbines if t["status"] == "running"]),
#         "warningTurbines": len([t for t in mock_turbines if t["status"] == "warning"]),
#         "stoppedTurbines": len([t for t in mock_turbines if t["status"] == "stopped"]),
#         "totalGeneration": mock_daily_stats["totalGeneration"],
#         "avgEfficiency": mock_daily_stats["avgEfficiency"]
#     }

# @app.get("/api/analysis/detailed")
# def get_analysis_detailed():
#     """Get detailed analysis data"""
#     return {
#         "turbineStats": [
#             {
#                 "id": t["id"],
#                 "name": t["name"],
#                 "efficiency": t["efficiency"],
#                 "power": t["power"],
#                 "status": t["status"]
#             }
#             for t in mock_turbines
#         ],
#         "faultStats": {
#             "totalFaults": sum(f["value"] for f in mock_fault_distribution),
#             "topFaultTypes": mock_fault_distribution[:3]
#         },
#         "powerStats": {
#             "maxPower": mock_daily_stats["maxPower"],
#             "avgPower": mock_daily_stats["avgPower"],
#             "totalGeneration": mock_daily_stats["totalGeneration"]
#         }
#     }

# 数据刷新API
@app.post("/api/data/refresh")
def refresh_data():
    """Refresh data"""
    # Data refresh logic can be implemented here
    return {"message": "Data refresh successful"}

@app.post("/api/turbines/{turbine_id}/refresh")
def refresh_turbine_data(turbine_id: str):
    """Refresh data for specified turbine"""
    # Data refresh logic for specified turbine can be implemented here
    return {"message": f"Turbine {turbine_id} data refresh successful"}

# Test data write (for initializing InfluxDB）
@app.post("/api/test/write")
def write_test_data():
    """Write test data to InfluxDB"""
    try:
        # Write turbine status data
        for turbine in mock_turbines:
            point = Point("turbine")
            point.tag("turbine_id", turbine["id"])
            point.tag("status", turbine["status"])
            point.field("name", turbine["name"])
            point.field("location", turbine["location"])
            point.field("power", int(turbine["power"]))
            point.field("windSpeed", float(turbine["windSpeed"]))
            point.field("temperature", int(turbine["temperature"]))
            point.field("vibration", float(turbine["vibration"]))
            point.field("lastMaintenance", turbine["lastMaintenance"])
            point.field("efficiency", int(turbine["efficiency"]))
            client.write(record=point, write_precision="s")

        for turbine in mock_turbine_info:
            point = Point("turbine_info")
            point.tag("turbine_id", turbine["id"])
            point.field("name", turbine["name"])
            point.field("location", turbine["location"])
            point.field("bladeLength", float(turbine["bladeLength"]))
            point.field("rotorDiameter", float(turbine["rotorDiameter"]))
            point.field("ratedPower", float(turbine["ratedPower"]))
            point.field("hubHeight", float(turbine["hubHeight"]))
            point.field("bladeCount", int(turbine["bladeCount"]))
            point.field("speedRange", turbine["speedRange"])
            point.field("model", turbine["model"])
            client.write(record=point, write_precision="s")
        
        for turbine in mock_system_info:
            point = Point("system_info")
            point.field("model", turbine["model"])
            point.field("manufacturer", turbine["manufacturer"])
            point.field("installationDate", turbine["installationDate"])
            point.field("runHours", float(turbine["runHours"]))
            point.field("maintenanceCycle", int(turbine["maintenanceCycle"]))
            point.field("status", turbine["status"])
            point.field("statusText", turbine["statusText"])
            client.write(record=point, write_precision="s")
        
        for turbine in mock_wind_data:
            point = Point("wind")
            point.tag("turbine_id", turbine["turbine_id"])
            point.field("speed", float(turbine["speed"]))
            point.field("direction", float(turbine["direction"]))
            client.write(record=point, write_precision="s")

        for turbine in mock_warnings:
            point = Point("warnings")
            point.tag("turbine_id", turbine["turbine_id"])
            point.field("title", turbine["title"])
            point.field("description", turbine["description"])
            point.field("type", turbine["type"])
            point.field("timestamp", turbine["timestamp"])
            client.write(record=point, write_precision="s")
        
        # Write daily statistics data
        point = Point("daily_stats")
        point.field("totalGeneration", mock_daily_stats["totalGeneration"])
        point.field("avgPower", mock_daily_stats["avgPower"])
        point.field("maxPower", mock_daily_stats["maxPower"])
        point.field("runTime", mock_daily_stats["runTime"])
        point.field("avgEfficiency", mock_daily_stats["avgEfficiency"])
        client.write(record=point, write_precision="s")
        
        return {"message": "Test data write successful"}
    except Exception as e:
        import traceback
        return {"message": f"Test data write failed: {str(e)}", "error": traceback.format_exc()}

# 配置文件相关API
CONFIG_FILE_PATH = "../STM32_Receiver/config.json"

class ChannelConfig(BaseModel):
    column: str
    range: Dict[str, float]

class ClassConfig(BaseModel):
    class_id: int
    database: str
    channels: List[ChannelConfig]

@app.get("/api/config/{class_id}")
def get_config(class_id: int):
    """获取指定组号的配置"""
    try:
        if not os.path.exists(CONFIG_FILE_PATH):
            return {"error": "配置文件不存在"}
        
        with open(CONFIG_FILE_PATH, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        if str(class_id) in config:
            return config[str(class_id)]
        else:
            return {"error": f"组号 {class_id} 的配置不存在"}
    except Exception as e:
        return {"error": f"读取配置失败: {str(e)}"}

@app.put("/api/config/{class_id}")
def save_config(class_id: int, config: ClassConfig):
    """保存/更新指定组号的配置"""
    try:
        # 读取现有配置
        if os.path.exists(CONFIG_FILE_PATH):
            with open(CONFIG_FILE_PATH, 'r', encoding='utf-8') as f:
                full_config = json.load(f)
        else:
            full_config = {}
        
        # 更新指定组号的配置
        full_config[str(class_id)] = {
            "class_id": class_id,
            "database": config.database,
            "channels": [
                {
                    "column": channel.column,
                    "range": {
                        "min": channel.range.get("min", 0),
                        "max": channel.range.get("max", 65535)
                    }
                }
                for channel in config.channels
            ]
        }
        
        # 保存到文件
        with open(CONFIG_FILE_PATH, 'w', encoding='utf-8') as f:
            json.dump(full_config, f, indent=2, ensure_ascii=False)
        
        return {"message": f"组号 {class_id} 的配置已保存"}
    except Exception as e:
        return {"error": f"保存配置失败: {str(e)}"}

# 聊天助手API
class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    response: str

@app.post("/api/chat", response_model=ChatResponse)
def chat_with_assistant(request: ChatRequest):
    """智能助手交互API"""
    try:
        import requests
        import json
        
        # 硅基流动大模型API配置
        API_KEY = "your_api_key_here"  # 请替换为真实的API密钥
        API_URL = "https://ark-cn-beijing.bytedance.net/api/v3/chat/completions"
        
        user_message = request.message
        
        # 构建系统提示
        system_prompt = "你是一个专业的风电场监控系统智能助手，负责回答用户关于系统运行、配置、数据等方面的问题。请保持回答专业、准确、简洁。"
        
        # 构建请求数据
        payload = {
            "model": "ep-202602121111111111111111",  # 请替换为真实的模型ID
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
            "temperature": 0.7,
            "max_tokens": 1000
        }
        
        # 发送请求到硅基流动API
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {API_KEY}"
        }
        
        response = requests.post(API_URL, headers=headers, data=json.dumps(payload), timeout=30)
        response.raise_for_status()  # 检查请求是否成功
        
        # 解析响应
        result = response.json()
        assistant_response = result["choices"][0]["message"]["content"]
        
        return ChatResponse(response=assistant_response)
    except Exception as e:
        print(f"Chat API error: {e}")
        # 当API调用失败时，返回一个默认的错误响应
        return ChatResponse(response="抱歉，我暂时无法回答您的问题，请稍后再试。")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
