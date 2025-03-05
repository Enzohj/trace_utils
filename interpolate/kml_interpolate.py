from fastkml import kml
from geopy.distance import geodesic
from shapely.geometry import Point, LineString
from datetime import datetime, timedelta
from shapely.coords import CoordinateSequence
import numpy as np
from scipy.interpolate import pchip_interpolate
import simplekml
import xml.etree.ElementTree as ET

# import cartopy.crs as ccrs

# def read_kmll(kml_file):
#     namespaces = {
#         'kml': 'http://www.opengis.net/kml/2.2',
#         'gx': 'http://www.google.com/kml/ext/2.2'
#     }
#     airport_points = []
#     track_points = []

#     # Parse the KML file
#     tree = ET.parse(kml_file)  # Replace 'your_kml_file.kml' with the path to your KML file
#     root = tree.getroot()

#     kml_data = {'lat': [], 'lon': []}

#     for placemark in root.findall('.//kml:Placemark', namespaces):
#         # Extract Point coordinates
#         point = placemark.find('.//kml:Point/kml:coordinates', namespaces)
#         if point is not None:
#             coords_text = point.text.strip()
#             # Split the coordinates by comma and convert to float
#             coords = tuple(map(float, coords_text.split(',')))
#             airport_points.append(coords)
        
    
#     start_placemark, end_placemark = airport_points

#     lat1, lon1, lat2, lon2 = start_placemark[1], start_placemark[0], end_placemark[1], end_placemark[0]
#     track_points = calculate_great_circle_points(lat1, lon1, lat2, lon2, num=100)
#     for point in track_points:
#         kml_data['lat'].append(point[0])
#         kml_data['lon'].append(point[1])
#     return kml_data

# def calculate_great_circle_points(lat1, lon1, lat2, lon2, num=1000):
#     """
#     计算两点之间的大圆航线中间点。
#     """
#     # 将角度转换为弧度
#     lat1_rad, lon1_rad = np.radians([lat1, lon1])
#     lat2_rad, lon2_rad = np.radians([lat2, lon2])

#     # 计算大圆航线的角度差
#     delta = np.arccos(
#         np.sin(lat1_rad) * np.sin(lat2_rad) +
#         np.cos(lat1_rad) * np.cos(lat2_rad) * np.cos(lon2_rad - lon1_rad)
#     )

#     # 生成插值比例
#     f = np.linspace(0, 1, num)

#     # 计算中间点
#     points = []
#     for frac in f:
#         A = np.sin((1 - frac) * delta) / np.sin(delta)
#         B = np.sin(frac * delta) / np.sin(delta)

#         x = A * np.cos(lat1_rad) * np.cos(lon1_rad) + B * np.cos(lat2_rad) * np.cos(lon2_rad)
#         y = A * np.cos(lat1_rad) * np.sin(lon1_rad) + B * np.cos(lat2_rad) * np.sin(lon2_rad)
#         z = A * np.sin(lat1_rad) + B * np.sin(lat2_rad)

#         lat_rad = np.arctan2(z, np.sqrt(x**2 + y**2))
#         lon_rad = np.arctan2(y, x)

#         points.append( (np.degrees(lat_rad), np.degrees(lon_rad)) )

#     return points


EARTH_RADIUS = 6371e3 # meters
   
def read_kml(kml_file):
    namespaces = {
        'kml': 'http://www.opengis.net/kml/2.2',
        'gx': 'http://www.google.com/kml/ext/2.2'
    }
    airport_points = []
    track_points = []

    # Parse the KML file
    tree = ET.parse(kml_file)  # Replace 'your_kml_file.kml' with the path to your KML file
    root = tree.getroot()

    kml_data = {'lat': [], 'lon': []}

    for placemark in root.findall('.//kml:Placemark', namespaces):
        # Extract Point coordinates
        point = placemark.find('.//kml:Point/kml:coordinates', namespaces)
        if point is not None:
            coords_text = point.text.strip()
            # Split the coordinates by comma and convert to float
            coords = tuple(map(float, coords_text.split(',')))
            airport_points.append(coords)
        
        # Extract gx:Track coordinates
        track = placemark.find('.//gx:Track', namespaces)
        if track is not None:
            for gx_coord in track.findall('.//gx:coord', namespaces):
                coord_text = gx_coord.text.strip()
                # Split the coordinates by space and convert to float
                coords = tuple(map(float, coord_text.split()))
                track_points.append(coords)
    
    start_placemark, end_placemark = airport_points
    kml_data['lat'].append(start_placemark[1])
    kml_data['lon'].append(start_placemark[0])
    for point in track_points:
        kml_data['lat'].append(point[1])
        kml_data['lon'].append(point[0])
    kml_data['lat'].append(end_placemark[1])
    kml_data['lon'].append(end_placemark[0])
    return kml_data

# def read_kml(kml_file):
#     kml_data = {'lat': [], 'lon': []}
#     with open(kml_file, 'rt', encoding='utf-8') as f:
#         doc = f.read()
#     k = kml.KML()
#     k.from_string(doc.encode('utf-8'))
#     document = list(k.features())[0]
#     start_placemark, end_placemark, trace_placemark = list(document.features())
#     start_point = start_placemark.geometry
#     end_point = end_placemark.geometry
#     trace_point = trace_placemark.geometry.coords
#     kml_data['lat'].append(start_point.y)
#     kml_data['lon'].append(start_point.x)
#     for point in trace_point:
#         kml_data['lat'].append(point[1])
#         kml_data['lon'].append(point[0])
#     kml_data['lat'].append(end_point.y)
#     kml_data['lon'].append(end_point.x)
#     return kml_data

def calculate_distance(kml_data):
    kml_dist = np.zeros(len(kml_data['lat']))
    for i in range(len(kml_dist)-1):
        lat1 = np.radians(kml_data['lat'][i])
        lon1 = np.radians(kml_data['lon'][i])
        lat2 = np.radians(kml_data['lat'][i+1])
        lon2 = np.radians(kml_data['lon'][i+1])

        delta_lat = lat2-lat1
        delta_lon = lon2-lon1

        c = 2.0*np.arcsin(np.sqrt(np.sin(delta_lat/2.0)**2+np.cos(lat1)*np.cos(lat2)*np.sin(delta_lon/2.0)**2)) # haversine formula

        dist_latlon = EARTH_RADIUS*c # great-circle distance

        kml_dist[i+1] = dist_latlon

    return kml_dist.tolist()
    
def kml_interpolate(kml_data, res= 1900, num = None):
    dist = calculate_distance(kml_data)
    xi = np.cumsum(dist)
    yi = np.array([kml_data[i] for i in ('lat', 'lon') if kml_data[i]])

    num = num if num is not None else int(np.ceil(xi[-1]/res))

    x = np.linspace(xi[0], xi[-1], num=num, endpoint=True)
    y = pchip_interpolate(xi, yi, x, axis=1)

    kml_data_interp = {'lat': list(y[0, :]),
                       'lon': list(y[1, :])}

    return kml_data_interp

def main():
    import argparse

    parser = argparse.ArgumentParser(description='interpolate kml files using piecewise cubic Hermite splines')

    parser.add_argument('g', type=str, default='/Users/bytedance/Code/my/trace_utils/files/kml/flights/FlightAware_CBJ5302_ZSHC_ZLXY_20240607_interpolated.kml', help='GPX file')
    parser.add_argument('-r', '--res', type=float, default=1900, help='interpolation resolution in meters (default: 1)')
    parser.add_argument('-n', '--num', type=int, default=None, help='force point count in output (default: disabled)')

    args = parser.parse_args()

    kml_path = args.g
    kml_data = read_kml(kml_path)
    print('Read {} trackpoints from {}'.format(len(kml_data['lat']), kml_path))
    kml_data_inter = kml_interpolate(kml_data)

    assert len(kml_data_inter['lat']) == len(kml_data_inter['lon']), "Latitude and longitude lists must be of the same length."

    # 创建一个simplekml对象
    kml = simplekml.Kml()

    # 创建一个Placemark，其包含一个LineString
    linestring = kml.newlinestring(name="Path Placemark")

    # 设置LineString的坐标
    linestring.coords = list(zip(kml_data_inter['lon'], kml_data_inter['lat']))  # 组合成(lon, lat)的元组
    output_file = '{}_interpolated.kml'.format(kml_path.split('/')[-1].split('.')[0])
    print('Write {} trackpoints from {}'.format(len(kml_data_inter['lat']), output_file))

    # 保存KML文件
    kml.save(output_file)

if __name__ == '__main__':
    main()
    # read_kml('FlightAware_CBJ5302_ZSHC_ZLXY_20240607.kml')
