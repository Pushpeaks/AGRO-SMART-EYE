import os
import urllib.request
import zipfile
from PIL import Image
import numpy as np

DATASET_DIR = "dataset"
CLASSES = [
    "Apple___Apple_scab",
    "Apple___Black_rot",
    "Apple___Cedar_apple_rust",
    "Apple___healthy",
    "Potato___Early_blight",
    "Potato___Late_blight",
    "Potato___healthy",
    "Tomato___Bacterial_spot",
    "Tomato___Early_blight",
    "Tomato___Late_blight",
    "Tomato___Leaf_Mold",
    "Tomato___Septoria_leaf_spot",
    "Tomato___Spider_mites Two-spotted_spider_mite",
    "Tomato___Target_Spot",
    "Tomato___Tomato_Yellow_Leaf_Curl_Virus",
    "Tomato___Tomato_mosaic_virus",
    "Tomato___healthy"
]

def generate_dummy_dataset(base_dir, num_samples_per_class=20):
    """
    Generates a tiny dummy dataset to test the training pipeline instantly.
    In a real scenario, you should download the actual PlantVillage dataset.
    """
    print("Generating dummy dataset for immediate testing...")
    
    train_dir = os.path.join(base_dir, 'train')
    val_dir = os.path.join(base_dir, 'val')
    
    for split_dir in [train_dir, val_dir]:
        for class_name in CLASSES:
            class_path = os.path.join(split_dir, class_name)
            os.makedirs(class_path, exist_ok=True)
            
            # Generate dummy images
            samples = num_samples_per_class if split_dir == train_dir else num_samples_per_class // 5
            for i in range(samples):
                # Create a random RGB image (e.g. mostly green to simulate leaves)
                random_noise = np.random.randint(0, 100, (224, 224, 3), dtype=np.uint8)
                random_noise[:, :, 1] += 100 # Add more green
                
                img = Image.fromarray(random_noise)
                img.save(os.path.join(class_path, f"dummy_{i}.jpg"))
                
    print(f"Dummy dataset generated successfully at {base_dir}!")
    print("NOTE: For real results, please replace this with the actual PlantVillage dataset.")

def download_kaggle_dataset():
    """
    Instructions for downloading the real dataset.
    """
    print("="*50)
    print("To use the REAL PlantVillage dataset, run:")
    print("1. pip install kaggle")
    print("2. kaggle datasets download -d emmarex/plantdisease")
    print("3. Unzip the downloaded file into the 'dataset' folder.")
    print("="*50)

if __name__ == "__main__":
    if not os.path.exists(DATASET_DIR):
        os.makedirs(DATASET_DIR)
        generate_dummy_dataset(DATASET_DIR)
        download_kaggle_dataset()
    else:
        print("Dataset directory already exists.")
