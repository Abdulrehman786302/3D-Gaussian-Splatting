import json
import os
import numpy as np
import cv2
from database import COLMAPDatabase

def get_features(image_path, max_features=10000, octave_resolution=6):
    # Extract SIFT features from an image.
    image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    if image is None:
        raise ValueError(f"Failed to load image at {image_path}")
    
    sift = cv2.SIFT_create(nfeatures=max_features, nOctaveLayers=octave_resolution)
    keypoints, descriptors = sift.detectAndCompute(image, None)
    
    if len(keypoints) == 0 or descriptors is None:
        raise ValueError(f"No features detected in image at {image_path}")
    
    keypoints = np.array([[kp.pt[0], kp.pt[1]] for kp in keypoints])
    return keypoints, descriptors

def get_matches(descriptors1, descriptors2, ratio_thresh=0.65):
    bf = cv2.BFMatcher(cv2.NORM_L2, crossCheck=False)
    matches = bf.knnMatch(descriptors1, descriptors2, k=2)
    
    match_idx1, match_idx2 = [], []
    for m, n in matches:
        if m.distance < ratio_thresh * n.distance:
            match_idx1.append(m.queryIdx)
            match_idx2.append(m.trainIdx)

    matches = np.array([match_idx1, match_idx2]).T
    return matches

def create_database(database_path, image_names, camera_params_list):
    db = COLMAPDatabase.connect(database_path)
    db.create_tables()

    camera_ids = []
    
    for params in camera_params_list:
        model, width, height, params = params
        camera_id = db.add_camera(model, width, height, params)
        camera_ids.append(camera_id)

    keypoints_descriptors = [get_features(os.path.join(image_folder, image_name)) for image_name in image_names]
    keypoints_list, descriptors_list = zip(*keypoints_descriptors)
    
    for i, image_name in enumerate(image_names):
        db.add_image(image_name, camera_ids[i])

    for i in range(len(image_names) - 1):
        for j in range(i + 1, len(image_names)):
            matches = get_matches(descriptors_list[i], descriptors_list[j])
            db.add_two_view_geometry(i + 1, j + 1, matches)

    for i, keypoints in enumerate(keypoints_list):
        db.add_keypoints(i + 1, keypoints)

    db.commit()
    db.close()

    return db

def load_camera_params_from_json(json_file):
    with open(json_file, 'r') as f:
        data = json.load(f)
    
    camera_params_list = []
    
    for image_data in data['images']:
        fx = image_data['fx']
        fy = image_data['fy']
        cx = image_data['cx']
        cy = image_data['cy']
        
        # Read distortion from the JSON, defaulting to empty list if not provided
        distortion = image_data.get('distortion', [])
        
        # Use PINHOLE model (camera model 1) if distortion coefficients are provided
        if distortion:
            model = 1  # PINHOLE model (which uses 5 parameters + distortion)
            distortion=distortion[:4]
        elif distortion==0:
            model = 7  # Use FOV model if no distortion is given
            distortion=[0]

        # Combine the intrinsic parameters with the distortion coefficients
        params = np.array([fx, fy, cx, cy] + distortion)
        
        # Read the image resolution (height, width)
        image_name = image_data['image_name']
        image_path = os.path.join(image_folder, image_name)
        height, width = cv2.imread(image_path).shape[:2]
        
        camera_params_list.append((model, width, height, params))
    
    print(camera_params_list)  # For debugging, see the list of camera parameters
    return camera_params_list


if __name__ == '__main__':
    # Path to the folder
    base_folder_path= input("Enter the path where the images folder and calibration file are located: ")
    
    # Check if the base folder exists
    if not os.path.isdir(base_folder_path):
        exit(f"The folder {base_folder_path} does not exist. Please provide a valid folder path.")
    # Database file path
    
    db_path = os.path.join(base_folder_path, 'database.db')
    # Check if the database already exists
    if os.path.exists(db_path):
        print(f"Database already exists at {db_path}.")
        action = input("Do you want to delete the existing database (yes/no)? ").strip().lower()
        
        if action == 'yes':
            os.remove(db_path)
            print("Deleted the existing database. A new one will be created.")
        else:
            new_folder = input("Please specify a different folder path: ").strip()
            db_path = os.path.join(new_folder, 'database.db')

    
    # Define paths for the images folder and the calibration JSON file
    image_folder = os.path.join(base_folder_path, 'images')
    calibration_file = os.path.join(base_folder_path, 'camera_calibration.json')

    # Check if the 'images' folder and the calibration file exist
    if not os.path.isdir(image_folder):
        exit(f"The folder {image_folder} does not exist. Please provide a valid images folder.")
    if not os.path.isfile(calibration_file):
        exit(f"The file {calibration_file} does not exist. Please provide a valid calibration JSON file.")

    # Load camera parameters from the JSON file
    camera_params_list = load_camera_params_from_json(calibration_file)
    
    # Get image names from the folder (assuming image names are in the JSON file)
    image_names = [image_data['image_name'] for image_data in json.load(open(calibration_file))['images']]
    print("Image names:", image_names)

    # Automatically create the database file path in the same folder
    database_path = os.path.join(base_folder_path, 'database.db')
    if os.path.exists(database_path):
        exit(f"Database already exists at {database_path}. Please choose a different folder or delete the existing database.")

    # Create database with user inputs and camera parameters from JSON
    db = create_database(database_path, image_names, camera_params_list)
    print('Database created at:', database_path)
