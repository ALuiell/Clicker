import os
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

        x1, y1, x2, y2 = win32gui.GetWindowRect(window_handle)
        x1 += 30
        y1 += 150
        x2 -= 40
        y2 -= 400

        click_counter = 0

        while True:
            if not paused:

                screenshot = ImageGrab.grab(bbox=(x1, y1, x2, y2))
                image = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
                hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

                lower_pink = np.array([140, 50, 100])  # Расширенный диапазон для розового
                upper_pink = np.array([180, 255, 255]) # Верхняя граница HSV
                lower_gray = np.array([0, 0, 50])
                upper_gray = np.array([180, 50, 200])
                kernel = np.ones((3, 3), np.uint8)

                # Создание маски для розовых и серых цветов
                mask_pink = cv2.inRange(hsv, lower_pink, upper_pink)
                mask_gray = cv2.inRange(hsv, lower_gray, upper_gray)
                mask_gray = cv2.erode(mask_gray, kernel, iterations=1)
                mask_gray = cv2.dilate(mask_gray, kernel, iterations=1)
                blurred = cv2.GaussianBlur(mask_gray, (5, 5), 0)

                # Объединение масок
                mask = cv2.bitwise_or(mask_pink, blurred)

                # Находим контуры на объединенной маске
                contours_all, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

                for contour in contours_all:
                    area = cv2.contourArea(contour)
                    x, y, w, h = cv2.boundingRect(contour)
                    aspect_ratio = float(w) / h
                    if area > 10 and 0.75 < aspect_ratio < 1.2:
                        center_x = x + w // 2
                        center_y = y + h // 2
                        absolute_x = x1 + center_x
                        absolute_y = y1 + center_y
                        win32api.SetCursorPos((absolute_x, absolute_y))
                        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, absolute_x, absolute_y, 0, 0)
                        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, absolute_x, absolute_y, 0, 0)
                        delay = random.uniform(0.01, 0.05)
                        time.sleep(delay)
                        click_counter += 1
                        break

            if keyboard.is_pressed('q'):
                print(click_counter)
                click_counter = 0
                paused = not paused
                time.sleep(0.2)

    else:
        print(f"Окно '{window_title}' не найдено")

except ValueError:
    print("Telegram window found but not Blum, open Blum and try again.")
    input()
