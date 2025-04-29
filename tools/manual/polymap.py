import shutil
from pathlib import Path
import enlighten
import pycolmap

def incremental_mapping_with_pbar(database_path, image_path, sfm_path):
    num_images = pycolmap.Database(database_path).num_images
    with enlighten.Manager() as manager:
        with manager.counter(total=num_images, desc="Images registered:") as pbar:
            pbar.update(0, force=True)
            reconstructions = pycolmap.incremental_mapping(
                database_path,
                image_path,
                sfm_path,
                initial_image_pair_callback=lambda: pbar.update(2),
                next_image_callback=lambda: pbar.update(1),
            )
    return reconstructions

def run():
    # Ask the user for the output path
    output_path_input = input("Enter the output path (e.g., 'example/'): ")
    output_path = Path(output_path_input).resolve()

    # Create necessary directories
    if not output_path.exists():
        output_path.mkdir(parents=True, exist_ok=True)

    # Ask for the image folder path
    image_path_input = input(f"Enter the path to the images folder within {output_path_input} (e.g., 'images/'): ")
    image_path = output_path / image_path_input

    # Check if the image folder exists
    if not image_path.exists():
        exit(f"The folder {image_path} does not exist. Please provide a valid folder path.")

    # Define the database and SfM paths
    database_path = output_path / "database.db"
    sfm_path = output_path / "sparse/0/"

    # Create the entire SfM output directory structure if it doesn't exist
    if sfm_path.exists():
        shutil.rmtree(sfm_path)  # Remove it if it already exists
    sfm_path.mkdir(parents=True, exist_ok=True)  # Create the directory and any missing parent directories

    # Ensure random seed is set for consistency
    pycolmap.set_random_seed(0)

    # Feature extraction and exhaustive matching with GPU acceleration
    sift_options = pycolmap.SiftExtractionOptions()
    sift_options.num_threads = 4  # Adjust as needed

    # Perform feature extraction using GPU
    #pycolmap.extract_features(database_path,image_path,sift_options=sift_options,device='cpu'  # Use 'cuda' for GPU acceleration)


    #pycolmap.match_exhaustive(database_path,  device='cpu'  # or 'cpu')

    mvs_path = output_path / "dense"
    # Create the entire SfM output directory structure if it doesn't exist
    if mvs_path.exists():
        shutil.rmtree(mvs_path)  # Remove it if it already exists
    mvs_path.mkdir(parents=True, exist_ok=True)  # Create the directory and any missing parent directories
    # Run incremental SfM
    reconstructions = incremental_mapping_with_pbar(database_path, image_path, sfm_path)
    reconstructions[0].write(sfm_path)
    print("Incremental SfM completed. Reconstructed scenes saved to:", sfm_path)
    # dense reconstruction
    #pycolmap.undistort_images(mvs_path, sfm_path, image_path)
    #pycolmap.patch_match_stereo(mvs_path)  # requires compilation with CUDA
    #pycolmap.stereo_fusion(mvs_path / "fused.ply", mvs_path)
if __name__ == "__main__":
    run()
