import cv2
import numpy as np
import pytesseract
import OCR_path

pytesseract.pytesseract.tesseract_cmd = OCR_path.ocr_path


def image_to_text(image_np):
    end = False
    while not end:
        try:
            gray = cv2.bitwise_not(image_np)  # Invert colors
            gray = cv2.cvtColor(gray, cv2.COLOR_BGR2GRAY)  # Convert to grayscale

            # Apply Gaussian blur to reduce noise (optional)
            gray = cv2.GaussianBlur(gray, (3, 3), 0)

            # Thresholding
            thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]

            # Apply dilation to improve character separation (optional)
            kernel = np.ones((2, 2), np.uint8)
            thresh = cv2.dilate(thresh, kernel, iterations=1)

            # OCR with configuration
            text = pytesseract.image_to_string(thresh, config='--psm 6 -c tessedit_char_whitelist=0123456789')

            if len(text) != 0:
                end = not end
                return text

        except pytesseract.TesseractError as e:
            print(f"Error during OCR: {e}")
            return []
