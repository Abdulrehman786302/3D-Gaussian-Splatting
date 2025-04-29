import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Ellipse
import matplotlib
matplotlib.use('Agg')  # Use non-GUI backend
import matplotlib.pyplot as plt
# Step 1: Define the 3D points
points_3d = np.array([
    [1.0, 1.0, 2.0],  # Point 1
    [2.0, 1.5, 3.0],  # Point 2
    [3.0, 2.0, 4.0]   # Point 3
])
colors = np.array([
    [1.0, 0.0, 0.0],  # Red
    [0.0, 1.0, 0.0],  # Green
    [0.0, 0.0, 1.0]   # Blue
])

# Step 2: Camera parameters
focal_length = 1.0
camera_position = np.array([0.0, 0.0, 0.0])

# Step 3: Project 3D points to 2D using pinhole camera model
def project_to_2d(points_3d, focal_length):
    projected = []
    for x, y, z in points_3d:
        u = focal_length * x / z
        v = focal_length * y / z
        projected.append([u, v])
    return np.array(projected)

points_2d = project_to_2d(points_3d, focal_length)

# Step 4: Define Gaussian parameters (covariance scaling by depth)
def calculate_covariance(depth, base_scale=0.1):
    scale = base_scale / depth  # Smaller Gaussians for farther points
    return np.array([[scale, 0], [0, scale]])

covariances = [calculate_covariance(p[2]) for p in points_3d]

# Step 5: Render 2D Gaussian blobs
def plot_gaussian(ax, mean, covariance, color, alpha=0.5):
    """Plot a 2D Gaussian as an ellipse."""
    eigenvalues, eigenvectors = np.linalg.eigh(covariance)
    angle = np.degrees(np.arctan2(eigenvectors[1, 0], eigenvectors[0, 0]))
    width, height = 2 * np.sqrt(eigenvalues)
    ellipse = Ellipse(mean, width, height, angle=angle, facecolor=color, alpha=alpha)
    ax.add_patch(ellipse)


# Initialize plot
fig, ax = plt.subplots(figsize=(6, 6))
ax.set_xlim(-1, 1)
ax.set_ylim(-1, 1)
ax.set_aspect('equal')

# Plot each Gaussian
for mean, covariance, color in zip(points_2d, covariances, colors):
    plot_gaussian(ax, mean, covariance, color)

# Annotate points
for i, (u, v) in enumerate(points_2d):
    ax.text(u, v, f"P{i+1}", color="black", fontsize=10, ha='center')

plt.title("Gaussian Splatting Example")
plt.xlabel("u (image x)")
plt.ylabel("v (image y)")
plt.grid(True)
plt.show()
