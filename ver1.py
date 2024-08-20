import random

import cv2
import keyboard
import numpy as np
from PIL import ImageGrab
import win32gui
import time
import win32api
import win32con

try:
    def window_exists(window_title):
        return win32gui.FindWindow(None, window_title)


    window_title = "TelegramDesktop"  # Замени на реальное название окна игры
    window_handle = window_exists(window_title)

    if window_exists(window_title):
        print(f"window: {window_title} found")
        print("press 'q' to pause")

        paused = False

        while True:
            if not paused:
                x1, y1, x2, y2 = win32gui.GetWindowRect(window_handle)

                x1 += 20
                y1 += 250
                x2 -= 20
                y2 -= 250

                screenshot = ImageGrab.grab(bbox=(x1, y1, x2, y2))
                image = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
                hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

                lower_green = np.array([30, 120, 100])
                upper_green = np.array([65, 255, 255])
                mask_green = cv2.inRange(hsv, lower_green, upper_green)
                kernel = np.ones((3, 3), np.uint8)
                mask_green = cv2.erode(mask_green, kernel, iterations=1)
                mask_green = cv2.dilate(mask_green, kernel, iterations=1)
                contours_green, _ = cv2.findContours(mask_green, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

                for contour in contours_green:
                    area = cv2.contourArea(contour)
                    x, y, w, h = cv2.boundingRect(contour)
                    aspect_ratio = float(w) / h
                    if area > 10 and 0.8 < aspect_ratio < 1.2:
                        t_start_c = time.perf_counter()
                        center_x = x + w // 2
                        center_y = y + h // 2
                        absolute_x = x1 + center_x + random.randint(-3, 3)
                        absolute_y = y1 + center_y + random.randint(-3, 3)
                        win32api.SetCursorPos((absolute_x, absolute_y))
                        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, absolute_x, absolute_y, 0, 0)
                        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, absolute_x, absolute_y, 0, 0)
                        delay = random.uniform(0.01, 0.07)
                        time.sleep(delay)
                        break

            if keyboard.is_pressed('q'):
                paused = not paused
                time.sleep(0.2)

    else:
        print(f"Окно '{window_title}' не найдено")

except ValueError:
    print("Telegram window found but not Blum, open Blum and try again.")
    input()

