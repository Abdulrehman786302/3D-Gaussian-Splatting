import os
from PIL import Image

def resize_images(input_folder, scale_factor):
    # Create a new folder name based on scale factor
    output_folder = f"{input_folder}_{scale_factor}"
    
    # Ensure the output folder does not exist yet
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    # List all files in the input folder
    for filename in os.listdir(input_folder):
        filepath = os.path.join(input_folder, filename)
        
        # Check if the file is an image (based on extension)
        if filename.lower().endswith(('.jpg', '.jpeg', '.png')):
            try:
                # Open the image
                with Image.open(filepath) as img:
                    # Get original dimensions
                    width, height = img.size
                    
                    # Calculate new dimensions based on scale factor
                    new_width = int(width // scale_factor)
                    new_height = int(height // scale_factor)
                    
                    # Resize the image using LANCZOS filter for better quality
                    resized_img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                    
                    # Save the resized image to the new folder
                    output_path = os.path.join(output_folder, filename)
                    resized_img.save(output_path)
                    print(f"Resized and saved: {output_path}")
            except Exception as e:
                print(f"Could not process image {filename}: {e}")

def main():
    # Ask the user for the input folder path and scale factor
    input_folder = input("Enter the path to the input folder containing images: ")
    scale_factor = int(input("Enter the integer scale factor for resizing: "))

    # Validate if the input folder exists
    if not os.path.isdir(input_folder):
        print(f"The folder {input_folder} does not exist. Please check the path.")
        return

    # Call the resize function
    resize_images(input_folder, scale_factor)

if __name__ == "__main__":
    main()
