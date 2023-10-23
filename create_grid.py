import numpy as np

# Initialize parameters
num_vertices_x = 64
num_vertices_z = 75
side_length = 1.0
height = np.sqrt(3) / 2 * side_length

# Initialize point cloud data list
points = []

# Initialize RGB color (white)
r, g, b = 255, 255, 255
rgb = (r << 16) | (g << 8) | b

# Calculate the total width and length of the grid
total_width = num_vertices_x * side_length
total_length = (num_vertices_z - 1) * height

# Calculate offsets to center the grid at X=0, Z=0
offset_x = -total_width / 2 + side_length / 2
offset_z = -total_length / 2 + height / 2

# Generate points
for i in range(num_vertices_z):
    for j in range(num_vertices_x):
        x = j * side_length + offset_x
        z = i * height + offset_z
        y = 0

        # Offset every other row by half a side length to form equilateral triangles
        if i % 2 == 1:
            x += side_length / 2

        # Append point coordinates and RGB value to list
        points.append([x, y, z, rgb])

# Convert to numpy array for easier manipulation
points = np.array(points)

# Display some sample points for verification
points[:10], points.shape


# Generate the PCD file header
header = """# .PCD v0.7 - Point Cloud Data file format
VERSION 0.7
FIELDS x y z rgb
SIZE 4 4 4 4
TYPE F F F U
COUNT 1 1 1 1
WIDTH {width}
HEIGHT 1
VIEWPOINT 0 0 0 1 0 0 0
POINTS {points}
DATA ascii
""".format(width=points.shape[0], points=points.shape[0])

# Prepare the PCD file content
pcd_content = header
for point in points:
    pcd_content += " ".join(map(str, point)) + "\n"

# Write the PCD content to a file
pcd_file_path = '/mnt/data/equilateral_triangle_grid.pcd'
with open(pcd_file_path, 'w') as f:
    f.write(pcd_content)

pcd_file_path




# -----------------------------------------------


from PIL import Image

# Load the image
image_path = '/assets/Roden image transparent.png'
image = Image.open(image_path).convert("RGBA")

image_np = np.array(image)      # Convert image to numpy array

image_width, image_height = image.size

image_width, image_height, image_np.shape       # Show some basic info


# Calculate scaling factor and offsets to align image and grid
scaling_factor_x = total_width / image_width
scaling_factor_z = total_length / image_height

offset_x_img = total_width / 2
offset_z_img = total_length / 2

new_rgb_values = []

# Iterate through each point in the grid
for point in points:
    x, y, z, _ = point
    
    # Transform grid coordinates to image coordinates
    x_img = int((x + offset_x_img) / scaling_factor_x)
    z_img = int((z + offset_z_img) / scaling_factor_z)
    
    # Define the 1 unit square around the vertex in image coordinates
    x_min = max(0, x_img - int(1 / scaling_factor_x))
    x_max = min(image_width, x_img + int(1 / scaling_factor_x))
    z_min = max(0, z_img - int(1 / scaling_factor_z))
    z_max = min(image_height, z_img + int(1 / scaling_factor_z))
    
    # Extract the region and calculate the average color
    region = image_np[z_min:z_max, x_min:x_max]
    alpha_channel = region[:,:,3]
    
    # Exclude transparent pixels (alpha = 0)
    non_transparent_pixels = region[alpha_channel > 0][:,:3]
    
    if non_transparent_pixels.size > 0:
        avg_color = np.mean(non_transparent_pixels, axis=0).astype(int)
        r, g, b = avg_color
        new_rgb = (r << 16) | (g << 8) | b
    else:
        # If all pixels in the region are transparent, set color to NaN
        new_rgb = np.nan

    new_rgb_values.append(new_rgb)

# Replace old RGB values with new ones
points[:, 3] = new_rgb_values

# Remove rows with NaN values (corresponding to transparent areas in the image)
points = points[~np.isnan(points[:, 3])]

# Display some sample points for verification and the new shape of the points array
points[:10], points.shape


# Update the PCD file header with new point count
header = header.format(width=points.shape[0], points=points.shape[0])

# Prepare the PCD file content
new_pcd_content = header
for point in points:
    new_pcd_content += " ".join(map(str, point)) + "\n"

# Write the updated PCD content to a new file
new_pcd_file_path = '/mnt/data/equilateral_triangle_grid_colored.pcd'
with open(new_pcd_file_path, 'w') as f:
    f.write(new_pcd_content)

new_pcd_file_path
