import os
import shutil
import numpy as np
import sys
import sqlite3
import subprocess
from pathlib import Path
import logging
from concurrent.futures import ThreadPoolExecutor

IS_PYTHON3 = sys.version_info[0] >= 3
MAX_IMAGE_ID = 2**31 - 1

CREATE_CAMERAS_TABLE = """CREATE TABLE IF NOT EXISTS cameras (
    camera_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    model INTEGER NOT NULL,
    width INTEGER NOT NULL,
    height INTEGER NOT NULL,
    params BLOB,
    prior_focal_length INTEGER NOT NULL)"""

CREATE_DESCRIPTORS_TABLE = """CREATE TABLE IF NOT EXISTS descriptors (
    image_id INTEGER PRIMARY KEY NOT NULL,
    rows INTEGER NOT NULL,
    cols INTEGER NOT NULL,
    data BLOB,
    FOREIGN KEY(image_id) REFERENCES images(image_id) ON DELETE CASCADE)"""

CREATE_IMAGES_TABLE = """CREATE TABLE IF NOT EXISTS images (
    image_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    name TEXT NOT NULL UNIQUE,
    camera_id INTEGER NOT NULL,
    prior_qw REAL,
    prior_qx REAL,
    prior_qy REAL,
    prior_qz REAL,
    prior_tx REAL,
    prior_ty REAL,
    prior_tz REAL,
    CONSTRAINT image_id_check CHECK(image_id >= 0 and image_id < {}),
    FOREIGN KEY(camera_id) REFERENCES cameras(camera_id))
""".format(MAX_IMAGE_ID)

CREATE_TWO_VIEW_GEOMETRIES_TABLE = """
CREATE TABLE IF NOT EXISTS two_view_geometries (
    pair_id INTEGER PRIMARY KEY NOT NULL,
    rows INTEGER NOT NULL,
    cols INTEGER NOT NULL,
    data BLOB,
    config INTEGER NOT NULL,
    F BLOB,
    E BLOB,
    H BLOB,
    qvec BLOB,
    tvec BLOB)
"""

CREATE_KEYPOINTS_TABLE = """CREATE TABLE IF NOT EXISTS keypoints (
    image_id INTEGER PRIMARY KEY NOT NULL,
    rows INTEGER NOT NULL,
    cols INTEGER NOT NULL,
    data BLOB,
    FOREIGN KEY(image_id) REFERENCES images(image_id) ON DELETE CASCADE)
"""

CREATE_MATCHES_TABLE = """CREATE TABLE IF NOT EXISTS matches (
    pair_id INTEGER PRIMARY KEY NOT NULL,
    rows INTEGER NOT NULL,
    cols INTEGER NOT NULL,
    data BLOB)"""

CREATE_NAME_INDEX = \
    "CREATE UNIQUE INDEX IF NOT EXISTS index_name ON images(name)"

CREATE_ALL = "; ".join([ 
    CREATE_CAMERAS_TABLE,
    CREATE_IMAGES_TABLE,
    CREATE_KEYPOINTS_TABLE,
    CREATE_DESCRIPTORS_TABLE,
    CREATE_MATCHES_TABLE,
    CREATE_TWO_VIEW_GEOMETRIES_TABLE,
    CREATE_NAME_INDEX
])

def array_to_blob(array):
    if IS_PYTHON3:
        return array.tobytes()  # Use tobytes() in Python 3
    else:
        return np.getbuffer(array)

def blob_to_array(blob, dtype, shape=(-1,)):
    if IS_PYTHON3:
        return np.frombuffer(blob, dtype=dtype).reshape(*shape)  # Use frombuffer in Python 3
    else:
        return np.frombuffer(blob, dtype=dtype).reshape(*shape)

class COLMAPDatabase(sqlite3.Connection):
    @staticmethod
    def connect(database_path):
        return sqlite3.connect(database_path, factory=COLMAPDatabase)

    def __init__(self, *args, **kwargs):
        super(COLMAPDatabase, self).__init__(*args, **kwargs)
        self.create_tables = lambda: self.executescript(CREATE_ALL)

    def update_camera(self, model, width, height, params, camera_id):
        params = np.asarray(params, np.float64)
        cursor = self.execute(
            "UPDATE cameras SET model=?, width=?, height=?, params=?, prior_focal_length=1 WHERE camera_id=?",
            (model, width, height, array_to_blob(params), camera_id))
        return cursor.lastrowid

def round_python3(number):
    rounded = round(number)
    if abs(number - rounded) == 0.5:
        return 2.0 * round(number / 2.0)
    return rounded

def run_command(command):
    """Run a command and handle errors."""
    try:
        result = subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print(f"Command '{' '.join(command)}' executed successfully.")
        return result
    except subprocess.CalledProcessError as e:
        print(f"Error occurred while running command: {' '.join(command)}")
        print(f"Error details: {e.stderr.decode()}")
        sys.exit(1)  # Exit the script if command fails

def check_disk_space(path, required_space_gb):
    """Check if there is enough disk space."""
    total, used, free = shutil.disk_usage(path)
    free_gb = free // (2**30)  # Convert bytes to GB
    if free_gb < required_space_gb:
        print(f"Warning: Not enough disk space! Required: {required_space_gb} GB, Available: {free_gb} GB")
        sys.exit(1)  # Exit script if not enough space

def create_directory(directory_path):
    """Create directory if it does not exist."""
    directory = Path(directory_path)
    if not directory.exists():
        print(f"Creating directory: {directory}")
        directory.mkdir(parents=True, exist_ok=True)
    else:
        print(f"Directory already exists: {directory}")

def file_exists(filepath):
    """Check if a file exists."""
    if not os.path.isfile(filepath):
        print(f"Error: File does not exist: {filepath}")
        sys.exit(1)
    return True

def copy_if_not_exists(src, dst):
    """Copy file only if it does not exist."""
    if not os.path.exists(dst):
        shutil.copy(src, dst)
        print(f"Copied: {src} -> {dst}")
    else:
        print(f"Skipped: {src} (file already exists)")

def process_image(img_name):
    """Process a single image (e.g., copy, feature extraction)."""
    copy_if_not_exists(os.path.join('..', 'images', img_name), os.path.join('images', img_name))

def pipeline(scene, base_path, n_views):
    llffhold = 8
    view_path = str(n_views) + '_views'
    os.chdir(os.path.join(base_path, scene))
    
    # Ensure directories exist
    create_directory(view_path)
    os.chdir(view_path)
    create_directory('created')
    create_directory('triangulated')
    create_directory('images')
    
    # Convert COLMAP model
    #run_command(['colmap', 'model_converter', '--input_path', '../sparse/0/', '--output_path', '../sparse/0/', '--output_type', 'TXT'])
    
    images = {}
    with open('../sparse/0/images.txt', "r") as fid:
        while True:
            line = fid.readline()
            if not line:
                break
            line = line.strip()
            if len(line) > 0 and line[0] != "#":
                elems = line.split()
                image_id = int(elems[0])
                qvec = np.array(tuple(map(float, elems[1:5])))
                tvec = np.array(tuple(map(float, elems[5:8])))
                camera_id = int(elems[8])
                image_name = elems[9]
                fid.readline().split()
                images[image_name] = elems[1:]
    
    img_list = sorted(images.keys(), key=lambda x: x)
    train_img_list = [c for idx, c in enumerate(img_list) if idx % llffhold != 0]
    if n_views > 0:
        idx_sub = [round_python3(i) for i in np.linspace(0, len(train_img_list)-1, n_views)]
        train_img_list = [c for idx, c in enumerate(train_img_list) if idx in idx_sub]
    
    # Copy image files using parallelization
    with ThreadPoolExecutor(max_workers=4) as executor:
        executor.map(process_image, train_img_list)
    
    shutil.copy('../sparse/0/cameras.txt', 'created/.')
    with open('created/points3D.txt', "w") as fid:
        pass
    
    # Run COLMAP feature extractor and matcher
    run_command(['colmap', 'feature_extractor','--database_path', 'database.db','--image_path', 'images','--SiftExtraction.max_image_size' ,'4032', '--SiftExtraction.max_num_features', '32768', '--SiftExtraction.estimate_affine_shape', '1', '--SiftExtraction.domain_size_pooling', '1'])
    run_command(['colmap', 'exhaustive_matcher', '--database_path', 'database.db', '--SiftMatching.guided_matching', '1', '--SiftMatching.max_num_matches', '32768'])

    db = COLMAPDatabase.connect('database.db')
    db_images = db.execute("SELECT * FROM images")
    img_rank = [db_image[1] for db_image in db_images]
    print(img_rank)
    
    ## Write out the images file
    with open('created/images.txt', "w") as fid:
        for idx, img_name in enumerate(img_rank):
            print(img_name)
            data = [str(1 + idx)] + [' ' + item for item in images[os.path.basename(img_name)]] + ['\n\n']
            fid.writelines(data)

    # Command for point triangulation
    run_command(['colmap', 'point_triangulator','--database_path', 'database.db','--image_path', 'images','--input_path', 'created','--output_path', 'triangulated','--Mapper.ba_local_max_num_iterations', '40','--Mapper.ba_local_max_refinements', '3','--Mapper.ba_global_max_num_iterations', '100'])
    # Command for model conversion
    run_command(['colmap', 'model_converter','--input_path', 'triangulated','--output_path', 'triangulated','--output_type', 'TXT'])
    # Command for image undistortion
    run_command(['colmap', 'image_undistorter','--image_path', 'images','--input_path', 'triangulated','--output_path', 'dense'])
    # Command for patch match stereo
    run_command(['colmap', 'patch_match_stereo','--workspace_path', 'dense'])
    # Command for stereo fusion
    run_command(['colmap', 'stereo_fusion','--workspace_path', 'dense','--output_path', 'dense/fused.ply'])

# Prompt user for inputs
base_path = input("Enter the base path (e.g., C:/Users/yourusername/Documents/dataset/nerf_llff_data): ")
scene = input("Enter the scene name (e.g., chair): ")
n_views = int(input("Enter the number of views: "))

# Run the pipeline with the user-provided values
pipeline(scene, base_path, n_views)
