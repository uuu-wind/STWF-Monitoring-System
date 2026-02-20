import os
import json
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

import numpy as np
import pandas as pd
from dotenv import load_dotenv

from influxdb_client_3 import InfluxDBClient3

from weather import Weather

try:
    from sklearn.ensemble import GradientBoostingRegressor
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
except Exception as e:
    raise ImportError(
        "scikit-learn is not installed. Please install it using 'pip install scikit-learn'."
    ) from e

try:
    import joblib
except Exception as e:
    raise ImportError(
        "joblib is not installed. Please install it using 'pip install joblib'."
    ) from e

try:
    from scipy.optimize import minimize_scalar
except Exception as e:
    raise ImportError(
        "scipy is not installed. Please install it using 'pip install scipy'."
    ) from e

@dataclass
class TrainConfig:
    influx_url: str = "http://localhost:8181"
    influx_token: str = ""
    influx_database: str = "windfarm"
    lookback_days: int = 7
    timezone_name: str = "Asia/Shanghai"
    model_dir: str = "./models"
    gbdt_params: dict = None
    low_power_method: str = "quantile"
    low_power_abs_threshold: float = 0.1
    low_power_quantile: float = 0.05
    min_rows_after_filter: int = 100

class GBDTTrainer:
    """
    Trainer for Gradient Boosting Decision Tree (GBDT) model.
    """
    def __init__(self, config: TrainConfig):
        self.config = config
        if self.config.gbdt_params is None:
            self.config.gbdt_params = dict(
                n_estimators = 300,
                learning_rate = 0.01,
                max_depth = 3,
                random_state  = 42,
                loss = "squared_error"
            )
        os.makedirs(self.config.model_dir, exist_ok=True)
        self.client = InfluxDBClient3(
            host=self.config.influx_url,
            token=self.config.influx_token,
            database=self.config.influx_database
        )
        self.weather = Weather()

    def _query_hourly_power(self, turbine_id: str, use_test_data: bool = False) -> pd.DataFrame:
        """
        Query hourly power data from InfluxDB or test CSV file.
        """
        if use_test_data:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            test_file = os.path.join(current_dir, "power_with_noise.csv")
            
            if not os.path.exists(test_file):
                print(f"测试数据文件不存在: {test_file}")
                return pd.DataFrame(columns=["time_bucket", "power_avg"])
            
            df = pd.read_csv(test_file)
            df["time_bucket"] = pd.to_datetime(df["time"], errors="coerce")
            df["power_avg"] = df["power"]
            df = df[["time_bucket", "power_avg"]]
            df = df.dropna(subset=["time_bucket"])
            return df
        else:
            now_utc = pd.Timestamp.now(tz="UTC")
            start_utc = now_utc - pd.Timedelta(days=self.config.lookback_days)
            query = f"""
                SELECT
                    date_bin(interval '1 hour', time) as time_bucket,
                    AVG(power) as power_avg
                FROM 'turbine'
                WHERE time >= '{start_utc.isoformat()}'
                    AND time <= '{now_utc.isoformat()}'
                    AND turbine_id = '{turbine_id}'
                GROUP BY 1
                ORDER BY 1 ASC
            """
            df = self.client.query(query=query, mode = "pandas")
            if df is None or df.empty:
                return pd.DataFrame(columns=["time_bucket", "power_avg"])

            df["time_bucket"] = pd.to_datetime(df["time_bucket"], utc=True, errors = "coerce")
            df = df.dropna(subset=["time_bucket"])
            return df

    def _get_past_weather(self) -> pd.DataFrame:
        """
        Get past weather data from Open-Meteo API.
        """
        wdf = self.weather.get_past_weather()
        if wdf is None or wdf.empty:
            return pd.DataFrame()
        
        wdf = wdf.copy()
        wdf["date"] = pd.to_datetime(wdf["date"], errors = "coerce", utc = False)

        if wdf["date"].dt.tz is None:
            wdf["date"] = wdf["date"].dt.tz_localize(self.config.timezone_name)
        wdf["time_hour"] = wdf["date"].dt.tz_convert(self.config.timezone_name).dt.floor("h")
        wdf = wdf.drop(columns=["date"])

        return wdf

    def _filter_low_power(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Filter out low power data points.
        """
        if df.empty:
            return df

        if "power_avg" not in df.columns:
            raise ValueError("DataFrame must contain 'power_avg' column.")
        
        power = df["power_avg"].astype(float)

        method = (self.config.low_power_method or "quantile").lower()
        if method == "quantile":
            q = float(self.config.low_power_quantile)
            q = min(max(q, 0.0), 1.0)
            threshold = float(power.quantile(q))
        elif method == "absolute":
            threshold = float(self.config.low_power_abs_threshold)
        else:
            raise ValueError(f"Unknown low_power_method: {self.config.low_power_method}")
        
        before = len(df)
        df2 = df.loc[power >= threshold].copy()
        after = len(df2)
        print(f"[train] low-power filter method={method}, threshold={threshold:.6g}, "
          f"removed={before-after}, remain={after}")

        return df2
    
    def build_training_set(self, turbine_id: str, use_test_data: bool = False) -> pd.DataFrame:
        """
        Build training set for GBDT model.
        """
        power_df = self._query_hourly_power(turbine_id, use_test_data=use_test_data)
        if power_df is None or power_df.empty:
            raise RuntimeError("No power data available.")
        
        power_df["time_hour"] = (
            power_df["time_bucket"]
            .dt.tz_convert(self.config.timezone_name)
            .dt.floor("h")
        )

        weather_df = self._get_past_weather()
        if weather_df is None or weather_df.empty:
            raise RuntimeError("No weather data available.")
        
        weather_cols = [c for c in weather_df.columns if c != "time_hour"]

        df = pd.merge(power_df[["time_hour", "power_avg"]], weather_df, on="time_hour", how="inner")
        df = self._filter_low_power(df)
        if len(df) < self.config.min_rows_after_filter:
            raise RuntimeError(f"Not enough data after low-power filter, remain={len(df)}")
        df = df.sort_values("time_hour").reset_index(drop=True)

        return df, weather_cols

    def train(self, turbine_id: str, test_size: float = 0.2, use_test_data: bool = False):
        """
        Train GBDT model for a turbine.
        """
        df, feature_cols = self.build_training_set(turbine_id, use_test_data=use_test_data)
        if df is None or df.empty:
            raise RuntimeError("No training data available.")
        y = df["power_avg"].astype(float).values
        X = df[feature_cols].astype(float).values

        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=42
        )

        model = GradientBoostingRegressor(**self.config.gbdt_params)
        model.fit(X_train, y_train)

        pred = model.predict(X_test)

        report = {
            "turbine_id": turbine_id,
            "rows": int(len(df)),
            "features": feature_cols,
            "mae": float(mean_absolute_error(y_test, pred)),
            "rmse": float(np.sqrt(mean_squared_error(y_test, pred))),
            "r2": float(r2_score(y_test, pred)),
        }

        save_path = os.path.join(self.config.model_dir, f"gbdt_{turbine_id}.joblib")
        joblib.dump({"model": model, "features": feature_cols}, save_path)
        report["model_path"] = save_path
        
        self.calculate_and_save_optimal_weight(turbine_id, model, use_test_data=use_test_data)
        
        return report
    
    def _get_baseline_prediction(self, weather_df):
        try:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            base_line_file = os.path.join(current_dir, "base_line.csv")
            
            if not os.path.exists(base_line_file):
                print(f"基线文件不存在: {base_line_file}")
                return None
            
            base_line_df = pd.read_csv(base_line_file, header=None, names=['wind_speed', 'value'])
            
            wind_speeds = weather_df['wind_speed_10m'].values
            base_wind_speeds = base_line_df['wind_speed'].values
            base_values = base_line_df['value'].values
            
            interpolated_values = np.interp(wind_speeds, base_wind_speeds, base_values)
            interpolated_values = interpolated_values * 1000
            
            return interpolated_values
        except Exception as e:
            print(f"计算基线预测失败: {e}")
            return None
    
    def _get_last_24h_data(self, turbine_id: str, use_test_data: bool = False):
        try:
            if use_test_data:
                current_dir = os.path.dirname(os.path.abspath(__file__))
                test_file = os.path.join(current_dir, "power_with_noise.csv")
                
                if not os.path.exists(test_file):
                    print(f"测试数据文件不存在: {test_file}")
                    return None
                
                df = pd.read_csv(test_file)
                df["time_bucket"] = pd.to_datetime(df["time"], errors="coerce")
                df["power_avg"] = df["power"]
                df = df[["time_bucket", "power_avg"]]
                df = df.dropna(subset=["time_bucket"])
                
                return df
            else:
                now_utc = pd.Timestamp.now(tz="UTC")
                start_utc = now_utc - pd.Timedelta(hours=24)
                
                query = f"""
                    SELECT
                        date_bin(interval '1 hour', time) as time_bucket,
                        AVG(power) as power_avg
                    FROM 'turbine'
                    WHERE time >= '{start_utc.isoformat()}'
                        AND time <= '{now_utc.isoformat()}'
                        AND turbine_id = '{turbine_id}'
                    GROUP BY 1
                    ORDER BY 1 ASC
                """
                
                df = self.client.query(query=query, mode="pandas")
                if df is None or df.empty:
                    return None
                
                df["time_bucket"] = pd.to_datetime(df["time_bucket"], utc=True, errors="coerce")
                df = df.dropna(subset=["time_bucket"])
                
                return df
        except Exception as e:
            print(f"获取过去24小时数据失败: {e}")
            return None
    
    def _optimize_weight(self, actual_values, baseline_predictions, trained_predictions):
        try:
            def objective_function(a):
                combined = a * baseline_predictions + (1 - a) * trained_predictions
                mse = np.mean((combined - actual_values) ** 2)
                return mse
            
            result = minimize_scalar(
                objective_function,
                bounds=(0, 1),
                method='bounded'
            )
            
            optimal_a = result.x
            min_mse = result.fun
            
            print(f"最优权重 a = {optimal_a:.4f}, 最小MSE = {min_mse:.4f}")
            
            return optimal_a
        except Exception as e:
            print(f"优化权重失败: {e}")
            return 0.5
    
    def _save_weight_to_config(self, weight):
        try:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            config_file = os.path.join(current_dir, "config.json")
            
            if os.path.exists(config_file):
                with open(config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
            else:
                config = {}
            
            config['model_weight'] = float(weight)
            config['weight_timestamp'] = datetime.now(timezone(timedelta(hours=8))).strftime('%Y-%m-%d %H:%M:%S')
            
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            
            print(f"权重已保存到 config.json: {weight:.4f}")
            return True
        except Exception as e:
            print(f"保存权重到 config.json 失败: {e}")
            return False
    
    def calculate_and_save_optimal_weight(self, turbine_id: str, model, use_test_data: bool = False):
        try:
            china_tz = timezone(timedelta(hours=8))
            current_time = datetime.now(china_tz).strftime('%Y-%m-%d %H:%M:%S')
            print(f"[{current_time}] 开始计算最优权重...")
            
            df = self._get_last_24h_data(turbine_id, use_test_data=use_test_data)
            if df is None or df.empty:
                print(f"[{current_time}] 无法获取过去24小时的实际功率数据")
                return False
            
            df = df.copy()
            df["time_hour"] = (
                pd.to_datetime(df["time_bucket"], utc = True, errors = "coerce")
                .dt.tz_convert(self.config.timezone_name)
                .dt.floor("h")
            )
            df = df.dropna(subset = ["time_hour"])
            actual_values = df["power_avg"].values
            
            weather_df = self._get_past_weather()
            if weather_df is None or weather_df.empty:
                print(f"[{current_time}] 无法获取天气数据")
                return False
            
            weather_df = weather_df.copy()
            weather_df["time_hour"] = pd.to_datetime(weather_df["time_hour"], errors = "coerce")
            weather_df = weather_df.dropna(subset=["time_hour"])
            df_with_weather = pd.merge(df[["time_hour", "power_avg"]], weather_df, 
                                       on = "time_hour", how = "inner")
            
            if df_with_weather.empty:
                print(f"[{current_time}] 无法合并功率和天气数据")
                return False
            
            baseline_predictions = self._get_baseline_prediction(df_with_weather)
            if baseline_predictions is None or len(baseline_predictions) == 0:
                print(f"[{current_time}] 无法计算基线模型预测值")
                return False
            
            feature_cols = [c for c in df_with_weather.columns if c not in ["time_hour", "power_avg"]]
            X = df_with_weather[feature_cols].astype(float).values
            trained_predictions = model.predict(X)
            
            min_length = min(len(actual_values), len(baseline_predictions), len(trained_predictions))
            actual_values = actual_values[:min_length]
            baseline_predictions = baseline_predictions[:min_length]
            trained_predictions = trained_predictions[:min_length]
            
            if min_length < 10:
                print(f"[{current_time}] 数据点数量不足 ({min_length}个)，无法计算权重")
                return False
            
            optimal_a = self._optimize_weight(actual_values, baseline_predictions, trained_predictions)
            
            success = self._save_weight_to_config(optimal_a)
            
            if success:
                print(f"[{current_time}] 权重计算完成，最优 a = {optimal_a:.4f}")
                return True
            else:
                print(f"[{current_time}] 权重保存失败")
                return False
        except Exception as e:
            china_tz = timezone(timedelta(hours=8))
            current_time = datetime.now(china_tz).strftime('%Y-%m-%d %H:%M:%S')
            print(f"[{current_time}] 计算权重时出错: {e}")
            return False

def main():
    load_dotenv()
    
    cfg = TrainConfig(
        influx_url=os.getenv("INFLUX_URL", "http://localhost:8181"),
        influx_token=os.getenv("INFLUX_TOKEN", ""),
        influx_database=os.getenv("INFLUX_DATABASE", "windfarm"),
        lookback_days=int(os.getenv("LOOKBACK_DAYS", "7")),
        model_dir = os.getenv("MODEL_DIR", "./models"),
    )
    trainer = GBDTTrainer(cfg)
    import sys
    turbine_id = sys.argv[1] if len(sys.argv) >= 2 else "T001"
    use_test_data = sys.argv[2].lower() == 'true' if len(sys.argv) >= 3 else False

    report = trainer.train(turbine_id = turbine_id, use_test_data=use_test_data)
    print("✅ Train finished:")
    for k, v in report.items():
        print(f"{k}: {v}")

if __name__ == "__main__":
    main()