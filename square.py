from PIL import Image
import numpy as np
import math
from utils import *

grid_width = 256
y_multiple = 1.7
search_radius_multiple = 0.1 / (grid_width / 256)
image = 'assets/image_transparent.png'
pcd = 'assets/PCD_ascii.pcd'

image = Image.open(image).convert("RGBA")
image_array = np.array(image)
image_width, image_height = image.size

aspect_ratio = image_width / image_height
grid_height = math.ceil(grid_width / aspect_ratio)
print(f'grid_width: {grid_width}, grid_height: {grid_height}, aspect_ratio: {aspect_ratio}')

# Calculate the step size for the grid based on the aspect ratio
grid_step = aspect_ratio / (grid_width - 1)
print(f'x_step: {grid_step}')

# Initialize the list to hold the PCD data
pcd_data = []

# Loop through each point in the grid
for i in range(grid_height):
    for j in range(grid_width):
        # Calculate the X and Z coordinates
        x = (j - (grid_width - 1) / 2) * grid_step
        z = (i - (grid_height - 1) / 2) * grid_step
        
        # Determine the corresponding image coordinates
        img_x = int((x + aspect_ratio / 2) * (image_width - 1) / aspect_ratio)
        img_y = int((z + 0.5) * (image_height - 1))
        
        # Extract the RGBA value from the image
        # ! probably want this to take the average of a unit wide square of pixels around the point
        r, g, b, a = image_array[img_y, img_x]
        
        # Skip transparent values
        if a == 0:
            continue
        
        # Append the point to the PCD data
        pcd_data.append([x, 0, z, pack_rgb(r, g, b)])

# Convert to NumPy array for easier handling later
pcd_data = np.array(pcd_data)
print(pcd_data[:5, :]) # print first few rows


# ===========================================================================
# =========================TOPOGRAPHICAL MATCHING============================
# ===========================================================================


# Function to load PCD file and return as a NumPy array
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

topo_pcd_data = load_pcd(pcd)

# Extract X, Y, Z coordinates
topo_x = topo_pcd_data[:, 0]
topo_y = topo_pcd_data[:, 1]
topo_z = topo_pcd_data[:, 2]

print(topo_pcd_data[:5, :])

# Create a KDTree for efficient nearest neighbor search
from scipy.spatial import cKDTree
topo_kdtree = cKDTree(topo_pcd_data[:, [0, 2]])  # Use only X and Z for matching

# Initialize array to hold the new Y-values
y_values = np.zeros(len(pcd_data))

# Define the initial search radius for Y-value
search_radius = search_radius_multiple * (grid_width / 64) * grid_step

# Search for nearest neighbors
for i, (x, _, z, _) in enumerate(pcd_data):
    # Query the KDTree to find points within the square
    points_in_square = topo_kdtree.query_ball_point([x, z], search_radius)

    # If no points found, progressively increase the search radius
    while not points_in_square and search_radius_multiple <= 3 * (grid_width / 64):
        search_radius_multiple += 0.1
        search_radius = max(search_radius_multiple * grid_step, search_radius_multiple * grid_step)
        points_in_square = topo_kdtree.query_ball_point([x, z], search_radius)

    if points_in_square:
        distances = [((x - topo_x[p]) ** 2 + (z - topo_z[p]) ** 2) for p in points_in_square]
        weights = [1 / d if d != 0 else 1 for d in distances]
        y_values[i] = np.average(topo_y[points_in_square], weights=weights)

# Search for nearest neighbors
""" for i, (x, _, z, _) in enumerate(pcd_data):
    # Query the KDTree to find points within the square
    points_in_square = topo_kdtree.query_ball_point([x, z], search_radius)

    # If no points found, progressively increase the search radius
    while not points_in_square and search_radius_multiple <= 3 * (grid_width / 64):
        search_radius_multiple += 1
        search_radius = max(search_radius_multiple * x_step, search_radius_multiple * z_step)
        points_in_square = topo_kdtree.query_ball_point([x, z], search_radius)

    if points_in_square:
        distances = [((x - topo_x[p]) ** 2 + (z - topo_z[p]) ** 2) for p in points_in_square]
        nearest_point = points_in_square[np.argmin(distances)]
        y_values[i] = topo_y[nearest_point] """
    
    # Filter out points that are outside the square bounds
""" filtered_points = [p for p in points_in_square if x_min <= topo_x[p] <= x_max and z_min <= topo_z[p] <= z_max]
    if filtered_points:
        distances = [((x - topo_x[p]) ** 2 + (z - topo_z[p]) ** 2) for p in filtered_points]
        nearest_point = filtered_points[np.argmin(distances)]
        new_y_values[i] = topo_y[nearest_point] """

# Update the Y-values in the original PCD data with the multiple
pcd_data[:, 1] = y_values * y_multiple
print(pcd_data[:5, :]) # Show first few rows to verify

unique_y_values = np.unique(pcd_data[:, 1])
print("Number of unique Y-values:", len(unique_y_values))
print("Number of points:", len(pcd_data))

def write_pcd_file(pcd_data, pcd_full_filename):
    # Write the PCD header
    with open(pcd_full_filename, 'w') as f:
        f.write("# .PCD v.7 - Point Cloud Data file format\n")
        f.write("VERSION .7\n")
        f.write("FIELDS x y z rgb\n")
        f.write("SIZE 4 4 4 4\n")
        f.write("TYPE F F F U\n")
        f.write("COUNT 1 1 1 1\n")
        f.write(f"WIDTH {len(pcd_data)}\n")
        f.write("HEIGHT 1\n")
        f.write("VIEWPOINT 0 0 0 1 0 0 0\n")
        f.write(f"POINTS {len(pcd_data)}\n")
        f.write("DATA ascii\n")
        
        # Write the PCD data
        for point in pcd_data:
            f.write(" ".join(map(str, point)) + "\n")

print(f'search_radius_multiple:{round(search_radius_multiple,1)}')
write_pcd_file(pcd_data, f'assets/writing/PCD_full_{grid_width}_{y_multiple}.pcd')