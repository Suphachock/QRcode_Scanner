import cv2
from pyzbar.pyzbar import decode
from PIL import Image, ImageDraw, ImageFont
import numpy as np

camera_id = 1
delay = 1
window_name = 'OpenCV pyzbar'

# Open the camera
cap = cv2.VideoCapture(camera_id)
scanned_qr_data = set()  # Store decoded data to avoid duplicates

while True:
    ret, frame = cap.read()
    if not ret:
        break  # Exit loop if frame capture fails

    # Decode QR codes
    barcodes = decode(frame)

    # Convert frame to RGB for PIL
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    frame_pil = Image.fromarray(frame_rgb)
    draw = ImageDraw.Draw(frame_pil)

    for d in barcodes:
        qr_data = d.data.decode('utf-8')

        if qr_data not in scanned_qr_data:
            scanned_qr_data.add(qr_data)  # Add new QR data to set
            print(qr_data)

        # Draw rectangle and text on the frame
        top_left = (d.rect.left, d.rect.top)
        bottom_right = (d.rect.left + d.rect.width, d.rect.top + d.rect.height)
        draw.rectangle([top_left, bottom_right], outline=(1, 255, 0), width=3)
        draw.text((d.rect.left, d.rect.top + d.rect.height), qr_data, fill=(0, 0, 255))

    # Convert back to BGR format for OpenCV
    frame_bgr = cv2.cvtColor(np.array(frame_pil), cv2.COLOR_RGB2BGR)

    # Display the frame
    cv2.imshow(window_name, frame_bgr)

    key = cv2.waitKey(delay) & 0xFF

    if key == ord('q'):
        break

# Release resources
cap.release()
cv2.destroyAllWindows()
