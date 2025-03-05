import numpy as np
from scipy.interpolate import pchip_interpolate
import simplekml
import xml.etree.ElementTree as ET

EARTH_RADIUS = 6371e3 # meters
   
def load_kml(kml_file):
    namespaces = {
        'kml': 'http://www.opengis.net/kml/2.2',
        'gx': 'http://www.google.com/kml/ext/2.2'
    }
    airport_points = []
    track_points = []

    tree = ET.parse(kml_file)  
    root = tree.getroot()

    kml_data = {'lat': [], 'lon': []}

    for placemark in root.findall('.//kml:Placemark', namespaces):
        name = placemark.find('kml:name', namespaces).text
        if 'Airport' in name:
            point = placemark.find('.//kml:Point/kml:coordinates', namespaces)
            if point is not None:
                coords_text = point.text.strip()
                coords = tuple(map(float, coords_text.split(',')))+ (name,)
                airport_points.append(coords)

        track = placemark.find('.//gx:Track', namespaces)
        if track is not None:
            for gx_coord in track.findall('.//gx:coord', namespaces):
                coord_text = gx_coord.text.strip()
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
    print('Finish loading KML file from {}'.format(kml_file))
    print(f'Departure from: {start_placemark[3]}')
    print(f'Arrival at: {end_placemark[3]}')
    print('Read {} trackpoints'.format(len(kml_data['lat'])))
    return kml_data, airport_points


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

        dist_latlon = EARTH_RADIUS*c 

        kml_dist[i+1] = dist_latlon

    return kml_dist.tolist()
    
def interpolate(kml_data, res= 1900, num = None):
    dist = calculate_distance(kml_data)
    xi = np.cumsum(dist)
    yi = np.array([kml_data[i] for i in ('lat', 'lon') if kml_data[i]])

    num = num if num is not None else int(np.ceil(xi[-1]/res))

    x = np.linspace(xi[0], xi[-1], num=num, endpoint=True)
    y = pchip_interpolate(xi, yi, x, axis=1)

    kml_data_inter = {'lat': list(y[0, :]),
                       'lon': list(y[1, :])}

    assert len(kml_data_inter['lat']) == len(kml_data_inter['lon']), "Latitude and longitude lists must be of the same length."

    return kml_data_inter

def write_kml(kml_data_inter, airport_points, kml_path):
    kml = simplekml.Kml()
    airport_d, airport_a = airport_points

    point1 = kml.newpoint(name=airport_d[3], coords=[(airport_d[0], airport_d[1])])
    point2 = kml.newpoint(name=airport_a[3], coords=[(airport_a[0], airport_a[1])])

    linestring = kml.newlinestring(name="Flight Trace")

    linestring.coords = list(zip(kml_data_inter['lon'], kml_data_inter['lat']))  
    print('Write {} trackpoints to {}'.format(len(kml_data_inter['lat']), kml_path))
    kml.save(kml_path)

if __name__ == '__main__':

    kml_path = '/Users/bytedance/Code/my/flight/FlightAware_CCA725_ZSHC_RJBB_20240915.kml'
    kml_data, airport_points = load_kml(kml_path)
    kml_data_inter = interpolate(kml_data)
    save_path = '{}_interpolated.kml'.format(kml_path.split('/')[-1].split('.')[0])
    write_kml(kml_data_inter, airport_points, save_path)
