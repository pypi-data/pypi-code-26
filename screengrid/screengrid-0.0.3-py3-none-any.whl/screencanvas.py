import win32api, win32con, win32gui, win32ui
from typing import List
import threading
import time
import string
import uuid
import ctypes
import rectangle

# http://msdn.microsoft.com/en-us/library/windows/desktop/ff700543(v=vs.85).aspx
# Consider using: WS_EX_COMPOSITED, WS_EX_LAYERED, WS_EX_NOACTIVATE, WS_EX_TOOLWINDOW, WS_EX_TOPMOST, WS_EX_TRANSPARENT
# The WS_EX_TRANSPARENT flag makes events (like mouse clicks) fall through the window.
EX_STYLE = win32con.WS_EX_COMPOSITED | win32con.WS_EX_LAYERED | win32con.WS_EX_NOACTIVATE | win32con.WS_EX_TOPMOST | win32con.WS_EX_TRANSPARENT

# http://msdn.microsoft.com/en-us/library/windows/desktop/ms632600(v=vs.85).aspx
# Consider using: WS_DISABLED, WS_POPUP, WS_VISIBLE
STYLE = win32con.WS_DISABLED | win32con.WS_POPUP | win32con.WS_VISIBLE

class ScreenCanvas:

    def __init__(
        self,
        x = 0,
        y = 0,
        width = win32api.GetSystemMetrics(win32con.SM_CXSCREEN),
        height = win32api.GetSystemMetrics(win32con.SM_CYSCREEN)
    ):
        self.window_handle = None
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.rectangles: List[rectangle.Rectangle] = []
        self._wndClassAtom, self._hInstance = self._win32_setup()

    def add_rectangle(self, x: int, y: int, width: int, height: int, text=None):
        rect = rectangle.Rectangle(x, y, width, height, text=text)
        self.rectangles.append(rect)

    def reset(self):
        self.rectangles = []

    def render(self):
        if self.window_handle is None:
            self.window_handle = win32gui.CreateWindowEx(
                EX_STYLE,
                self._wndClassAtom,
                None, # WindowName
                STYLE,
                self.x,
                self.y,
                self.width,
                self.height,
                None, # hWndParent
                None, # hMenu
                self._hInstance,
                None # lpParam
            )
                # http://msdn.microsoft.com/en-us/library/windows/desktop/ms633540(v=vs.85).aspx
            win32gui.SetLayeredWindowAttributes(self.window_handle, 0x00ffffff, 255, win32con.LWA_COLORKEY | win32con.LWA_ALPHA)

            # http://msdn.microsoft.com/en-us/library/windows/desktop/dd145167(v=vs.85).aspx
            #win32gui.UpdateWindow(self.window_handle)

            # http://msdn.microsoft.com/en-us/library/windows/desktop/ms633545(v=vs.85).aspx
            win32gui.SetWindowPos(self.window_handle, win32con.HWND_TOPMOST, 0, 0, 0, 0,
                win32con.SWP_NOACTIVATE | win32con.SWP_NOMOVE | win32con.SWP_NOSIZE | win32con.SWP_SHOWWINDOW)
        else:
            win32gui.RedrawWindow(self.window_handle, None, None, win32con.RDW_INVALIDATE | win32con.RDW_ERASE)

    def _win_message(self, hWnd, message, wParam, lParam):
        if message == win32con.WM_PAINT:
            device_context_handle, paintStruct = win32gui.BeginPaint(hWnd)
            dpiScale = win32ui.GetDeviceCaps(device_context_handle, win32con.LOGPIXELSX) / 60.0
            fontSize = 20

            # http://msdn.microsoft.com/en-us/library/windows/desktop/dd145037(v=vs.85).aspx
            lf = win32gui.LOGFONT()
            lf.lfFaceName = "Times New Roman"
            # lf.lfHeight = int(round(dpiScale * fontSize))
            lf.lfHeight = 20
            lf.lfWeight = 0
            # Use nonantialiased to remove the white edges around the text.
            lf.lfQuality = win32con.NONANTIALIASED_QUALITY
            hf = win32gui.CreateFontIndirect(lf)
            win32gui.SelectObject(device_context_handle, hf)
            self._draw(device_context_handle)
            win32gui.EndPaint(hWnd, paintStruct)
            return 0

        elif message == win32con.WM_DESTROY:
            win32gui.PostQuitMessage(0)
            return 0

        else:
            return win32gui.DefWindowProc(hWnd, message, wParam, lParam)

    def _draw(self, device_context_handle):
        for rect in self.rectangles:
            rect.draw(device_context_handle)

    def _win32_setup(self):
        hInstance = win32api.GetModuleHandle()
        className = str(uuid.uuid4()) # probably a better way to do this

        # http://msdn.microsoft.com/en-us/library/windows/desktop/ms633576(v=vs.85).aspx
        # win32gui does not support WNDCLASSEX.
        wndClass                = win32gui.WNDCLASS()
        # http://msdn.microsoft.com/en-us/library/windows/desktop/ff729176(v=vs.85).aspx
        wndClass.style          = win32con.CS_HREDRAW | win32con.CS_VREDRAW
        wndClass.lpfnWndProc    = self._win_message
        wndClass.hInstance      = hInstance
        wndClass.hCursor        = win32gui.LoadCursor(None, win32con.IDC_ARROW)
        wndClass.hbrBackground  = win32gui.GetStockObject(win32con.WHITE_BRUSH)
        wndClass.lpszClassName  = className
        # win32gui does not support RegisterClassEx
        wndClassAtom = win32gui.RegisterClass(wndClass)
        return wndClassAtom, hInstance