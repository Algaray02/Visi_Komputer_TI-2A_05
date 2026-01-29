import os
import shutil
import sys

try:
    import sam2
    sam2_path = os.path.dirname(sam2.__file__)
    config_src = os.path.join(sam2_path, "configs", "sam2.1_hiera_l.yaml")
    config_dst = "sam2.1_hiera_l.yaml"
    
    if os.path.exists(config_src):
        shutil.copy(config_src, config_dst)
        print(f"✓ Config file copied: {config_dst}")
    else:
        print(f"✗ Config file not found at: {config_src}")
        print("\nTry running: pip install -e git+https://github.com/facebookresearch/segment-anything-2.git#egg=sam2")
except Exception as e:
    print(f"Error: {e}")
