import os
import shutil
from pathlib import Path
from collections import defaultdict
import yaml
import re

# Define paths
roboflow_dir = Path("datasets/roboflow")
output_dir = Path("datasets/detect-helmet")
output_images = output_dir / "images"
output_labels = output_dir / "labels"

# Create output directory structure
for split in ['train', 'val', 'test']:
    (output_images / split).mkdir(parents=True, exist_ok=True)
    (output_labels / split).mkdir(parents=True, exist_ok=True)

print("="*70)
print("📁 MERGE DATASET DENGAN CLASS HARMONISASI")
print("="*70)
print(f"\nTarget class (3 class):")
print(f"  0 = With Helmet")
print(f"  1 = No Helmet")
print(f"  2 = Motorcycle")

# Define class mapping dari setiap dataset
CLASS_MAPPINGS = {
    'helmet1': {0: 0, 1: 1},  # With Helmet -> 0, Without Helmet -> 1
    'helmet2': {0: 0, 1: 1, 2: -1},  # licence -> skip (-1)
    'helmet3': {0: 0},  # helmet -> With Helmet (0)
    'helmet4': {0: 0, 1: 1},  # With Helmet -> 0, Without Helmet -> 1
    'helmet5': {0: 0, 1: 1},  # helmet -> 0, without-helmet -> 1
    'helmet6': {0: 0, 1: 1},  # helmet -> 0, no-helmet -> 1
    'helmet7': {0: 0, 1: 2},  # Helm -> With Helmet (0), Motor -> Motorcycle (2)
    'motor1': {0: 2},  # motorcycle -> 2
    'motor2': {0: 2},  # motor -> 2
    'motor3': {0: 2},  # Motor -> 2
    'motor4': {0: 2},  # Motor -> 2
    'motor5': {0: 2},  # motor-7ASr -> 2
    'motor6': {0: 2},  # motors -> 2
    'motor7': {0: 1, 1: 2},  # '0' -> No Helmet (1), '1' -> Motorcycle (2)
}

file_counter = defaultdict(int)
skipped_counter = defaultdict(int)

# Process each dataset folder
dataset_folders = sorted([d for d in roboflow_dir.iterdir() if d.is_dir()])

print(f"\n🔄 Memproses {len(dataset_folders)} dataset folder...")

for dataset_path in dataset_folders:
    dataset_name = dataset_path.name
    class_mapping = CLASS_MAPPINGS.get(dataset_name, {})
    
    print(f"\n  📦 {dataset_name}")
    print(f"     Class mapping: {class_mapping}")
    
    # Process each split (train, val, test)
    for split in ['train', 'valid', 'test']:
        split_dir = dataset_path / split
        if not split_dir.exists():
            continue
            
        # Map 'valid' to 'val' in output
        output_split = 'val' if split == 'valid' else split
        
        # Process images and labels
        images_src = split_dir / "images"
        labels_src = split_dir / "labels"
        
        if images_src.exists() and labels_src.exists():
            # Get all image files
            img_files = list(images_src.iterdir())
            
            for img_file in img_files:
                if not img_file.is_file():
                    continue
                
                # Find corresponding label file
                img_stem = img_file.stem
                label_file = None
                for lbl in labels_src.iterdir():
                    if lbl.stem == img_stem:
                        label_file = lbl
                        break
                
                if label_file is None:
                    continue
                
                # Read label file and convert class IDs
                try:
                    with open(label_file, 'r') as f:
                        lines = f.readlines()
                    
                    converted_lines = []
                    skip_image = False
                    
                    for line in lines:
                        parts = line.strip().split()
                        if len(parts) < 5:  # class_id + bbox
                            continue
                        
                        old_class_id = int(parts[0])
                        new_class_id = class_mapping.get(old_class_id, -1)
                        
                        # Skip if class should be excluded (-1)
                        if new_class_id == -1:
                            skipped_counter[f'{dataset_name}_{output_split}'] += 1
                            skip_image = True
                            break
                        
                        # Replace class ID with new one
                        new_line = f"{new_class_id} " + " ".join(parts[1:]) + "\n"
                        converted_lines.append(new_line)
                    
                    if skip_image:
                        continue
                    
                    # Copy image with new name
                    new_img_name = f"{dataset_name}_{img_file.name}"
                    dest_img = output_images / output_split / new_img_name
                    shutil.copy2(img_file, dest_img)
                    file_counter[f'{output_split}_img'] += 1
                    
                    # Write converted label file
                    new_label_name = f"{dataset_name}_{label_file.name}"
                    dest_label = output_labels / output_split / new_label_name
                    with open(dest_label, 'w') as f:
                        f.writelines(converted_lines)
                    file_counter[f'{output_split}_label'] += 1
                    
                except Exception as e:
                    print(f"     ⚠️  Error processing {img_file.name}: {e}")
                    continue

print("\n" + "="*70)
print("📊 STATISTIK MERGE:")
print("="*70)
print("\nFile yang diproses:")
for key, count in sorted(file_counter.items()):
    print(f"  {key}: {count}")

if skipped_counter:
    print("\nFile yang di-skip (karena class di-exclude):")
    for key, count in sorted(skipped_counter.items()):
        print(f"  {key}: {count}")

# Create unified data.yaml
data_yaml_content = {
    'path': str(output_dir.resolve()),
    'train': 'images/train',
    'val': 'images/val',
    'test': 'images/test',
    'nc': 3,
    'names': ['with_helmet', 'no_helmet', 'motorcycle']
}

data_yaml_path = output_dir / "data.yaml"
with open(data_yaml_path, 'w') as f:
    yaml.dump(data_yaml_content, f, default_flow_style=False, sort_keys=False)

print(f"\n📄 File data.yaml dibuat di: {data_yaml_path}")

print("\n" + "="*70)
print("✅ MERGE SELESAI!")
print("="*70)
print(f"\n📁 Hasil merge tersimpan di: {output_dir}")
print(f"   ├── images/")
print(f"   │   ├── train/")
print(f"   │   ├── val/")
print(f"   │   └── test/")
print(f"   └── labels/")
print(f"       ├── train/")
print(f"       ├── val/")
print(f"       └── test/")
print(f"\n📌 Class Mapping Hasil Akhir:")
print(f"   0 = with_helmet")
print(f"   1 = no_helmet")
print(f"   2 = motorcycle")
print("="*70)
