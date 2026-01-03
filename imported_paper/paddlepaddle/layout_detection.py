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
for res in output:
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

