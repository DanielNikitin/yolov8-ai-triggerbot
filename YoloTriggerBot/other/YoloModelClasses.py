from ultralytics import YOLO
model = YOLO("testCS2.pt")
print(model.names)
