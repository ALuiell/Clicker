"""VERSION 2.0"""
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
import count_rewards


paused = False
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

    def retrieve_reward_points(self):
        global total_points
        x1, y1, x2, y2 = self.get_coords()
        coords = (x1 + 170, y1 + 345, x2 - 100, y2 - 275)
        try:
            screenshot = ImageGrab.grab(bbox=coords)
            screenshot_np = np.array(screenshot)

            count_points_for_game = count_rewards.image_to_text(screenshot_np).split()

            if count_points_for_game:
                clear = ''.join(c for c in count_points_for_game[0] if c.isdigit())
                if clear:
                    print(f'points per game: {clear}')
                    total_points += int(clear)
                else:
                    print("points per game : error")
            else:
                print("points per game : error")

        except Exception as e:
            print(f"points per game : error")
            print(f"Error: {e}")

    def replay_game(self):
        print("Try to start new game")
        self.retrieve_reward_points()
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
        y1 += 150
        x2 -= 20
        y2 -= 400

        start_time = None
        time_limit = 30

        while True and (start_time is None or time.time() - start_time <= time_limit):
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
                    if area > 15 and 0.8 < aspect_ratio < 1.2:
                        if start_time is None:
                            start_time = time.time()
                            logging.info("Game started. Clicking initiated.")  # Log the start
                            print("Game started. Clicking initiated.")

                        center_x = x + w // 2
                        center_y = y + h // 2
                        absolute_x = x1 + center_x + random.randint(-5, 5)
                        absolute_y = y1 + center_y + random.randint(-5, 5)
                        win32api.SetCursorPos((absolute_x, absolute_y))
                        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, absolute_x, absolute_y, 0, 0)
                        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, absolute_x, absolute_y, 0, 0)
                        delay = random.uniform(0.05, 0.1)
                        time.sleep(delay)
                        break

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
    print("INSTRUCTION")
    print("OPEN BLUM, START SCRIPT, ENTER THE NUMBER OF GAMES, PRESS PLAY ON MAIN SCREEN AND WATCH")
    print("Press 'q' to pause(pause broke script)")
    if clicker.is_window_open():
        count = clicker.count_replay_game()
        for _ in range(count):
            clicker.find_objects_and_click()
            clicker.replay_game()
            count -= 1
            print(f"Games Left {count + 1}")
            print("------------------------------------------------------")

        clicker.find_objects_and_click()
        clicker.retrieve_reward_points()
    print(f"total points: {total_points}")
    print("End")
    input("Press enter to quit.")


if __name__ == '__main__':
    game()
