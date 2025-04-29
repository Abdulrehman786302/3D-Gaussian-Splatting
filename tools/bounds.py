import numpy as np
import os

# Ask the user for the base path and scene name
base_path = input("Enter the base path (e.g., C:/Users/user/Documents/FSGS/dataset/nerf_llff_data): ")
scene = input("Enter the scene name (e.g., chair): ")

# Construct the paths based on user input
images_txt_path = os.path.join(base_path, scene, 'sparse', '0', 'images.txt')
points3D_txt_path = os.path.join(base_path, scene, 'sparse', '0', 'points3D.txt')
output_path = os.path.join(base_path, scene, 'poses_bounds.npy')

# Read camera poses from images.txt
poses = []
with open(images_txt_path, 'r') as f:
    for line in f:
        if line.startswith('#') or not line.strip():
            continue
        elements = line.split()
        qw, qx, qy, qz = map(float, elements[1:5])
        tx, ty, tz = map(float, elements[5:8])
        pose = np.array([qw, qx, qy, qz, tx, ty, tz])
        poses.append(pose)

poses = np.array(poses)

# Load points3D from points3D.txt (just for bounds, not used for poses directly)
points3D = []
with open(points3D_txt_path, 'r') as f:
    for line in f:
        if line.startswith('#') or not line.strip():
            continue
        elements = line.split()
        x, y, z = map(float, elements[1:4])
        points3D.append([x, y, z])

points3D = np.array(points3D)
min_bounds = np.min(points3D, axis=0)
max_bounds = np.max(points3D, axis=0)
bounds = np.array([min_bounds, max_bounds])

# Save the poses_bounds.npy file
np.save(output_path, np.hstack([poses, bounds]))

print(f"poses_bounds.npy generated successfully at {output_path}.")
