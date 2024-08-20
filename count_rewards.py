import cv2
import pytesseract
import OCR_path

pytesseract.pytesseract.tesseract_cmd = OCR_path.ocr_path


def image_to_text(image_np):

    gray = cv2.bitwise_not(image_np)
    gray = cv2.cvtColor(gray, cv2.COLOR_BGR2GRAY)
    gray = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
    text = pytesseract.image_to_string(gray)

    return text
