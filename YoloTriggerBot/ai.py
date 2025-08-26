import cv2
import tkinter as tk
from PIL import Image, ImageTk
from config import config
from gui import ai_image_label

def UpdateTargetDot(x, y):
    if hasattr(config, 'canvas') and hasattr(config, 'target_dot'):
        try:
            config.canvas.coords(config.target_dot, x-3, y-3, x+3, y+3)
        except tk.TclError:
            pass

def update_gui_ai_frame(frame):
    if config.show_debug_window and 'ai_image_label' in globals():
        try:
            image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            image = Image.fromarray(image)
            image = image.resize((200, 200))
            photo = ImageTk.PhotoImage(image)
            ai_image_label.configure(image=photo)
            ai_image_label.image = photo
        except:
            print("window is not active")
