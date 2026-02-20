from weather import Weather
import pandas as pd
import numpy as np
import os

def get_baseline_power(weather_df, base_line_file):
    """
    根据天气数据使用基线模型计算功率
    """
    base_line_df = pd.read_csv(base_line_file, header=None, names=['wind_speed', 'value'])
    
    wind_speeds = weather_df['wind_speed_10m'].values
    base_wind_speeds = base_line_df['wind_speed'].values
    base_values = base_line_df['value'].values
    
    interpolated_values = np.interp(wind_speeds, base_wind_speeds, base_values)
    interpolated_values = interpolated_values * 1000
    
    return interpolated_values

def add_noise(power_values, noise_percent=0.05):
    """
    为功率数据添加指定百分比的噪声
    """
    noise = np.random.normal(0, noise_percent, size=len(power_values))
    noisy_power = power_values * (1 + noise)
    
    return noisy_power

def main():
    print("开始获取过去7天的小时天气数据...")
    
    weather = Weather()
    weather_df = weather.get_past_weather()
    
    if weather_df.empty:
        print("未获取到天气数据")
        return
    
    print(f"成功获取 {len(weather_df)} 条天气数据")
    
    current_dir = os.path.dirname(os.path.abspath(__file__))
    base_line_file = os.path.join(current_dir, "base_line.csv")
    
    if not os.path.exists(base_line_file):
        print(f"基线文件不存在: {base_line_file}")
        return
    
    print("使用基线模型计算功率...")
    baseline_power = get_baseline_power(weather_df, base_line_file)
    
    print("添加5%的噪声...")
    noisy_power = add_noise(baseline_power, noise_percent=0.05)
    
    result_df = pd.DataFrame({
        'time': weather_df['date'],
        'power': noisy_power
    })
    
    output_file = os.path.join(current_dir, "power_with_noise.csv")
    result_df.to_csv(output_file, index=False)
    
    print(f"数据已保存到: {output_file}")
    print(f"共 {len(result_df)} 条记录")
    print(f"功率范围: {result_df['power'].min():.2f} - {result_df['power'].max():.2f}")
    print(f"平均功率: {result_df['power'].mean():.2f}")

if __name__ == "__main__":
    main()
