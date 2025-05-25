import pyautogui
import ctypes

try:
    import pygetwindow as gw
except ImportError:
    gw = None

class KindleController:
    @staticmethod
    def activate_kindle(window_title="Kindle for PC") -> bool:
        """Kindle for PC のウィンドウを前面化し、成功可否を返す"""
        if not gw:
            print("pygetwindow not installed; cannot activate Kindle window.")
            return False
        # 完全一致で探す
        windows = gw.getWindowsWithTitle(window_title)
        if windows:
            hwnd = windows[0]._hWnd
            # ウィンドウを復元＆前面化
            SW_RESTORE = 9
            ctypes.windll.user32.ShowWindow(hwnd, SW_RESTORE)
            ctypes.windll.user32.SetForegroundWindow(hwnd)
            return True
        # 部分一致で再検索
        candidates = [w for w in gw.getAllWindows() if window_title.lower() in w.title.lower()]
        if candidates:
            hwnd = candidates[0]._hWnd
            SW_RESTORE = 9
            ctypes.windll.user32.ShowWindow(hwnd, SW_RESTORE)
            ctypes.windll.user32.SetForegroundWindow(hwnd)
            return True
        # デバッグ用タイトル表示
        titles = [w.title for w in gw.getAllWindows()]
        print(f"No window matching '{window_title}'. Available titles:\n{titles}")
        return False

    @staticmethod
    def send_page_turn(key="left"):
        """指定したキーでページ送りを行う"""
        pyautogui.press(key)
