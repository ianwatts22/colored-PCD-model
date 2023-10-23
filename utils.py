import os
import numpy as np
from PIL import Image


 # Convert to 24-bit RGB color aka packed value
def pack_rgb(r, g, b):
    return (r << 16) | (g << 8) | b

def load_pcd(filename):
    points = []
    with open(filename, 'r') as f:
        reading_data = False
        for line in f:
            if reading_data:
                points.append(list(map(float, line.strip().split())))
            if line.startswith("DATA"):
                reading_data = True
    return np.array(points)



# =================================================
# import open3d as o3d

def manipulate_pcd(pcd):
    """
    Manipulate a PCD file.
    :param pcd: PCD file to manipulate.
    :return: Manipulated PCD file.
    """
    # This is a placeholder for your PCD manipulation code.
    # You can add any manipulation you want here.
    # For example, let's just translate the PCD for now.
    translation = np.array([1.0, 2.0, 3.0])
    pcd.translate(translation)
    return pcd

def save_pcd(pcd, file_path):
    """
    Save a PCD file to a given path.
    :param pcd: PCD file to save.
    :param file_path: Path to save the PCD file.
    """
    o3d.io.write_point_cloud(file_path, pcd)