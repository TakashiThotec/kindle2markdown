import os
import pyautogui

class ScreenshotManager:
    @staticmethod
    def create_folder(folder_path):
        os.makedirs(folder_path, exist_ok=True)

    @staticmethod
    def take_screenshot(save_path, capture_rect):
        # capture_rect: (left, top, width, height)
        screenshot = pyautogui.screenshot(region=capture_rect)
        screenshot.save(save_path)

    @staticmethod
    def delete_files(file_paths):
        for f in file_paths:
            if os.path.isfile(f):
                os.remove(f)
