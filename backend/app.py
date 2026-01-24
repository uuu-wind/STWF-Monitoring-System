from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS
import os
from dotenv import load_dotenv
from pydantic import BaseModel
from typing import List, Dict, Optional
import datetime
import random

# 加载环境变量
load_dotenv()

# InfluxDB 连接配置
INFLUXDB_URL = os.getenv("INFLUXDB_URL", "http://localhost:8086")
INFLUXDB_TOKEN = os.getenv("INFLUXDB_TOKEN", "your-token")
INFLUXDB_ORG = os.getenv("INFLUXDB_ORG", "your-org")
INFLUXDB_BUCKET = os.getenv("INFLUXDB_BUCKET", "windfarm")

# 创建 FastAPI 应用
app = FastAPI(
    title="风电智能监控平台API",
    description="基于FastAPI和InfluxDB的风电监控系统后端API",
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

# 创建 InfluxDB 客户端
client = InfluxDBClient(url=INFLUXDB_URL, token=INFLUXDB_TOKEN, org=INFLUXDB_ORG)
write_api = client.write_api(write_options=SYNCHRONOUS)
query_api = client.query_api()

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
    reactivePower: float
    apparentPower: float

class SystemInfo(BaseModel):
    model: str
    manufacturer: str
    installationDate: str
    runHours: float
    maintenanceCycle: int
    status: str
    statusText: str

class WindData(BaseModel):
    speed: float
    direction: float

class AlertStats(BaseModel):
    critical: int
    major: int
    minor: int

class PowerTrend(BaseModel):
    hours: List[str]
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
        "name": "北风一号",
        "location": "内蒙古风场A区",
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
        "name": "北风二号",
        "location": "内蒙古风场A区",
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
        "name": "北风三号",
        "location": "内蒙古风场B区",
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
        "name": "北风四号",
        "location": "内蒙古风场B区",
        "status": "stopped",
        "power": 0,
        "windSpeed": 8.5,
        "temperature": 24,
        "vibration": 0,
        "lastMaintenance": "2026-01-01",
        "efficiency": 0
    },
    {
        "id": "T005",
        "name": "北风五号",
        "location": "内蒙古风场C区",
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
        "id": "W001",
        "title": "齿轮箱温度过高",
        "description": "北风二号风机齿轮箱温度超过阈值，当前温度：75°C",
        "type": "warning",
        "timestamp": "2026-01-18 14:30"
    },
    {
        "id": "W002",
        "title": "振动值异常",
        "description": "北风二号风机振动值超过安全范围，当前值：4.5mm/s",
        "type": "warning",
        "timestamp": "2026-01-18 14:45"
    },
    {
        "id": "W003",
        "title": "风速传感器故障",
        "description": "北风五号风机风速传感器无响应，请检查",
        "type": "error",
        "timestamp": "2026-01-18 15:00"
    },
    {
        "id": "W004",
        "title": "发电机温度偏高",
        "description": "北风三号风机发电机温度偏高，当前温度：65°C",
        "type": "warning",
        "timestamp": "2026-01-18 15:15"
    }
]

mock_fault_distribution = [
    {"name": "传感器故障", "value": 25},
    {"name": "齿轮箱故障", "value": 15},
    {"name": "发电机故障", "value": 10},
    {"name": "叶片故障", "value": 8},
    {"name": "其他故障", "value": 12}
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

mock_turbine_info = {
    "id": "T001",
    "name": "北风一号",
    "location": "内蒙古风场A区",
    "bladeLength": 55,
    "rotorDiameter": 112,
    "ratedPower": 2500,
    "hubHeight": 120,
    "bladeCount": 3,
    "speedRange": "3-20 RPM"
}

mock_runtime_data = {
    "dailyGeneration": 28500,
    "activePower": 2200,
    "reactivePower": 350,
    "apparentPower": 2230
}

mock_system_info = {
    "model": "WTG-2.5MW",
    "manufacturer": "新能源科技有限公司",
    "installationDate": "2024-03-15",
    "runHours": 8640,
    "maintenanceCycle": 90,
    "status": "running",
    "statusText": "运行中"
}

mock_wind_data = {
    "speed": 12.5,
    "direction": 135
}

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
    return {"message": "风电智能监控平台API正在运行"}

# 风机相关API
@app.get("/api/turbines", response_model=List[Turbine])
def get_turbines(status: Optional[str] = None):
    """获取风机列表，支持状态筛选"""
    try:
        # 尝试从InfluxDB查询
        query = f'from(bucket: "{INFLUXDB_BUCKET}") |> range(start: -1h) |> filter(fn: (r) => r._measurement == "turbine")'
        if status:
            query += f' |> filter(fn: (r) => r.status == "{status}")'
        query += ' |> last()'
        
        result = query_api.query(query=query)
        turbines = []
        
        for table in result:
            for record in table.records:
                turbine = Turbine(
                    id=record.values.get("turbine_id", ""),
                    name=record.values.get("name", ""),
                    location=record.values.get("location", ""),
                    status=record.values.get("status", ""),
                    power=float(record.values.get("power", 0)),
                    windSpeed=float(record.values.get("windSpeed", 0)),
                    temperature=float(record.values.get("temperature", 0)),
                    vibration=float(record.values.get("vibration", 0)),
                    lastMaintenance=record.values.get("lastMaintenance", ""),
                    efficiency=float(record.values.get("efficiency", 0))
                )
                turbines.append(turbine)
        
        if turbines:
            return turbines
    except Exception as e:
        print(f"InfluxDB查询失败: {e}")
    
    # 使用模拟数据
    if status:
        return [t for t in mock_turbines if t["status"] == status]
    return mock_turbines

@app.get("/api/turbines/{turbine_id}", response_model=TurbineInfo)
def get_turbine_info(turbine_id: str):
    """获取指定风机的详细信息"""
    try:
        # 尝试从InfluxDB查询
        query = f'from(bucket: "{INFLUXDB_BUCKET}") |> range(start: -1h) |> filter(fn: (r) => r._measurement == "turbine_info" and r.turbine_id == "{turbine_id}") |> last()'
        result = query_api.query(query=query)
        
        for table in result:
            for record in table.records:
                info = TurbineInfo(
                    id=turbine_id,
                    name=record.values.get("name", ""),
                    location=record.values.get("location", ""),
                    bladeLength=float(record.values.get("bladeLength", 0)),
                    rotorDiameter=float(record.values.get("rotorDiameter", 0)),
                    ratedPower=float(record.values.get("ratedPower", 0)),
                    hubHeight=float(record.values.get("hubHeight", 0)),
                    bladeCount=int(record.values.get("bladeCount", 0)),
                    speedRange=record.values.get("speedRange", "")
                )
                return info
    except Exception as e:
        print(f"InfluxDB查询失败: {e}")
    
    # 使用模拟数据
    if turbine_id == "T001":
        return mock_turbine_info
    raise HTTPException(status_code=404, detail="风机不存在")

@app.get("/api/turbines/{turbine_id}/runtime", response_model=RuntimeData)
def get_turbine_runtime(turbine_id: str):
    """获取风机运行数据"""
    try:
        # 尝试从InfluxDB查询
        query = f'from(bucket: "{INFLUXDB_BUCKET}") |> range(start: -1h) |> filter(fn: (r) => r._measurement == "runtime_data" and r.turbine_id == "{turbine_id}") |> last()'
        result = query_api.query(query=query)
        
        for table in result:
            for record in table.records:
                data = RuntimeData(
                    dailyGeneration=float(record.values.get("dailyGeneration", 0)),
                    activePower=float(record.values.get("activePower", 0)),
                    reactivePower=float(record.values.get("reactivePower", 0)),
                    apparentPower=float(record.values.get("apparentPower", 0))
                )
                return data
    except Exception as e:
        print(f"InfluxDB查询失败: {e}")
    
    # 使用模拟数据
    return mock_runtime_data

@app.get("/api/turbines/{turbine_id}/system", response_model=SystemInfo)
def get_turbine_system(turbine_id: str):
    """获取风机系统信息"""
    try:
        # 尝试从InfluxDB查询
        query = f'from(bucket: "{INFLUXDB_BUCKET}") |> range(start: -1h) |> filter(fn: (r) => r._measurement == "system_info" and r.turbine_id == "{turbine_id}") |> last()'
        result = query_api.query(query=query)
        
        for table in result:
            for record in table.records:
                info = SystemInfo(
                    model=record.values.get("model", ""),
                    manufacturer=record.values.get("manufacturer", ""),
                    installationDate=record.values.get("installationDate", ""),
                    runHours=float(record.values.get("runHours", 0)),
                    maintenanceCycle=int(record.values.get("maintenanceCycle", 0)),
                    status=record.values.get("status", ""),
                    statusText=record.values.get("statusText", "")
                )
                return info
    except Exception as e:
        print(f"InfluxDB查询失败: {e}")
    
    # 使用模拟数据
    return mock_system_info

@app.get("/api/turbines/{turbine_id}/wind", response_model=WindData)
def get_turbine_wind(turbine_id: str):
    """获取风速风向数据"""
    try:
        # 尝试从InfluxDB查询
        query = f'from(bucket: "{INFLUXDB_BUCKET}") |> range(start: -1h) |> filter(fn: (r) => r._measurement == "wind_data" and r.turbine_id == "{turbine_id}") |> last()'
        result = query_api.query(query=query)
        
        for table in result:
            for record in table.records:
                data = WindData(
                    speed=float(record.values.get("speed", 0)),
                    direction=float(record.values.get("direction", 0))
                )
                return data
    except Exception as e:
        print(f"InfluxDB查询失败: {e}")
    
    # 使用模拟数据
    return mock_wind_data

@app.get("/api/turbines/{turbine_id}/alerts", response_model=AlertStats)
def get_turbine_alerts(turbine_id: str):
    """获取风机告警统计"""
    try:
        # 尝试从InfluxDB查询
        query = f'from(bucket: "{INFLUXDB_BUCKET}") |> range(start: -24h) |> filter(fn: (r) => r._measurement == "alerts" and r.turbine_id == "{turbine_id}")'
        result = query_api.query(query=query)
        
        stats = {"critical": 0, "major": 0, "minor": 0}
        for table in result:
            for record in table.records:
                severity = record.values.get("severity", "")
                if severity in stats:
                    stats[severity] += 1
        
        return AlertStats(**stats)
    except Exception as e:
        print(f"InfluxDB查询失败: {e}")
    
    # 使用模拟数据
    return mock_alert_stats

@app.get("/api/turbines/{turbine_id}/power/trend", response_model=PowerTrend)
def get_turbine_power_trend(turbine_id: str):
    """获取发电量趋势数据"""
    try:
        # 尝试从InfluxDB查询
        query = f'from(bucket: "{INFLUXDB_BUCKET}") |> range(start: -24h) |> filter(fn: (r) => r._measurement == "power_trend" and r.turbine_id == "{turbine_id}")'
        result = query_api.query(query=query)
        
        hours = []
        power = []
        for table in result:
            for record in table.records:
                hour = record.values.get("hour", "")
                if hour:
                    hours.append(hour)
                    power.append(float(record.values.get("power", 0)))
        
        if hours and power:
            return PowerTrend(hours=hours, power=power)
    except Exception as e:
        print(f"InfluxDB查询失败: {e}")
    
    # 使用模拟数据
    return mock_power_trend

# 统计数据API
@app.get("/api/stats/daily", response_model=DailyStats)
def get_daily_stats():
    """获取当日发电统计数据"""
    try:
        # 尝试从InfluxDB查询
        query = f'from(bucket: "{INFLUXDB_BUCKET}") |> range(start: -24h) |> filter(fn: (r) => r._measurement == "daily_stats") |> last()'
        result = query_api.query(query=query)
        
        for table in result:
            for record in table.records:
                stats = DailyStats(
                    totalGeneration=float(record.values.get("totalGeneration", 0)),
                    avgPower=float(record.values.get("avgPower", 0)),
                    maxPower=float(record.values.get("maxPower", 0)),
                    runTime=float(record.values.get("runTime", 0)),
                    avgEfficiency=float(record.values.get("avgEfficiency", 0))
                )
                return stats
    except Exception as e:
        print(f"InfluxDB查询失败: {e}")
    
    # 使用模拟数据
    return mock_daily_stats

# 警告信息API
@app.get("/api/warnings", response_model=List[Warning])
def get_warnings():
    """获取最新警告信息"""
    try:
        # 尝试从InfluxDB查询
        query = f'from(bucket: "{INFLUXDB_BUCKET}") |> range(start: -24h) |> filter(fn: (r) => r._measurement == "warnings") |> sort(columns: ["_time"], desc: true) |> limit(n: 10)'
        result = query_api.query(query=query)
        
        warnings = []
        for table in result:
            for record in table.records:
                warning = Warning(
                    id=record.values.get("warning_id", ""),
                    title=record.values.get("title", ""),
                    description=record.values.get("description", ""),
                    type=record.values.get("type", ""),
                    timestamp=record.values.get("timestamp", "")
                )
                warnings.append(warning)
        
        if warnings:
            return warnings
    except Exception as e:
        print(f"InfluxDB查询失败: {e}")
    
    # 使用模拟数据
    return mock_warnings

# 故障相关API
@app.get("/api/faults/distribution", response_model=List[FaultDistribution])
def get_fault_distribution():
    """获取故障分布数据"""
    try:
        # 尝试从InfluxDB查询
        query = f'from(bucket: "{INFLUXDB_BUCKET}") |> range(start: -7d) |> filter(fn: (r) => r._measurement == "faults") |> group(columns: ["fault_type"]) |> count()'
        result = query_api.query(query=query)
        
        distribution = []
        for table in result:
            for record in table.records:
                fault = FaultDistribution(
                    name=record.values.get("fault_type", ""),
                    value=int(record.values.get("_value", 0))
                )
                distribution.append(fault)
        
        if distribution:
            return distribution
    except Exception as e:
        print(f"InfluxDB查询失败: {e}")
    
    # 使用模拟数据
    return mock_fault_distribution

@app.get("/api/faults/daily", response_model=DailyFaults)
def get_daily_faults():
    """获取每日故障数数据"""
    try:
        # 尝试从InfluxDB查询
        query = f'from(bucket: "{INFLUXDB_BUCKET}") |> range(start: -7d) |> filter(fn: (r) => r._measurement == "faults") |> group(columns: ["date"]) |> count()'
        result = query_api.query(query=query)
        
        dates = []
        counts = []
        for table in result:
            for record in table.records:
                date = record.values.get("date", "")
                if date:
                    dates.append(date)
                    counts.append(int(record.values.get("_value", 0)))
        
        if dates and counts:
            return DailyFaults(dates=dates, counts=counts)
    except Exception as e:
        print(f"InfluxDB查询失败: {e}")
    
    # 使用模拟数据
    return mock_daily_faults

# 发电相关API
@app.get("/api/power/comparison", response_model=PowerComparison)
def get_power_comparison():
    """获取当日发电量对比数据"""
    try:
        # 尝试从InfluxDB查询
        query = f'from(bucket: "{INFLUXDB_BUCKET}") |> range(start: -24h) |> filter(fn: (r) => r._measurement == "power_comparison")'
        result = query_api.query(query=query)
        
        hours = []
        actual = []
        predicted = []
        for table in result:
            for record in table.records:
                hour = record.values.get("hour", "")
                if hour:
                    hours.append(hour)
                    actual.append(float(record.values.get("actual", 0)))
                    predicted.append(float(record.values.get("predicted", 0)))
        
        if hours and actual and predicted:
            return PowerComparison(hours=hours, actual=actual, predicted=predicted)
    except Exception as e:
        print(f"InfluxDB查询失败: {e}")
    
    # 使用模拟数据
    return mock_power_comparison

# 分析相关API
@app.get("/api/analysis/overview")
def get_analysis_overview():
    """获取分析概览数据"""
    return {
        "totalTurbines": len(mock_turbines),
        "runningTurbines": len([t for t in mock_turbines if t["status"] == "running"]),
        "warningTurbines": len([t for t in mock_turbines if t["status"] == "warning"]),
        "stoppedTurbines": len([t for t in mock_turbines if t["status"] == "stopped"]),
        "totalGeneration": mock_daily_stats["totalGeneration"],
        "avgEfficiency": mock_daily_stats["avgEfficiency"]
    }

@app.get("/api/analysis/detailed")
def get_analysis_detailed():
    """获取详细分析数据"""
    return {
        "turbineStats": [
            {
                "id": t["id"],
                "name": t["name"],
                "efficiency": t["efficiency"],
                "power": t["power"],
                "status": t["status"]
            }
            for t in mock_turbines
        ],
        "faultStats": {
            "totalFaults": sum(f["value"] for f in mock_fault_distribution),
            "topFaultTypes": mock_fault_distribution[:3]
        },
        "powerStats": {
            "maxPower": mock_daily_stats["maxPower"],
            "avgPower": mock_daily_stats["avgPower"],
            "totalGeneration": mock_daily_stats["totalGeneration"]
        }
    }

# 数据刷新API
@app.post("/api/data/refresh")
def refresh_data():
    """刷新数据"""
    # 这里可以实现数据刷新逻辑
    return {"message": "数据刷新成功"}

@app.post("/api/turbines/{turbine_id}/refresh")
def refresh_turbine_data(turbine_id: str):
    """刷新指定风机数据"""
    # 这里可以实现指定风机数据刷新逻辑
    return {"message": f"风机 {turbine_id} 数据刷新成功"}

# 测试数据写入（用于初始化InfluxDB）
@app.post("/api/test/write")
def write_test_data():
    """写入测试数据到InfluxDB"""
    try:
        # 写入风机状态数据
        for turbine in mock_turbines:
            point = Point("turbine")
            point.tag("turbine_id", turbine["id"])
            point.tag("name", turbine["name"])
            point.tag("location", turbine["location"])
            point.field("status", turbine["status"])
            point.field("power", turbine["power"])
            point.field("windSpeed", turbine["windSpeed"])
            point.field("temperature", turbine["temperature"])
            point.field("vibration", turbine["vibration"])
            point.field("lastMaintenance", turbine["lastMaintenance"])
            point.field("efficiency", turbine["efficiency"])
            write_api.write(bucket=INFLUXDB_BUCKET, record=point)
        
        # 写入每日统计数据
        point = Point("daily_stats")
        point.field("totalGeneration", mock_daily_stats["totalGeneration"])
        point.field("avgPower", mock_daily_stats["avgPower"])
        point.field("maxPower", mock_daily_stats["maxPower"])
        point.field("runTime", mock_daily_stats["runTime"])
        point.field("avgEfficiency", mock_daily_stats["avgEfficiency"])
        write_api.write(bucket=INFLUXDB_BUCKET, record=point)
        
        return {"message": "测试数据写入成功"}
    except Exception as e:
        return {"message": f"测试数据写入失败: {str(e)}"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
