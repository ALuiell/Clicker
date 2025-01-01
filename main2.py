import random
import cv2
import keyboard
import numpy as np
from PIL import ImageGrab
import win32gui
import time
import win32api
import win32con
import logging

paused = True
total_points = 0
logging.basicConfig(filename='clicker_log.txt', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
safe = True

class Clicker:
    def __init__(self):
        self.window_title = "TelegramDesktop"
        self.windows_handle = None
        self.coordinates = None

    @staticmethod
    def count_replay_game():
        print("Enter the number of tickets (games) to play automatically after the first manual run.")
        print("Example: If you have 5 tickets, enter 4 and start the first game manually. ")
        while True:
            try:
                count = int(input("How many times do you want to play?: "))
                if 0 < count < 10000:
                    return count
            except ValueError:
                print("Invalid input. Please enter an integer.")

    def window_exists(self):
        return win32gui.FindWindow(None, self.window_title)

    def get_coords(self):
        self.coordinates = win32gui.GetWindowRect(self.windows_handle)
        return self.coordinates

    def is_window_open(self):
        while True:
            window_handle = self.window_exists()
            if window_handle:
                print(f"window: {self.window_title} found")
                self.windows_handle = window_handle
                x1, y1, x2, y2 = self.get_coords()
                coords = (x1 + 20, y1 + 100, x2 - 20, y2 - 450)
                try:
                    # blum window check
                    screenshot = ImageGrab.grab(bbox=coords)
                    print("Blum found")
                    return True
                except ValueError:
                    print("Blum window is not active. Make sure the correct Blum window is active.")
                    time.sleep(1)
            else:
                print(f"Window'{self.window_title}' Found")
                time.sleep(1)

    def replay_game(self):
        print("Try to start new game")
        time.sleep(5)
        x1, y1, x2, y2 = self.get_coords()
        coords = (x1 + 20, y1 + 530, x2 - 30, y2 - 75)

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
                    win32api.SetCursorPos((absolute_x, absolute_y))
                    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, absolute_x, absolute_y, 0, 0)
                    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, absolute_x, absolute_y, 0, 0)
                    return

                else:
                    time.sleep(2)
                    print("Trying to find Button PLAY ")

    def flexible_hsv_filter(self, image):
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        lower_hsv_bound = (175, 200, 50)
        upper_hsv_bound = (180, 255, 180)
        mask = cv2.inRange(hsv, lower_hsv_bound, upper_hsv_bound)
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        return contours

    def flexible_red_filter(self, image):
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

        # Define red color ranges in HSV
        red_lower1 = (0, 120, 70)
        red_upper1 = (10, 255, 255)
        red_lower2 = (170, 120, 70)
        red_upper2 = (180, 255, 255)

        # Create masks for the red ranges
        red_mask1 = cv2.inRange(hsv, red_lower1, red_upper1)
        red_mask2 = cv2.inRange(hsv, red_lower2, red_upper2)
        red_mask = cv2.bitwise_or(red_mask1, red_mask2)

        # Find contours from the red mask
        contours, _ = cv2.findContours(red_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        red_objects = []

        # Loop through contours to detect valid red objects
        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            roi = red_mask[y:y + h, x:x + w]
            red_pixels = cv2.countNonZero(roi)
            total_pixels = w * h

            # Criteria for valid red objects
            if total_pixels > 150 and red_pixels / total_pixels > 0.6 and 0.7 <= w / h <= 1.3:
                red_objects.append((x, y, w, h))

        return red_objects


    def refined_merge_close_contours(self, image, contours, merge_distance=10, min_area=50):
        merged_boxes = []
        for contour in contours:
            # Проверка на пустой контур и на формат данных
            if contour is None or len(contour) < 3 or not isinstance(contour, np.ndarray):
                continue

            try:
                x, y, w, h = cv2.boundingRect(contour)
            except cv2.error as e:
                logging.warning(f"Skipping invalid contour: {e}")
                continue
            box = [x, y, x + w, y + h]
            area = w * h
            if area < min_area:
                continue
            merged = False
            for i, existing_box in enumerate(merged_boxes):
                if (
                        abs(box[0] - existing_box[2]) <= merge_distance or
                        abs(box[2] - existing_box[0]) <= merge_distance or
                        abs(box[1] - existing_box[3]) <= merge_distance or
                        abs(box[3] - existing_box[1]) <= merge_distance
                ):
                    merged_boxes[i] = [
                        min(existing_box[0], box[0]),
                        min(existing_box[1], box[1]),
                        max(existing_box[2], box[2]),
                        max(existing_box[3], box[3]),
                    ]
                    merged = True
                    break
            if not merged:
                merged_boxes.append(box)
        return merged_boxes

    def verify(self, frame):
        contours_type1 = self.flexible_hsv_filter(frame)
        merged_boxes_type1 = self.refined_merge_close_contours(frame, contours_type1)

        contours_type2 = self.flexible_red_filter(frame)

        # Если обнаружены бомбочки, возвращаем False
        if merged_boxes_type1 or contours_type2:
            return False

        return True

    def find_objects_and_click(self):
        global paused
        safe = True
        x1, y1, x2, y2 = self.coordinates
        y1 += 100
        x1 += 10
        x2 -= 10
        y2 -= 400

        line_y = y1 + int((y2 - y1) * 0.75)
        detection_zone_y = line_y - 50  # Верхняя граница зоны для проверки

        new_box_x1 = x1 - 10
        new_box_x2 = x2 + 10
        new_box_y1 = detection_zone_y - 60  # Чуть ниже зоны обнаружения
        new_box_y2 = line_y + 20  # Чуть ниже линии кликов

        step = 30
        start_time = None
        time_limit = 45

        while True and (start_time is None or time.time() - start_time <= time_limit):
            if not paused:
                if start_time is None:
                    start_time = time.time()
                    logging.info("Game started. Clicking initiated.")
                    print("Game started. Clicking initiated.")

                # Снимок экрана из области проверки
                screenshot = ImageGrab.grab(bbox=(new_box_x1, new_box_y1, new_box_x2, new_box_y2))
                frame = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)

                # Проверяем наличие бомбочек
                safe = self.verify(frame)

                if safe:
                    # Если безопасно, выполняем клики
                    for x in range(x1, x2, step):
                        absolute_x = x + random.randint(-2, 2)
                        absolute_y = line_y + random.randint(-2, 2)

                        # Симуляция клика
                        win32api.SetCursorPos((absolute_x, absolute_y))
                        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
                        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)

                        time.sleep(0.02)
                else:
                    # Если небезопасно, пропускаем цикл кликов
                    print("Bomb detected. Not clicking.")
                    logging.info("Bomb detected. Skipping clicks.")

                time.sleep(random.uniform(0.01, 0.04))

            if keyboard.is_pressed('q'):
                paused = not paused
                time.sleep(0.2)
                if paused:
                    logging.info("Clicker paused")
                else:
                    logging.info("Clicker resumed")


clicker = Clicker()


def game():
    print("""
    ██████╗░██╗░░░░░██╗░░░██╗███╗░░░███╗  ░█████╗░██╗░░░░░██╗░█████╗░██╗░░██╗███████╗██████╗░
    ██╔══██╗██║░░░░░██║░░░██║████╗░████║  ██╔══██╗██║░░░░░██║██╔══██╗██║░██╔╝██╔════╝██╔══██╗
    ██████╦╝██║░░░░░██║░░░██║██╔████╔██║  ██║░░╚═╝██║░░░░░██║██║░░╚═╝█████═╝░█████╗░░██████╔╝
    ██╔══██╗██║░░░░░██║░░░██║██║╚██╔╝██║  ██║░░██╗██║░░░░░██║██║░░██╗██╔═██╗░██╔══╝░░██╔══██╗
    ██████╦╝███████╗╚██████╔╝██║░╚═╝░██║  ╚█████╔╝███████╗██║╚█████╔╝██║░╚██╗███████╗██║░░██║
    ╚═════╝░╚══════╝░╚═════╝░╚═╝░░░░░╚═╝  ░╚════╝░╚══════╝╚═╝░╚════╝░╚═╝░░╚═╝╚══════╝╚═╝░░╚═╝""")
    print("ver_without_count_rewards")
    print("INSTRUCTION")
    print("Open Blum, start script, enter the number of games, press play on main screen and watch")
    print("Press 'q' to pause(pause broke script)")
    if clicker.is_window_open():
        count = clicker.count_replay_game()
        for _ in range(count):
            clicker.find_objects_and_click()
            clicker.replay_game()
            count -= 1
            print(f"Games Left {count}")
            print("------------------------------------------------------")
        clicker.find_objects_and_click()
    print("End")


if __name__ == '__main__':
    game()
