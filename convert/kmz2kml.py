import zipfile
import os

def kmz_to_kml(kmz_file, output_directory):
    # 确保输出目录存在
    os.makedirs(output_directory, exist_ok=True)

    # 使用 zipfile 解压 KMZ 文件
    with zipfile.ZipFile(kmz_file, 'r') as kmz:
        # 列出 KMZ 中的所有文件
        file_list = kmz.namelist()
        for file_name in file_list:
            # 检查每个文件名，通常 KML 文件的扩展名是 .kml
            if file_name.endswith('.kml'):
                # 解压 KML 文件到输出目录
                kmz.extract(file_name, output_directory)
                print(f'Extracted: {file_name}')

# 示例使用
kmz_file = '/Users/hjx/Code/gpx-interpolate/fow_gps_processer/tokaido_tokyoatami.kmz'  # 替换为您的 KMZ 文件路径
output_directory = '/Users/hjx/Code/gpx-interpolate/fow_gps_processer'  # 替换为您希望输出 KML 文件的目录

kmz_to_kml(kmz_file, output_directory)
