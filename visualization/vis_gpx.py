import gpxpy
import matplotlib.pyplot as plt
import cartopy
import cartopy.crs as ccrs

# 读取GPX文件
with open('/Users/hjx/Code/gpx-interpolate/Archive/test_ori.gpx', 'r') as gpx_file:
    gpx = gpxpy.parse(gpx_file)

# 收集所有的轨迹点经纬度
lats = []
lons = []

for track in gpx.tracks:
    for segment in track.segments:
        for point in segment.points:
            lats.append(point.latitude)
            lons.append(point.longitude)

# 利用Cartopy设置地图投影
ax = plt.axes(projection=ccrs.PlateCarree())
ax.set_extent([min(lons), max(lons), min(lats), max(lats)])

# 添加地图特征
ax.coastlines(resolution='10m')
ax.add_feature(cartopy.feature.LAND)
ax.add_feature(cartopy.feature.OCEAN)
ax.add_feature(cartopy.feature.RIVERS)
ax.add_feature(cartopy.feature.LAKES)

# 绘制轨迹
plt.plot(lons, lats, color='red', linewidth=3, transform=ccrs.Geodetic())

# 显示地图
plt.show()
