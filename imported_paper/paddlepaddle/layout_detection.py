"""
Layout Detection Script for PaddleOCR

IMPORTANT: This script requires Python 3.11 (PaddlePaddle doesn't support Python 3.14 yet).
Run with: py -3.11 layout_detection.py <image_path>
"""

from paddleocr import LayoutDetection
import cv2
import numpy as np
import argparse

# Configuration options to try:
# 1. Increase img_size for better detection of smaller regions
#    Default is usually 800, try: 1280, 1536, 1920, or 2560
# 2. Adjust layout_threshold (lower = more detections)
#    Default is usually 0.5, try: 0.3, 0.4 for more sensitive detection
# 3. Note: PP-DocLayout-L is trained on document layouts, not game interfaces
#    Your slot machine image may need different preprocessing

# Initialize model
# Note: img_size parameter is not supported for PP-DocLayout-L model
# The model will automatically handle image sizing
model = LayoutDetection(model_name="PP-DocLayout-L")

# Optional: Preprocess image to improve detection
def preprocess_image(image_path, max_size=1920, enhance_contrast=True):
    """
    Preprocess image before layout detection.
    
    Args:
        image_path: Path to input image
        max_size: Maximum dimension (width or height) to resize to
        enhance_contrast: Whether to enhance image contrast
    """
    img = cv2.imread(image_path)
    if img is None:
        raise ValueError(f"Could not read image: {image_path}")
    
    h, w = img.shape[:2]
    original_size = (w, h)
    
    # Resize if image is too large (helps with memory and detection)
    if max_size and max(h, w) > max_size:
        scale = max_size / max(h, w)
        new_w, new_h = int(w * scale), int(h * scale)
        img = cv2.resize(img, (new_w, new_h), interpolation=cv2.INTER_LINEAR)
        print(f"Resized image from {original_size} to ({new_w}, {new_h})")
    
    # Optional: Enhance contrast (may help with detection)
    if enhance_contrast:
        img = cv2.convertScaleAbs(img, alpha=1.2, beta=10)
        print("Applied contrast enhancement")
    
    return img

# Parse command-line arguments
parser = argparse.ArgumentParser(description='Layout Detection Script for PaddleOCR')
parser.add_argument('image_path', help='Path to the input image file')
args = parser.parse_args()

# Method 1: Direct file path (simplest)
# output = model.predict(args.image_path, batch_size=1)

# Method 2: Preprocess first (recommended for large or low-contrast images)
image = preprocess_image(args.image_path, max_size=1920, enhance_contrast=True)
output = model.predict(image, batch_size=1)

# Process results
def get_box_coords(box):
    if 'bbox' in box:
        return box['bbox']
    if 'coordinate' in box:
        return box['coordinate']
    return None

def is_inside(inner, outer):
    # inner, outer are [x1, y1, x2, y2]
    ix1, iy1, ix2, iy2 = inner
    ox1, oy1, ox2, oy2 = outer
    return ix1 >= ox1 and iy1 >= oy1 and ix2 <= ox2 and iy2 <= oy2

def filter_nested_boxes(boxes):
    if not boxes: return []
    to_remove = set()
    for i in range(len(boxes)):
        for j in range(len(boxes)):
            if i == j: continue
            box_i = boxes[i]
            box_j = boxes[j]
            coords_i = get_box_coords(box_i)
            coords_j = get_box_coords(box_j)
            
            if not coords_i or not coords_j: continue
            
            # Check labels - strictly image inside image.
            # Labels might be 'figure', 'image', etc. Depending on model.
            # Assuming 'image' based on user description.
            label_i = str(box_i.get('label', '')).lower()
            label_j = str(box_j.get('label', '')).lower()
            
            # Adjust these terms if needed based on model output classes
            target_labels = ['image', 'figure', 'picture']
            is_image_i = any(t in label_i for t in target_labels)
            is_image_j = any(t in label_j for t in target_labels)
            
            if is_image_i and is_image_j:
                if is_inside(coords_i, coords_j):
                    # i is inside j. Remove i.
                    to_remove.add(i)
    
    return [b for k, b in enumerate(boxes) if k not in to_remove]

for res in output:
    # Filter nested images before processing
    if 'res' in res and 'boxes' in res['res']:
        res['res']['boxes'] = filter_nested_boxes(res['res']['boxes'])
    elif 'boxes' in res:
        res['boxes'] = filter_nested_boxes(res['boxes'])

    res.print()
    res.save_to_img(save_path="./output/")
    res.save_to_json(save_path="./output/res.json")
    
    # Print detection statistics
    # Access boxes from the result structure (res is a dict-like object)
    if 'res' in res and 'boxes' in res['res']:
        boxes = res['res']['boxes']
        print(f"\nDetected {len(boxes)} layout regions")
        # Print detected labels
        labels = [box['label'] for box in boxes]
        label_counts = {}
        for label in labels:
            label_counts[label] = label_counts.get(label, 0) + 1
        print(f"Label distribution: {label_counts}")
    elif 'boxes' in res:
        boxes = res['boxes']
        print(f"\nDetected {len(boxes)} layout regions")
        labels = [box['label'] for box in boxes]
        label_counts = {}
        for label in labels:
            label_counts[label] = label_counts.get(label, 0) + 1
        print(f"Label distribution: {label_counts}")

