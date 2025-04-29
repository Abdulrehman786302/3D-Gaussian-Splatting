import os
import numpy as np
import os
import sys
import imageio
import skimage.transform


import colmap_read_model as read_model


# Prompt user for the file path
camerasfile = input("Please enter the path to the cameras.bin file: ")

# Check if the file exists at the given path
if not os.path.exists(camerasfile):
    print("The specified file does not exist. Please check the path and try again.")
else:
    # Read the camera data from the file
    camdata = read_model.read_cameras_binary(camerasfile)
    list_of_keys = list(camdata.keys())
    print(list_of_keys)
    cam = camdata[list_of_keys[0]]
    print(list_of_keys)
    print( 'Cameras', len(cam))
    
    # Now you can proceed with the rest of your code
    for cam_id, cam in camdata.items():
        print(f"Camera ID: {cam_id}")
        print(f"  Model: FOV")
        print(f"  Resolution: {cam.width}x{cam.height}")
        print(f"  Focal Length: {cam.params[0]}")
        print(f"  Other Parameters: {cam.params[1:]}")
        print()
