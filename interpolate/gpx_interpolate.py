# imports
import gpxpy

import numpy as np

from datetime import datetime, tzinfo
from typing import Dict, List, Union, Optional

from scipy.interpolate import pchip_interpolate

# types
GPXData = Dict[str, Union[List[float], tzinfo, None]]

# globals
EARTH_RADIUS = 6371e3 # meters
EPS = 1e-6 # seconds

# functions
def gpx_interpolate(gpx_data: GPXData, res: float = 1.0, num: Optional[int] = None) -> GPXData:
    """
    Returns gpx_data interpolated with a spatial resolution res using piecewise cubic Hermite splines.

    if num is passed, gpx_data is interpolated to num points and res is ignored.
    """

    if all(gpx_data[i] in (None, []) for i in ('lat', 'lon', 'ele', 'tstamp')):
        return gpx_data

    _gpx_data = gpx_remove_duplicates(gpx_data)
    _gpx_dist = gpx_calculate_distance(_gpx_data, use_ele=True)

    xi = np.cumsum(_gpx_dist)
    yi = np.array([_gpx_data[i] for i in ('lat', 'lon', 'ele', 'tstamp') if _gpx_data[i]])

    num = num if num is not None else int(np.ceil(xi[-1]/res))

    x = np.linspace(xi[0], xi[-1], num=num, endpoint=True)
    y = pchip_interpolate(xi, yi, x, axis=1)

    gpx_data_interp = {'lat': list(y[0, :]),
                       'lon': list(y[1, :]),
                       'ele': list(y[2, :]) if gpx_data['ele'] else None,
                       'tstamp': list(y[-1, :]) if gpx_data['tstamp'] else None,
                       'tzinfo': gpx_data['tzinfo']}

    return gpx_data_interp

def gpx_calculate_distance(gpx_data: GPXData, use_ele: bool = False) -> List[float]:
    """
    Returns the distance between GPX trackpoints.

    if use_ele is True and gpx_data['ele'] is not None, the elevation data is used to compute the distance.
    """

    gpx_dist = np.zeros(len(gpx_data['lat']))

    for i in range(len(gpx_dist)-1):
        lat1 = np.radians(gpx_data['lat'][i])
        lon1 = np.radians(gpx_data['lon'][i])
        lat2 = np.radians(gpx_data['lat'][i+1])
        lon2 = np.radians(gpx_data['lon'][i+1])

        delta_lat = lat2-lat1
        delta_lon = lon2-lon1

        c = 2.0*np.arcsin(np.sqrt(np.sin(delta_lat/2.0)**2+np.cos(lat1)*np.cos(lat2)*np.sin(delta_lon/2.0)**2)) # haversine formula

        dist_latlon = EARTH_RADIUS*c # great-circle distance

        if gpx_data['ele'] and use_ele:
            dist_ele = gpx_data['ele'][i+1]-gpx_data['ele'][i]

            gpx_dist[i+1] = np.sqrt(dist_latlon**2+dist_ele**2)
        else:
            gpx_dist[i+1] = dist_latlon

    return gpx_dist.tolist()

def gpx_calculate_speed(gpx_data: GPXData) -> List[float]:
    """
    Returns the speed between GPX trackpoints.
    """

    gpx_dist = gpx_calculate_distance(gpx_data, use_ele=True)

    gpx_dtstamp = np.diff(gpx_data['tstamp'], prepend=gpx_data['tstamp'][0])
    gpx_dtstamp[gpx_dtstamp < EPS] = np.nan

    gpx_speed = np.nan_to_num(gpx_dist/gpx_dtstamp, nan=0.0)

    return gpx_speed.tolist()

def gpx_remove_duplicates(gpx_data: GPXData) -> GPXData:
    """
    Returns gpx_data where duplicate trackpoints are removed.
    """

    gpx_dist = gpx_calculate_distance(gpx_data, use_ele=False)

    i_dist = np.concatenate(([0], np.nonzero(gpx_dist)[0])) # keep gpx_dist[0] = 0.0

    if len(i_dist) == len(gpx_dist):
        return gpx_data

    gpx_data_nodup = {'lat': [], 'lon': [], 'ele': [], 'tstamp': [], 'tzinfo': gpx_data['tzinfo']}

    for k in ('lat', 'lon', 'ele', 'tstamp'):
        gpx_data_nodup[k] = [gpx_data[k][i] for i in i_dist] if gpx_data[k] else None

    return gpx_data_nodup


def gpx_read(gpx_file: str) -> GPXData:
    """
    Returns a GPXData structure from a GPX file.
    """

    gpx_data = {'lat': [], 'lon': [], 'ele': [], 'tstamp': [], 'tzinfo': None}

    i = 0
    i_latlon = []
    i_tstamp = []

    with open(gpx_file, 'r') as file:
        gpx = gpxpy.parse(file)
        start = gpx.waypoints[0]
        end = gpx.waypoints[-1]

        for track in gpx.tracks:
            for segment in track.segments:
                for point in segment.points:
                    gpx_data['lat'].append(point.latitude)
                    gpx_data['lon'].append(point.longitude)

                    i_latlon.append(i)

                    try:
                        gpx_data['ele'].append(point.elevation)
                    except:
                        pass

                    try:
                        gpx_data['tstamp'].append(point.time.timestamp())
                    except:
                        pass
                    else:
                        if not gpx_data['tzinfo']:
                            gpx_data['tzinfo'] = point.time.tzinfo

                        i_tstamp.append(i)

                    i += 1

    # remove trackpoints without tstamp
    if i_tstamp and not len(i_latlon) == len(i_tstamp):
        for k in ('lat', 'lon', 'ele', 'tstamp'):
            gpx_data[k] = [gpx_data[k][i] for i in i_tstamp] if gpx_data[k] else None
    gpx_data['lat'].insert(0, start.latitude)
    gpx_data['lon'].insert(0, start.longitude)
    gpx_data['ele'].insert(0, start.elevation)
    gpx_data['tstamp'].insert(0, 0)
    gpx_data['lat'].append(end.latitude)
    gpx_data['lon'].append(end.longitude)
    gpx_data['ele'].append(end.elevation)
    gpx_data['tstamp'].append(gpx_data['tstamp'][-1]+1)

    return gpx_data


def gpx_write(gpx_file: str, gpx_data: GPXData, write_speed: bool = False) -> None:
    """
    Writes a GPX file with a GPXData structure, including speed if write_speed is True.
    """

    if write_speed:
        if not gpx_data['tstamp']:
            raise ValueError('tstamp data is missing from gpx_data')

        gpx_speed = gpx_calculate_speed(gpx_data)

    gpx = gpxpy.gpx.GPX()
    gpx_track = gpxpy.gpx.GPXTrack()
    gpx_segment = gpxpy.gpx.GPXTrackSegment()

    gpx.tracks.append(gpx_track)
    gpx_track.segments.append(gpx_segment)

    for i in range(len(gpx_data['lat'])):
        lat = gpx_data['lat'][i]
        lon = gpx_data['lon'][i]
        ele = gpx_data['ele'][i] if gpx_data['ele'] else None
        time = datetime.fromtimestamp(gpx_data['tstamp'][i], tz=gpx_data['tzinfo']) if gpx_data['tstamp'] else None
        speed = gpx_speed[i] if write_speed else None

        gpx_point = gpxpy.gpx.GPXTrackPoint(lat, lon, ele, time, speed=speed)

        gpx_segment.points.append(gpx_point)

    try:
        with open(gpx_file, 'w') as file:
            file.write(gpx.to_xml(version='1.0' if write_speed else '1.1'))
    except:
        exit('ERROR Failed to save {}'.format(gpx_file))

    return


# main
def main():
    import argparse

    parser = argparse.ArgumentParser(description='interpolate GPX files using piecewise cubic Hermite splines')

    parser.add_argument('gpx_files', type=str, default='', help='GPX file')
    parser.add_argument('-r', '--res', type=float, default=1900, help='interpolation resolution in meters (default: 1)')
    parser.add_argument('-n', '--num', type=int, default=None, help='force point count in output (default: disabled)')
    parser.add_argument('-s', '--speed', action='store_true', help='save interpolated speed')

    args = parser.parse_args()



    if not args.gpx_files.endswith('_interpolated.gpx'):
        gpx_file = args.gpx_files
        gpx_data = gpx_read(gpx_file)

        print('Read {} trackpoints from {}'.format(len(gpx_data['lat']), gpx_file))

        gpx_data_nodup = gpx_remove_duplicates(gpx_data)

        if not len(gpx_data_nodup['lat']) == len(gpx_data['lat']):
            print('Removed {} duplicate trackpoint(s)'.format(len(gpx_data['lat'])-len(gpx_data_nodup['lat'])))

        gpx_data_interp = gpx_interpolate(gpx_data_nodup, args.res, args.num)

        output_file = '{}_interpolated.gpx'.format(gpx_file[:-4])

        gpx_write(output_file, gpx_data_interp, write_speed=args.speed)

        print('Saved {} trackpoints to {}'.format(len(gpx_data_interp['lat']), output_file))

if __name__ == '__main__':
    main()
