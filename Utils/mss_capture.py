import numpy as np
import mss
import cv2


class Grabber:
    type = "mss-capture"
    cap_size_set = False

    def __init__(self):
        self.sct = mss.mss()
        self.monitor = None

    def set_cap_size(self, w, h, x=0, y=0):
        self.monitor = {
            "top": y,
            "left": x,
            "width": w,
            "height": h
        }
        self.cap_size_set = True

    def get_image(self, grab_area):
        """
        Захватывает область экрана и возвращает кадр как numpy array в RGB
        :param grab_area: словарь {'width': int, 'height': int, 'left': int, 'top': int}
        :return: np.ndarray (RGB)
        """
        if not self.cap_size_set:
            self.set_cap_size(
                grab_area['width'],
                grab_area['height'],
                grab_area.get('left', 0),
                grab_area.get('top', 0)
            )

        img = self.sct.grab(self.monitor)
        frame = np.array(img)[:, :, :3]  # Отбрасываем альфа-канал
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        return frame
