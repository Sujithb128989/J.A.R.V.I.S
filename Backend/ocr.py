import difflib
import cv2
import easyocr
import numpy as np
import pyautogui as pg
from PIL import ImageGrab
from time import time as t

# Initialize EasyOCR reader globally for efficiency
reader = easyocr.Reader(['en'], gpu=True) # enabled after using cuda 

def calculate_center(bbox):
    """Calculate the center of a bounding box."""
    (top_left, top_right, bottom_right, bottom_left) = bbox
    center_x = (top_left[0] + bottom_right[0]) / 2
    center_y = (top_left[1] + bottom_right[1]) / 2
    return int(center_x), int(center_y)

def Ocr(st, double_click=False, **kwargs):
    """Perform OCR on the screen and click on the closest match."""
    try:
        # Take a screenshot
        screen = np.array(ImageGrab.grab())

        # Convert screenshot to grayscale for better OCR performance
        grayscale_screen = cv2.cvtColor(screen, cv2.COLOR_RGB2GRAY)

        # Perform OCR
        start_time = t()
        results = reader.readtext(grayscale_screen)
        print(f"Text recognition completed in {t() - start_time:.2f} seconds.")

        # Extract detected words
        detected_words = [res[1].lower() for res in results]

        # Find the closest match to the input string
        closest_match = difflib.get_close_matches(st.lower(), detected_words, n=1)
        if closest_match:
            print(f"Best match for '{st}' is '{closest_match[0]}'.")
            for res in results:
                if res[1].lower() == closest_match[0].lower():
                    bbox = res[0]
                    center_x, center_y = calculate_center(bbox)

                    # Perform click action
                    if double_click:
                        pg.click(x=center_x, y=center_y, clicks=2, interval=0.35)
                    else:
                        pg.click(x=center_x, y=center_y)

                    return f"Clicked on '{st}' successfully."
        else:
            return f"No button found named '{st}'."

    except Exception as e:
        return f"An error occurred: {e}"

