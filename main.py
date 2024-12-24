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

    def find_objects_and_click(self):
        global paused
        x1, y1, x2, y2 = self.coordinates
        x1 += 20
        y1 += 170
        x2 -= 20
        y2 -= 400

        start_time = None
        time_limit = 45

        # Выбор линии на уровне 3/4 высоты области
        line_y = y1 + int((y2 - y1) * 0.75)
        step = 30  # Шаг между кликами на линии

        while True and (start_time is None or time.time() - start_time <= time_limit):
            if not paused:
                if start_time is None:
                    start_time = time.time()
                    logging.info("Game started. Clicking initiated.")  # Log the start
                    print("Game started. Clicking initiated.")

                # Прокликивание по линии быстро и плавно
                for x in range(x1, x2, step):
                    absolute_x = x + random.randint(-2, 2)  # Меньше отклонение для плавности
                    absolute_y = line_y + random.randint(-2, 2)

                    # Эмуляция клика
                    win32api.SetCursorPos((absolute_x, absolute_y))
                    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
                    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)

                    # Очень маленькая задержка для плавности
                    time.sleep(0.02)

                # Минимальная задержка между циклами
                delay = random.uniform(0.01, 0.08)
                time.sleep(delay)

            if keyboard.is_pressed('q'):
                paused = not paused
                time.sleep(0.2)

                if paused:
                    logging.info("Clicker paused")
                else:
                    logging.info("Clicker resumed")
        logging.info("Time limit reached or game ended. Clicking stopped.")


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