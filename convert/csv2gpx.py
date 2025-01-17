import pandas as pd
import xml.etree.ElementTree as ET

# 读取CSV文件
df = pd.read_csv('/Users/hjx/Code/gpx-interpolate/gps-1720928340-0.csv')

# 按时间排序
df['timestamp_ms'] = pd.to_datetime(df['timestamp_ms'], unit='ms')  # 转换为时间戳
df = df.sort_values(by='timestamp_ms')

# 创建GPX根元素
gpx = ET.Element('gpx', version='1.1', creator='YourScript')

# 添加轨迹
trk = ET.SubElement(gpx, 'trk')
trkseg = ET.SubElement(trk, 'trkseg')

# 遍历数据并添加点
for index, row in df.iterrows():
    trkpt = ET.SubElement(trkseg, 'trkpt', lat=str(row['latitude']), lon=str(row['longitude']))
    ET.SubElement(trkpt, 'ele').text = str(row['altitude'])
    ET.SubElement(trkpt, 'time').text = row['timestamp_ms'].isoformat() + 'Z'  # GPX要求UTC时间

# 保存GPX文件
tree = ET.ElementTree(gpx)
tree.write('output.gpx', xml_declaration=True, encoding='utf-8')

print("GPX文件已生成")
