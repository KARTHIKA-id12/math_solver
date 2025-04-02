import os
import sys
import cv2
import numpy as np
from PIL import Image
import pytesseract
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def check_tesseract():
    """Check if Tesseract OCR is installed and available"""
    try:
        import pytesseract
        pytesseract.get_tesseract_version()
        return True, pytesseract
    except Exception:
        return False, None

def extract_text_from_image(image_path):
    # First check if Tesseract is available
    tesseract_available, pytesseract = check_tesseract()
    
    if not tesseract_available:
        installation_guide = """
Tesseract OCR is not installed or not found in your PATH. Please install it:

For Windows:
1. Download installer from: https://github.com/UB-Mannheim/tesseract/wiki
2. Install and add to PATH
3. Restart your application

For macOS:
1. Install using Homebrew: brew install tesseract

For Linux:
1. sudo apt install tesseract-ocr
2. sudo apt install libtesseract-dev

After installation, make sure to install the Python wrapper:
pip install pytesseract
"""
        return f"Error: {installation_guide}"
        
    try:
        # Read image
        if not os.path.exists(image_path):
            return "Error: Image file not found"
            
        img = cv2.imread(image_path)
        if img is None:
            return "Error: Could not read image. File may be corrupted."
        
        # Convert to grayscale
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Enhance image for math equation recognition
        # Apply multiple preprocessing techniques to improve OCR accuracy
        
        # Method 1: Basic thresholding
        _, thresh1 = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
        
        # Method 2: Adaptive thresholding
        thresh2 = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                      cv2.THRESH_BINARY, 11, 2)
        
        # Method 3: Denoising
        denoised = cv2.fastNlMeansDenoising(gray, None, 10, 7, 21)
        _, thresh3 = cv2.threshold(denoised, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
        
        # Try multiple preprocessing methods and combine results
        results = []
        
        # Configure different OCR options for math
        configs = [
            r'--oem 3 --psm 6',  # Default
            r'--oem 3 --psm 6 -l eng',  # English only
            r'--oem 1 --psm 6',  # Legacy engine
            r'--oem 3 --psm 4'   # Single column of text
        ]
        
        # Try all combinations of preprocessed images and configs
        for img_processed, img_name in [(thresh1, "thresh"), (thresh2, "adaptive"), 
                                       (thresh3, "denoised"), (gray, "gray")]:
            for config in configs:
                try:
                    text = pytesseract.image_to_string(img_processed, config=config)
                    text = text.strip()
                    if text and len(text) > 5:  # Only keep meaningful results
                        results.append(text)
                except Exception:
                    continue
        
        # Choose the best result (longest text as a simple heuristic)
        if results:
            results.sort(key=len, reverse=True)
            return results[0]
        else:
            return "Error: Could not extract text from image. Try typing the math problem manually."
            
    except Exception as e:
        return f"Error processing image: {str(e)}"