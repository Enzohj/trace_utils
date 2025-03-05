import xml.etree.ElementTree as ET
import folium
import numpy as np

# 解析KML文件
def parse_kml_coordinates(kml_path):
    with open(kml_path, 'r', encoding='utf-8') as f:
        kml_content = f.read()
    # 解析XML
    root = ET.fromstring(kml_content)
    
    # 查找命名空间
    ns = {'kml': 'http://www.opengis.net/kml/2.2'}
    
    # 提取机场坐标
    airports = []
    for placemark in root.findall('.//kml:Placemark', ns):
        name = placemark.find('kml:name', ns).text
        if 'Airport' in name:
            coords = placemark.find('.//kml:coordinates', ns).text.strip().split(',')
            airports.append({
                'name': name,
                'coords': [float(coords[1]), float(coords[0])]  # [lat, lon]
            })
    
    # 提取航线坐标
    path_coords = []
    path = root.find('.//kml:LineString/kml:coordinates', ns).text.strip()
    for coord in path.split():
        lon, lat, _ = coord.split(',')
        path_coords.append([float(lat), float(lon)])
    
    return airports, path_coords

# 创建地图
def create_flight_map(airports, path_coords, kml_path):
    # 计算路径的中心点作为地图中心
    center_lat = np.mean([coord[0] for coord in path_coords])
    center_lon = np.mean([coord[1] for coord in path_coords])
    
    # 创建地图
    m = folium.Map(location=[center_lat, center_lon], zoom_start=5)
    
    # 添加机场标记
    for airport in airports:
        folium.Marker(
            location=airport['coords'],
            popup=airport['name'],
            icon=folium.Icon(color='red', icon='info-sign')
        ).add_to(m)
    
    # 添加航线
    folium.PolyLine(
        locations=path_coords,
        weight=2,
        color='blue',
        opacity=0.8
    ).add_to(m)

    m.save(kml_path)
    print('Save visualization map to {}'.format(kml_path))

    
    return m


if __name__ == '__main__':
    kml_path = '/Users/bytedance/Code/my/flight/FlightAware_CCA725_ZSHC_RJBB_20240915_interpolated.kml'

    airports, path_coords = parse_kml_coordinates(kml_path)
    save_path = '{}_visualization.html'.format(kml_path.split('/')[-1].split('.')[0].split('_interpolated')[0])
    flight_map = create_flight_map(airports, path_coords, save_path)
