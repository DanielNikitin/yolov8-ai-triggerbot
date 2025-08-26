import threading
import pyautogui
import keyboard
from PIL import Image
from ultralytics import YOLO
import pydirectinput
import math
import os

def run_bot(decision):
    # Determine which action to take based on detected objects
    distance_target = 1000

    if "scrap" in decision:
        # Move towards the scrap location
        pyautogui.moveTo(decision["scrap_location"])
        distance_target = decision["scrap_distance"]
        print(f"Going to Scrap: {decision['scrap_location']}")
    
    if distance_target < 300:
        pydirectinput.press('1')  # Example action when close enough
        pydirectinput.press('2')  # Example action when close enough


# Function to take screenshots
def take_screenshot(stop_event, model):
    screenx_center = 3840/2
    screeny_center = 2160/2
    pyautogui.FAILSAFE = False

    while not stop_event.is_set():
        decision = {
            "scrap": False,
            "scrap_location": None,
            "scrap_distance": float('inf'),
        }

        # Take screenshot
        screenshot = pyautogui.screenshot()
        screenshot = Image.frombytes('RGB', screenshot.size, screenshot.tobytes())
        
        results = model([screenshot], conf=.70)  # return a list of Results objects
        boxes = results[0].boxes.xyxy.tolist()
        classes = results[0].boxes.cls.tolist()
        names = results[0].names
        confidences = results[0].boxes.conf.tolist()

        # Process results list
        for box, cls, conf in zip(boxes, classes, confidences):
            x1, y1, x2, y2 = box
            center_x = (x1 + x2) / 2
            center_y = (y1 + y2) / 2

            name = names[int(cls)]
            
            if name == "scrap":
                decision["scrap"] = True
                distance = ((center_x - screenx_center) ** 2 + (center_y - screeny_center) ** 2) ** 0.5
                # Update scrap location if it's closer
                if distance < decision["scrap_distance"]:
                    decision["scrap_location"] = (center_x, center_y)
                    decision["scrap_distance"] = distance
        
        run_bot(decision)


# Main function
def main():
    print(pyautogui.KEYBOARD_KEYS)
    model_path = os.path.join(os.getcwd(), "FoxholeModel_4", "exp5", "weights", "best.pt")
    
    # Load the YOLO model
    model = YOLO(model_path)

    stop_event = threading.Event()
    
    # Create and start the screenshot thread
    screenshot_thread = threading.Thread(target=take_screenshot, args=(stop_event, model))
    screenshot_thread.start()

    # Listen for keyboard input to quit the program
    keyboard.wait("q")

    # Set the stop event to end the screenshot thread
    stop_event.set()

    # Wait for the screenshot thread to finish
    screenshot_thread.join()

    print("Program ended.")

if __name__ == "__main__":
    main()
