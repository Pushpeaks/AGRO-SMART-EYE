import os
import shutil
import random

# Use a max number of images per class to keep training fast but effective
MAX_PER_CLASS = 150
TRAIN_RATIO = 0.8

SOURCE_DIR = "temp_dataset/raw/color"
TARGET_DIR = "dataset"

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

def main():
    print("Processing real PlantVillage dataset...")
    
    # Clean up existing dummy dataset
    if os.path.exists(TARGET_DIR):
        shutil.rmtree(TARGET_DIR)
        
    os.makedirs(os.path.join(TARGET_DIR, 'train'), exist_ok=True)
    os.makedirs(os.path.join(TARGET_DIR, 'val'), exist_ok=True)
    
    if not os.path.exists(SOURCE_DIR):
        print(f"Source directory {SOURCE_DIR} not found. Ensure git clone completed.")
        return

    for class_name in CLASSES:
        src_class_path = os.path.join(SOURCE_DIR, class_name)
        if not os.path.exists(src_class_path):
            print(f"Warning: Class {class_name} not found in downloaded dataset.")
            continue
            
        images = [f for f in os.listdir(src_class_path) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
        random.shuffle(images)
        
        # Limit the number of images
        images = images[:MAX_PER_CLASS]
        
        num_train = int(len(images) * TRAIN_RATIO)
        train_images = images[:num_train]
        val_images = images[num_train:]
        
        # Create target directories
        train_class_path = os.path.join(TARGET_DIR, 'train', class_name)
        val_class_path = os.path.join(TARGET_DIR, 'val', class_name)
        
        os.makedirs(train_class_path, exist_ok=True)
        os.makedirs(val_class_path, exist_ok=True)
        
        # Copy files
        for img in train_images:
            shutil.copy2(os.path.join(src_class_path, img), os.path.join(train_class_path, img))
            
        for img in val_images:
            shutil.copy2(os.path.join(src_class_path, img), os.path.join(val_class_path, img))
            
        print(f"Processed {class_name}: {len(train_images)} train, {len(val_images)} val.")

    print("\nDataset successfully processed! You can now run train.py.")

if __name__ == "__main__":
    main()
