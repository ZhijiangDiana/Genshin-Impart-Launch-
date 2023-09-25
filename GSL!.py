import argparse
import time
import webbrowser
import cv2
import mss
import numpy as np
import os
import win32con, win32gui, win32api
from playsound import playsound
from threading import Thread

GSUrl = "https://ys.mihoyo.com/"
screen_Res_W = 2560
screen_Res_H = 1440

class ScreenCapture:
    """
    parameters
    ----------
        screen_frame : Tuple[int, int]
            屏幕宽高，分别为x，y
        region : Tuple[float, float]
            实际截图范围，分别为x，y，(1.0, 1.0)表示全屏检测，越低检测范围越小(始终保持屏幕中心为中心)
    """

    def __init__(self, screen_frame=(1920, 1080), region=(1, 1)):
        self.parser = argparse.ArgumentParser()
        self.parser.add_argument('--region', type=tuple, default=region,
                                 help='截图范围；分别为x，y，(1.0, 1.0)表示全屏检测，越低检测范围越小(始终保持屏幕中心为中心)')
        self.parser_args = self.parser.parse_args()

        self.cap = mss.mss()  # 实例化mss，并使用高效模式

        self.screen_width = screen_frame[0]  # 屏幕的宽
        self.screen_height = screen_frame[1]  # 屏幕的高
        self.mouse_x, self.mouse_y = self.screen_width // 2, self.screen_height // 2  # 屏幕中心点坐标

        # 截图区域
        self.GAME_WIDTH, self.GAME_HEIGHT = int(self.screen_width * self.parser_args.region[0]), int(
            self.screen_height * self.parser_args.region[1])  # 宽高
        self.GAME_LEFT, self.GAME_TOP = int(0 + self.screen_width // 2 * (1. - self.parser_args.region[0])), int(
            0 + 1080 // 2 * (1. - self.parser_args.region[1]))  # 原点

        self.monitor = {
            'left': self.GAME_LEFT,
            'top': self.GAME_TOP,
            'width': self.GAME_WIDTH,
            'height': self.GAME_HEIGHT
        }

        self.img = None

    def grab_screen_mss(self):
        # cap.grab截取图片，np.array将图片转为数组，cvtColor将BRGA转为BRG,去掉了透明通道
        return cv2.cvtColor(np.array(self.cap.grab(self.monitor)), cv2.COLOR_BGRA2BGR)

    def update_img(self, img):
        self.img = img

    def get_img(self):
        return self.img

def getGenshinPath():
    line = "1"
    path = ""
    with open('C:\Program Files\Genshin Impact\config.ini', 'r', encoding = 'utf-8') as config:
        while line!="":
            line = config.readline()
            if line.__contains__("game_install_path="):
                path = line.removeprefix("game_install_path=")
                break
        return path

def get_all_hwnd(hwnd, all_Windows):
    if (win32gui.IsWindow(hwnd) and
            win32gui.IsWindowEnabled(hwnd) and
            win32gui.IsWindowVisible(hwnd)):
        temp = [hwnd, win32gui.GetClassName(hwnd), win32gui.GetWindowText(hwnd)]
        all_Windows.append(temp)



if __name__ == '__main__':
    # cnt = 0
    path = ""
    try:
        path = getGenshinPath()
        path = path.removesuffix("\n")
        path += "/Yuanshen.exe"
    except FileNotFoundError:
        win32api.MessageBox(0, "给我马上下载原神！", "不玩原神的有难了！", win32con.MB_ICONWARNING)
        webbrowser.open(GSUrl)
        exit(0)


    # print(path)
    sc = ScreenCapture(screen_frame=(screen_Res_W, screen_Res_H))

    while True:
        img = sc.grab_screen_mss()

        R_mean = np.mean([np.mean(img[:, :, 2])])
        G_mean = np.mean([np.mean(img[:, :, 1])])
        B_mean = np.mean([np.mean(img[:, :, 0])])
        # print(str(cnt) + ": " + str(R_mean) + " " + str(G_mean) + " " + str(B_mean))
        # cnt += 1
        time.sleep(0.2)

        if (R_mean+G_mean+B_mean)/3 >= 250:
            Genshin = Thread(target=os.startfile(path))

            closeWindow = win32gui.GetForegroundWindow()
            # print(str(foreground) + " " + win32gui.GetWindowText(foreground))

            cv2.namedWindow("white_screen", cv2.WINDOW_NORMAL)
            cv2.setWindowProperty("white_screen", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
            cv2.imshow("white_screen", img)

            foreground = win32gui.FindWindow(None, "white_screen")
            win32gui.SetWindowPos(foreground, win32con.HWND_TOPMOST, 0, 0, screen_Res_W, screen_Res_H, win32con.SWP_SHOWWINDOW)
            cv2.waitKey(3)
            time.sleep(1)
            win32gui.PostMessage(closeWindow, win32con.WM_CLOSE, 0, 0)

            all_Windows = []
            hasGenshinOpened = False
            while not hasGenshinOpened:
                win32gui.EnumWindows(get_all_hwnd, all_Windows)
                # print(all_Windows)
                for window in all_Windows:
                    if window[2] == "原神":
                        # print(window)
                        win32gui.SetWindowPos(window[0], win32con.HWND_TOPMOST, 0, 0, screen_Res_W, screen_Res_H,
                                              win32con.SWP_SHOWWINDOW)
                        hasGenshinOpened = True
                        time.sleep(1)
                        # cv2.destroyAllWindows()
                        break
                all_Windows.clear()

            # print("原神，启动！")

            playsound("GSL.mp3")
            exit(0)
