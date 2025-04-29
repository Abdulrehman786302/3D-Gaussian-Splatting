import os
import subprocess
import sys

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

def create_sparse_model(base_path, scene):
    os.chdir(os.path.join(base_path, scene))

    # Ensure necessary directories exist
    if not os.path.exists("images"):
        os.makedirs("images")
    if not os.path.exists("sparse"):
        os.makedirs("sparse") 
    
    # Step 1: Create the COLMAP database
    print("Creating COLMAP database...")
    run_command(['colmap', 'database_creator', '--database_path', 'database.db'])

    # Step 2: Extract features from images with the user-defined max image size
    run_command([ 
        'colmap', 'feature_extractor',
        '--database_path', 'database.db',
        '--image_path', 'images',
        '--SiftExtraction.max_num_features', '32768',
        '--SiftExtraction.use_gpu', '1'
    ])
    
    # Step 3: Match features between images
    run_command([
        'colmap', 'exhaustive_matcher',
        '--database_path', 'database.db',
        '--SiftMatching.guided_matching', '1',
        '--SiftMatching.max_num_matches', '32768'
    ])
    
    # Step 4: Run the COLMAP mapper to create the sparse model
    run_command([
        'colmap', 'mapper',
        '--database_path', 'database.db',
        '--image_path', 'images',
        '--output_path', 'sparse',
        '--Mapper.num_threads', '16',
        '--Mapper.init_min_tri_angle', '4',
        '--Mapper.multiple_models', '0',
        '--Mapper.extract_colors', '0',
    ])
    #run_command(['colmap', 'bundle_adjuster', '--input_path', 'sparse/0/', '--output_path', 'sparse/0/'])
    # Step 5: Optionally convert the sparse model to a text format
    run_command([
        'colmap', 'model_converter',
        '--input_path', 'sparse/0/',
        '--output_path', 'sparse/0/',
        '--output_type', 'TXT'
    ])

    

def main():
    # Get user input for max image size, base path, and scene
    base_path = input("Enter base path to dataset (e.g., C:/Users/user/Documents/FSGS/dataset/...): ")
    scene = input("Enter the scene name (e.g., chair): ")
    
    # Call the function to create sparse model
    create_sparse_model(base_path, scene)

# Run the script
if __name__ == "__main__":
    main()
