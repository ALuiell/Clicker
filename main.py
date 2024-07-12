import logging
import random
import cv2
import keyboard
import numpy as np
from PIL import ImageGrab
import win32gui
import time
import win32api
import win32con

paused = False


class Clicker:
    def __init__(self):
        self.window_title = "TelegramDesktop"
        self.windows_handle = None
        self.coordinates = None

    @staticmethod
    def count_replay_game():
        while True:
            try:
                count = int(input("How many times do you want to play?: "))
                if 0 < count < 10000:
                    return count
            except ValueError:
                print("Invalid input. Please enter an integer.")

    def window_exists(self):
        return win32gui.FindWindow(None, self.window_title)

    def is_window_open(self):
        while True:
            window_handle = self.window_exists()
            if window_handle:
                print(f"window: {self.window_title} found")
                self.windows_handle = window_handle
                self.coordinates = win32gui.GetWindowRect(window_handle)
                x1, y1, x2, y2 = self.coordinates
                coords = (x1 + 20, y1 + 100, x2 - 20, y2 - 450)
                try:
                    screenshot = ImageGrab.grab(bbox=coords)
                    print("Blum found")
                    return True  # Окно найдено и активно
                except ValueError:
                    print("Blum window is not active. Make sure the correct Blum window is active.")
                    time.sleep(1)  # Ждем 1 секунду перед следующей попыткой
            else:
                print(f"Окно '{self.window_title}' не найдено")
                time.sleep(1)  # Ждем 1 секунду перед следующей попыткой

    def replay_game(self, count):
        print("Start Found Play Button")
        count_replay = count
        x1, y1, x2, y2 = self.coordinates
        coords = (x1 + 20, y1 + 500, x2 - 20, y2 - 75)

        while True:

            screenshot = ImageGrab.grab(bbox=coords)
            hsv = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2HSV)

            lower_white = np.array([0, 0, 230])
            upper_white = np.array([180, 20, 255])

            mask_white = cv2.inRange(hsv, lower_white, upper_white)
            contours_white, _ = cv2.findContours(mask_white, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            for contour in contours_white:
                area = cv2.contourArea(contour)
                x, y, w, h = cv2.boundingRect(contour)
                if area > 15000:
                    center_x = x + w // 2
                    center_y = y + h // 2
                    absolute_x = coords[0] + center_x
                    absolute_y = coords[1] + center_y
                    cv2.rectangle(hsv, (x, y), (x + w, y + h), (0, 255, 0), 2)
                    cv2.imshow("Screenshot", hsv)
                    cv2.waitKey(0)
                    win32api.SetCursorPos((absolute_x, absolute_y))
                    # win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, absolute_x, absolute_y, 0, 0)
                    # win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, absolute_x, absolute_y, 0, 0)
                    break
                else:
                    print("Button Play not found")

    # def find_objects_and_click(self, count):
    #     print("Start Game")
    #     global paused
    #     x1, y1, x2, y2 = self.coordinates
    #     x1 += 20
    #     y1 += 150
    #     x2 -= 20
    #     y2 -= 400
    #     #
    #     # start_time = time.time()
    #     #
    #     # while time.time() - start_time < 30:
    #     while True:
    #         if not paused:
    #             screenshot = ImageGrab.grab(bbox=(x1, y1, x2, y2))
    #             image = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
    #             hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    #
    #             lower_green = np.array([30, 120, 100])
    #             upper_green = np.array([65, 255, 255])
    #             mask_green = cv2.inRange(hsv, lower_green, upper_green)
    #             contours_green, _ = cv2.findContours(mask_green, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    #
    #             for contour in contours_green:
    #                 area = cv2.contourArea(contour)
    #                 x, y, w, h = cv2.boundingRect(contour)
    #                 aspect_ratio = float(w) / h
    #                 if area > 10 and 0.8 < aspect_ratio < 1.2:
    #                     center_x = x + w // 2
    #                     center_y = y + h // 2
    #                     absolute_x = x1 + center_x + random.randint(-3, 3)
    #                     absolute_y = y1 + center_y + random.randint(-3, 3)
    #                     win32api.SetCursorPos((absolute_x, absolute_y))
    #                     win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, absolute_x, absolute_y, 0, 0)
    #                     win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, absolute_x, absolute_y, 0, 0)
    #                     delay = random.uniform(0.04, 0.1)
    #                     time.sleep(delay)
    #                     break

    def find_objects_and_click(self, count):
        print("Start Game")
        global paused
        x1, y1, x2, y2 = self.coordinates
        x1 += 20
        y1 += 150
        x2 -= 20
        y2 -= 400

        start_time = None
        time_limit = 30

        while True and (start_time is None or time.time() - start_time <= time_limit):  # Условие цикла
            if not paused:
                screenshot = ImageGrab.grab(bbox=(x1, y1, x2, y2))
                image = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
                hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

                lower_green = np.array([30, 120, 100])
                upper_green = np.array([65, 255, 255])
                mask_green = cv2.inRange(hsv, lower_green, upper_green)
                contours_green, _ = cv2.findContours(mask_green, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

                for contour in contours_green:
                    area = cv2.contourArea(contour)
                    x, y, w, h = cv2.boundingRect(contour)
                    aspect_ratio = float(w) / h
                    if area > 10 and 0.8 < aspect_ratio < 1.2:
                        if start_time is None:
                            start_time = time.time()  # Устанавливаем start_time при первом клике

                        center_x = x + w // 2
                        center_y = y + h // 2
                        absolute_x = x1 + center_x + random.randint(-3, 3)
                        absolute_y = y1 + center_y + random.randint(-3, 3)
                        win32api.SetCursorPos((absolute_x, absolute_y))
                        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, absolute_x, absolute_y, 0, 0)
                        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, absolute_x, absolute_y, 0, 0)
                        delay = random.uniform(0.04, 0.1)
                        time.sleep(delay)
                        break

            if keyboard.is_pressed('w'):
                paused = not paused
                time.sleep(0.2)

                if paused:
                    print("Clicker paused")
                else:
                    print("Clicker resumed")

        # self.replay_game(count)


clicker = Clicker()


def game():
    while True:
        if clicker.is_window_open():
            count = clicker.count_replay_game()
            # clicker.find_objects_and_click(count)
            clicker.replay_game(count)


if __name__ == '__main__':
    game()
