import cv2
import pytesseract
import OCR_path

pytesseract.pytesseract.tesseract_cmd = OCR_path.ocr_path


def image_to_text(image_np):
    end = False
    while not end:
        try:
            gray = cv2.cvtColor(image_np, cv2.COLOR_BGR2GRAY)
            thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
            text = pytesseract.image_to_string(thresh, config='--psm 6 -c tessedit_char_whitelist=0123456789')

            if len(text) != 0:
                end = not end
                return text

        except pytesseract.TesseractError as e:
            print(f"Error during OCR: {e}")
            return []
