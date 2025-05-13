import argparse
from interpolate import load_kml, interpolate, write_kml
from visualization import parse_kml_coordinates, create_flight_map


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('f', type=str, default='', help='kml file')
    parser.add_argument('-r', '--res', type=float, default=1900, help='interpolation resolution in meters (default: 1)')
    parser.add_argument('-n', '--num', type=int, default=None, help='force point count in output (default: disabled)')
    parser.add_argument('-v', '--visualize', action='store_true', help='visualize the flight path')
    args = parser.parse_args()
    return args


def main():
    args = parse_args()
    kml_path = args.f
    kml_data, airport_points = load_kml(kml_path)
    kml_data_inter = interpolate(kml_data, args.res, args.num)
    save_path = 'output/{}_interpolated.kml'.format(kml_path.split('/')[-1].split('.')[0])
    write_kml(kml_data_inter, airport_points, save_path)
    if args.visualize:
        airports, path_coords = parse_kml_coordinates(save_path)
        vis_path = 'output/{}_visualization.html'.format(kml_path.split('/')[-1].split('.')[0])
        flight_map = create_flight_map(airports, path_coords, vis_path)


if __name__ == '__main__':
    main()