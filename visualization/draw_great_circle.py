import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import numpy as np

def calculate_great_circle_points(lat1, lon1, lat2, lon2, num=1000):
    """
    计算两点之间的大圆航线中间点。
    """
    # 将角度转换为弧度
    lat1_rad, lon1_rad = np.radians([lat1, lon1])
    lat2_rad, lon2_rad = np.radians([lat2, lon2])

    # 计算大圆航线的角度差
    delta = np.arccos(
        np.sin(lat1_rad) * np.sin(lat2_rad) +
        np.cos(lat1_rad) * np.cos(lat2_rad) * np.cos(lon2_rad - lon1_rad)
    )

    # 生成插值比例
    f = np.linspace(0, 1, num)

    # 计算中间点
    points = []
    for frac in f:
        A = np.sin((1 - frac) * delta) / np.sin(delta)
        B = np.sin(frac * delta) / np.sin(delta)

        x = A * np.cos(lat1_rad) * np.cos(lon1_rad) + B * np.cos(lat2_rad) * np.cos(lon2_rad)
        y = A * np.cos(lat1_rad) * np.sin(lon1_rad) + B * np.cos(lat2_rad) * np.sin(lon2_rad)
        z = A * np.sin(lat1_rad) + B * np.sin(lat2_rad)

        lat_rad = np.arctan2(z, np.sqrt(x**2 + y**2))
        lon_rad = np.arctan2(y, x)

        points.append( (np.degrees(lat_rad), np.degrees(lon_rad)) )

    return points

# 定义起飞和降落机场的坐标（示例：北京首都国际机场和伦敦希思罗机场）
departure = {
    'name': 'PEK',
    'lat': 39.509167,   # 北京首都国际机场纬度
    'lon': 116.410556    # 北京首都国际机场经度
}

arrival = {
    'name': 'LHR',
    'lat': 30.228333,    # 伦敦希思罗机场纬度
    'lon': 120.431667     # 伦敦希思罗机场经度
}

# 计算大圆航线上的中间点
flight_path = calculate_great_circle_points(
    departure['lat'], departure['lon'],
    arrival['lat'], arrival['lon'],
    num=100
)

# 分离纬度和经度
lats, lons = zip(*flight_path)

# 使用 Cartopy 绘制地图和飞行轨迹
plt.figure(figsize=(12, 8))
ax = plt.axes(projection=ccrs.PlateCarree())

# 添加地图元素
ax.stock_img()  # 添加标准地图背景
ax.coastlines()  # 添加海岸线
ax.gridlines(draw_labels=True, dms=True, x_inline=False, y_inline=False)

# 绘制飞行轨迹
ax.plot(lons, lats, color='blue', linewidth=2, label='Flight Path')

# 标记起飞和降落机场
ax.plot(departure['lon'], departure['lat'], marker='o', color='red', markersize=5, label=departure['name'])
ax.plot(arrival['lon'], arrival['lat'], marker='o', color='green', markersize=5, label=arrival['name'])

# 添加机场名称标签
plt.text(departure['lon'] + 3, departure['lat'] + 3, departure['name'], color='red', fontsize=12)
plt.text(arrival['lon'] + 3, arrival['lat'] + 3, arrival['name'], color='green', fontsize=12)

# 设置标题和图例
plt.title(f"Flight Trajectory from {departure['name']} to {arrival['name']}")
plt.legend()

# 显示图像
plt.show()
