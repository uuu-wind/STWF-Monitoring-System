import pandas as pd
import numpy as np
import os
import json
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Tuple
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
        self.turbines_file = os.path.join(current_dir, "turbines.json")
        self.model_dir = os.path.join(current_dir, "models")
        self.forecast_result = {}
        self.scheduler = BackgroundScheduler()
        self.scheduler.add_job(self._forecast_task, 'interval', minutes=30, id='forecast_job')
        
        self.default_model = None
        self.default_features = None
        self.model_cache: Dict[str, object] = {}
        self.features_cache: Dict[str, List[str]] = {}
        self.model_weight = 0.5
        self.model_weights: Dict[str, float] = {}
        self.turbine_orientations: Dict[str, float] = {}
        
        self._load_model_and_config()
    
    def _load_base_line(self):
        df = pd.read_csv(self.base_line_file, header=None, names=['wind_speed', 'value'])
        return df

    def refresh_models(self):
        self.default_model = None
        self.default_features = None
        self.model_cache = {}
        self.features_cache = {}
        self._load_model_and_config()
    
    def _load_model_and_config(self):
        try:
            model_file = os.path.join(self.model_dir, "gbdt_T001.joblib")
            if os.path.exists(model_file):
                model_data = joblib.load(model_file)
                self.default_model = model_data["model"]
                self.default_features = model_data["features"]
                self.model_cache["T001"] = self.default_model
                self.features_cache["T001"] = self.default_features
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
                    raw_model_weights = config.get('model_weights', {})
                    if isinstance(raw_model_weights, dict):
                        parsed_weights: Dict[str, float] = {}
                        for key, value in raw_model_weights.items():
                            try:
                                parsed_weights[str(key).upper()] = float(value)
                            except (TypeError, ValueError):
                                continue
                        self.model_weights = parsed_weights
                        if self.model_weights:
                            print(f"按风机权重加载成功: {len(self.model_weights)} 台")
            else:
                print(f"配置文件不存在: {self.config_file}")
        except Exception as e:
            print(f"加载配置失败: {e}")

        self.turbine_orientations = self._load_turbine_orientations()

    def _load_turbine_orientations(self) -> Dict[str, float]:
        orientations: Dict[str, float] = {}
        try:
            if not os.path.exists(self.turbines_file):
                return orientations

            with open(self.turbines_file, 'r', encoding='utf-8') as f:
                turbine_data = json.load(f)

            for turbine_id, turbine_cfg in turbine_data.items():
                info = turbine_cfg.get('info', {}) if isinstance(turbine_cfg, dict) else {}
                raw_value = info.get('orientation', 0.0)
                try:
                    orientations[turbine_id.upper()] = float(raw_value)
                except (TypeError, ValueError):
                    orientations[turbine_id.upper()] = 0.0
        except Exception as e:
            print(f"加载风机朝向失败: {e}")

        return orientations

    def _get_turbine_ids(self) -> List[str]:
        if self.turbine_orientations:
            return list(self.turbine_orientations.keys())
        return ["T001"]

    def _get_model_and_features(self, turbine_id: str) -> Tuple[Optional[object], Optional[List[str]]]:
        tid = turbine_id.upper()
        if tid in self.model_cache and tid in self.features_cache:
            return self.model_cache[tid], self.features_cache[tid]

        model_file = os.path.join(self.model_dir, f"gbdt_{tid}.joblib")
        try:
            if os.path.exists(model_file):
                model_data = joblib.load(model_file)
                self.model_cache[tid] = model_data["model"]
                self.features_cache[tid] = model_data["features"]
                print(f"模型加载成功: {model_file}")
                return self.model_cache[tid], self.features_cache[tid]
        except Exception as e:
            print(f"加载模型失败({tid}): {e}")

        return self.default_model, self.default_features

    def _build_target_df(self, weather_df: Optional[pd.DataFrame] = None) -> pd.DataFrame:
        if weather_df is None:
            weather_df = self.weather.get_weather()
    
        weather_df['datetime'] = pd.to_datetime(weather_df['date'], utc=True).dt.tz_convert('Asia/Shanghai')
        
        china_tz = timezone(timedelta(hours=8))
        now = datetime.now(china_tz)
        
        target_times = []
        for i in range(1, 5):
            target_time = now + timedelta(hours=i)
            target_time = target_time.replace(minute=0, second=0, microsecond=0)
            target_times.append(target_time)
        
        target_data = []
        for target_time in target_times:
            exact_match = weather_df[weather_df['datetime'] == target_time]
            if not exact_match.empty:
                target_data.append(exact_match.iloc[0])
            else:
                closest_idx = (weather_df['datetime'] - target_time).abs().idxmin()
                target_data.append(weather_df.loc[closest_idx])

        return pd.DataFrame(target_data)

    def BaseLineForecast(self, turbine_id: str = "T001", target_df: Optional[pd.DataFrame] = None):
        base_line_df = self._load_base_line()
        if target_df is None:
            target_df = self._build_target_df()

        orientation = self.turbine_orientations.get(turbine_id.upper(), 0.0)
        
        # 考虑风向
        wind_direction_diff = target_df['wind_direction_10m'].values - orientation
        wind_speeds = target_df['wind_speed_10m'].values * np.abs(np.cos(np.radians(wind_direction_diff)))
        
        base_wind_speeds = base_line_df['wind_speed'].values
        base_values = base_line_df['value'].values
        
        interpolated_values = np.interp(wind_speeds, base_wind_speeds, base_values)
        interpolated_list = interpolated_values.tolist()
        for i in range(len(interpolated_list)):
            interpolated_list[i] = interpolated_list[i] * 1000
        
        return interpolated_list, target_df
    
    def FixForecast(self, turbine_id: str, baseline_result, target_df):
        model, features = self._get_model_and_features(turbine_id)
        if model is None or features is None:
            print("模型未加载，使用基线预测")
            return baseline_result
        
        try:
            X = target_df[features].astype(float).values
            model_predictions = model.predict(X)
            
            turbine_key = turbine_id.upper()
            a = self.model_weights.get(turbine_key, self.model_weight)
            combined_predictions = a * np.array(baseline_result) + (1 - a) * model_predictions
            
            return combined_predictions.tolist()
        except Exception as e:
            print(f"模型预测失败: {e}，使用基线预测")
            return baseline_result
    
    def _forecast_task(self):
        self.turbine_orientations = self._load_turbine_orientations()
        target_df = self._build_target_df()
        timestamp = datetime.now(timezone(timedelta(hours=8))).strftime('%H:%M')

        forecast_by_turbine = {}
        for turbine_id in self._get_turbine_ids():
            baseline_result, _ = self.BaseLineForecast(turbine_id=turbine_id, target_df=target_df)
            fix_result = self.FixForecast(turbine_id=turbine_id, baseline_result=baseline_result, target_df=target_df)
            forecast_by_turbine[turbine_id] = {
                'result': fix_result,
                'timestamp': timestamp
            }

        self.forecast_result = forecast_by_turbine
        print(f"[{datetime.now(timezone(timedelta(hours=8))).strftime('%Y-%m-%d %H:%M:%S')}] 预测数据已更新，风机数量: {len(forecast_by_turbine)}")
    
    def start_forecast_task(self):
        if not self.scheduler.running:
            self.scheduler.start()
            print("预测任务已启动，每30分钟更新一次")
    
    def stop_forecast_task(self):
        if self.scheduler.running:
            self.scheduler.shutdown()
            print("预测任务已停止")
    
    def GetForecast(self, turbine_id: Optional[str] = None):
        if not isinstance(self.forecast_result, dict):
            return self.forecast_result

        if turbine_id:
            return self.forecast_result.get(turbine_id.upper(), {})

        if "T001" in self.forecast_result:
            return self.forecast_result["T001"]

        for _, value in self.forecast_result.items():
            return value

        return {}

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
