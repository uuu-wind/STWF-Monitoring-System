import pandas as pd
import numpy as np
import os
import json
from datetime import datetime, timedelta, timezone
from apscheduler.schedulers.background import BackgroundScheduler
from weather import Weather

try:
    import joblib
except Exception as e:
    raise ImportError(
        "joblib is not installed. Please install it using 'pip install joblib'."
    ) from e

class Forecast:
    def __init__(self):
        self.weather = Weather()
        current_dir = os.path.dirname(os.path.abspath(__file__))
        self.base_line_file = os.path.join(current_dir, "base_line.csv")
        self.config_file = os.path.join(current_dir, "config.json")
        self.model_dir = os.path.join(current_dir, "models")
        self.forecast_result = []
        self.scheduler = BackgroundScheduler()
        self.scheduler.add_job(self._forecast_task, 'interval', minutes=30, id='forecast_job')
        
        self.model = None
        self.features = None
        self.model_weight = 0.5
        
        self._load_model_and_config()
    
    def _load_base_line(self):
        df = pd.read_csv(self.base_line_file, header=None, names=['wind_speed', 'value'])
        return df
    
    def _load_model_and_config(self):
        try:
            model_file = os.path.join(self.model_dir, "gbdt_T001.joblib")
            if os.path.exists(model_file):
                model_data = joblib.load(model_file)
                self.model = model_data["model"]
                self.features = model_data["features"]
                print(f"模型加载成功: {model_file}")
            else:
                print(f"模型文件不存在: {model_file}")
        except Exception as e:
            print(f"加载模型失败: {e}")
        
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    if 'model_weight' in config:
                        self.model_weight = float(config['model_weight'])
                        print(f"权重加载成功: {self.model_weight}")
            else:
                print(f"配置文件不存在: {self.config_file}")
        except Exception as e:
            print(f"加载配置失败: {e}")
    
    def BaseLineForecast(self):
        base_line_df = self._load_base_line()
        
        weather_df = self.weather.get_weather()
        
        china_tz = timezone(timedelta(hours=8))
        now = datetime.now(china_tz)
        
        target_times = []
        for i in range(1, 5):
            target_time = now + timedelta(hours=i)
            target_time = target_time.replace(minute=0, second=0, microsecond=0)
            target_times.append(target_time)
        
        weather_df['datetime'] = pd.to_datetime(weather_df['date'], utc=True).dt.tz_convert('Asia/Shanghai')
        
        target_data = []
        for target_time in target_times:
            exact_match = weather_df[weather_df['datetime'] == target_time]
            if not exact_match.empty:
                target_data.append(exact_match.iloc[0])
            else:
                closest_idx = (weather_df['datetime'] - target_time).abs().idxmin()
                target_data.append(weather_df.loc[closest_idx])
        
        target_df = pd.DataFrame(target_data)
        
        wind_speeds = target_df['wind_speed_10m'].values
        
        base_wind_speeds = base_line_df['wind_speed'].values
        base_values = base_line_df['value'].values
        
        interpolated_values = np.interp(wind_speeds, base_wind_speeds, base_values)
        interpolated_list = interpolated_values.tolist()
        for i in range(len(interpolated_list)):
            interpolated_list[i] = interpolated_list[i] * 1000
        
        return interpolated_list, target_df
    
    def FixForecast(self, baseline_result, target_df):
        if self.model is None or self.features is None:
            print("模型未加载，使用基线预测")
            return baseline_result
        
        try:
            X = target_df[self.features].astype(float).values
            model_predictions = self.model.predict(X)
            
            a = self.model_weight
            combined_predictions = a * np.array(baseline_result) + (1 - a) * model_predictions
            
            return combined_predictions.tolist()
        except Exception as e:
            print(f"模型预测失败: {e}，使用基线预测")
            return baseline_result
    
    def _forecast_task(self):
        baseline_result, target_df = self.BaseLineForecast()
        fix_result = self.FixForecast(baseline_result, target_df)
        
        # self.forecast_result = {
        #     'baseline': baseline_result,
        #     'fix': fix_result,
        #     'timestamp': datetime.now(timezone(timedelta(hours=8))).strftime('%Y-%m-%d %H:%M:%S')
        # }
        self.forecast_result = {
            'result': fix_result,
            'timestamp': datetime.now(timezone(timedelta(hours=8))).strftime('%H:%M')
        }
        
        print(f"[{datetime.now(timezone(timedelta(hours=8))).strftime('%Y-%m-%d %H:%M:%S')}] 预测数据已更新")
    
    def start_forecast_task(self):
        if not self.scheduler.running:
            self.scheduler.start()
            print("预测任务已启动，每30分钟更新一次")
    
    def stop_forecast_task(self):
        if self.scheduler.running:
            self.scheduler.shutdown()
            print("预测任务已停止")
    
    def GetForecast(self):
        return self.forecast_result

if __name__ == "__main__":
    import time
    
    forecast = Forecast()
    forecast._forecast_task()
    forecast.start_forecast_task()
    
    try:
        while True:
            result = forecast.GetForecast()
            if result:
                print(f"当前预测结果: {result}")
            time.sleep(10)
    except KeyboardInterrupt:
        print("\n正在停止预测任务...")
        forecast.stop_forecast_task()
