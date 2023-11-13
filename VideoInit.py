import cv2
from ultralytics import YOLO

def gen_frames(videopath):
    model = YOLO("trained_data/best.pt", "v8")  # Make sure this path is correct
    class_list = ["NonViolence", "Violence"]  # Update this list based on your model's classes

    cap = cv2.VideoCapture(videopath)
    
    if not cap.isOpened():
        # If the video can't be opened, yield an empty frame or an error message
        yield (b'--frame\r\nContent-Type: image/jpeg\r\n\r\n' + 
               b'No video' + b'\r\n')
        return

    while True:
        success, frame = cap.read()
        if not success:
            break

        # Video processing and object detection
        detect_params = model.predict(source=[frame], conf=0.1, save=False)
        for box in detect_params[0].boxes:
            clsID = box.cls.numpy()[0]
            conf = box.conf.numpy()[0]
            bb = box.xyxy.numpy()[0]
            
            x1 = int(bb[0])
            x2 = int(bb[2])
            y1 = int(bb[1])
            y2 = int(bb[3])
           
            text = class_list[int(clsID)]
            cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 255, 0), 3)
            font = cv2.FONT_HERSHEY_COMPLEX
            cv2.putText(frame, text, (x1, y1), font, 1, (255, 255, 255), 2)

        # Encode the frame in JPEG format
        (flag, encodedImage) = cv2.imencode(".jpg", frame)
        if not flag:
            continue

        # Yield the frame as a byte stream
        yield (b'--frame\r\nContent-Type: image/jpeg\r\n\r\n' + 
               bytearray(encodedImage) + b'\r\n')

    cap.release()
