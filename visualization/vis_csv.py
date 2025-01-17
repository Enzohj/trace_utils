import pandas as pd
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature

# 加载数据
filename = 'data.csv'  # 替换为你的CSV文件的实际路径
df = pd.read_csv(filename)

# 创建地图投影
fig = plt.figure(figsize=(10, 5))
ax = plt.axes(projection=ccrs.PlateCarree())

# 添加彩色背景图层（例如添加陆地和海洋特征）
ax.add_feature(cfeature.LAND, zorder=0)  # 陆地
ax.add_feature(cfeature.OCEAN, zorder=0) # 海洋
ax.add_feature(cfeature.COASTLINE, zorder=1)  # 海岸线
ax.add_feature(cfeature.BORDERS, linestyle=':', zorder=1)  # 国界线

# 绘制数据点，并保留返回的collection用于colorbar
scatter = ax.scatter(df['longitude'], df['latitude'],
                     c=df['accuracy'],  # 使用accuracy列的值进行颜色映射
                     cmap='viridis',  # 颜色映射方式
                     marker='o',  # 标记样式
                     transform=ccrs.PlateCarree(), zorder=2)  # 指定绘图使用的坐标系统

# 添加颜色条
plt.colorbar(scatter, ax=ax, shrink=0.5, label='Accuracy')

# 设置地图范围
ax.set_global()

# 添加标题
plt.title('Data Points Visualization')

# 保存到文件
plt.savefig('colorful_map_visualization.png', dpi=300)

# 显示图片
plt.show()
