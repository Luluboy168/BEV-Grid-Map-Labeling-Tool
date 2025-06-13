import os
import torch
import cv2
import numpy as np
from tqdm import tqdm
from transformers import Mask2FormerImageProcessor, Mask2FormerForUniversalSegmentation

import warnings
warnings.filterwarnings("ignore", r"`label_ids_to_fuse` unset. No instance will be fused.", category=UserWarning, module="transformers")


# Config
IMAGE_FOLDER = "images"
OUTPUT_FOLDER = "panoptic"
MODEL_ID = "facebook/mask2former-swin-large-coco-panoptic"
# MODEL_ID = "facebook/mask2former-swin-large-cityscapes-panoptic"
CATEGORY_IDS = [2, 5, 7]  # car, bus, truck for coco
# CATEGORY_IDS = [13, 14, 15]  # car, bus, truck for cityscape

# Prepare output directory
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# Load model and processor
device = "cuda" if torch.cuda.is_available() else "cpu"
processor = Mask2FormerImageProcessor.from_pretrained(MODEL_ID)
model = Mask2FormerForUniversalSegmentation.from_pretrained(MODEL_ID).to(device).eval()

# Collect image files
image_files = [f for f in os.listdir(IMAGE_FOLDER)
               if f.lower().endswith(('.jpg', '.jpeg', '.png'))]

print(f"🔍 Found {len(image_files)} images...")

# Process each image
for filename in tqdm(image_files, desc="Processing"):
    image_path = os.path.join(IMAGE_FOLDER, filename)
    image_bgr = cv2.imread(image_path)
    if image_bgr is None:
        print(f"Skipping unreadable file: {filename}")
        continue

    image_rgb = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)
    h, w = image_rgb.shape[:2]

    # Preprocess input
    inputs = processor(images=image_rgb, return_tensors="pt").to(device)

    # Run inference
    with torch.no_grad():
        outputs = model(**inputs)

    # Post-process segmentation
    processed = processor.post_process_panoptic_segmentation(outputs, target_sizes=[(h, w)], label_ids_to_fuse=[])[0]
    panoptic_seg = processed["segmentation"].cpu().numpy()
    segments_info = processed["segments_info"]

    # Create a merged binary mask for car and truck
    combined_mask = np.zeros((h, w), dtype=np.uint8)
    for seg in segments_info:
        if seg["label_id"] in CATEGORY_IDS:
            combined_mask[panoptic_seg == seg["id"]] = 255

    # Save mask
    output_path = os.path.join(OUTPUT_FOLDER, os.path.splitext(filename)[0] + ".png")
    cv2.imwrite(output_path, combined_mask)

print(f"Done. Combined car+truck masks saved to '{OUTPUT_FOLDER}'")
