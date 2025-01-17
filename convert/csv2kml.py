import pandas as pd
import simplekml

# 加载 CSV 文件
csv_file = '/Users/hjx/Code/gpx-interpolate/gps-1720928340-0.csv'  # 替换为你的 CSV 文件路径
data = pd.read_csv(csv_file)

# 创建 KML 对象
kml = simplekml.Kml()

# 遍历每一行数据，提取经纬度并创建 KML 点
for index, row in data.iterrows():
    kml.newpoint(name=str(index),  # 使用索引作为名称，可以定制
                  coords=[(row['longitude'], row['latitude'])],
                  description=f"Timestamp: {row['timestamp_ms']}")

# 保存 KML 文件
kml_file = 'output.kml'  # 你想要保存的 KML 文件名
kml.save(kml_file)

print(f'KML 文件已保存为 {kml_file}')
