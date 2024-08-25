import tkinter as tk
from PIL import Image, ImageTk, ImageDraw, ImageFont
import cv2
from pyzbar.pyzbar import decode
import numpy as np

class SimpleApp:
    def __init__(self, root):
        self.root = root
        self.root.title("โปรแกรมสแกนกระจกแผนกเตา 1")
        self.root.state("zoomed")
        
        # Initialize camera and scanned QR data set
        self.cap = cv2.VideoCapture(0)  # Use camera ID 1 as per your original code
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        
        self.scanned_qr_data = set()
        
        self.create_widgets()
        self.update_camera_frame()

    def create_widgets(self):
        
        # ส่วนหัวข้อ
        self.title_frame = tk.Label(self.root, text="โหมดสแกนรหัสพนักงาน", bg="lightblue", font=("Kanit", 30),height=2)
        self.title_frame.grid(row=0, column=0, columnspan=2, sticky="nsew")
        # --------------------------------------------------------

        # ส่วนภาพจากกล้อง
        self.camera_frame = tk.Label(self.root, bg="lightgreen")
        self.camera_frame.grid(row=1, column=0, sticky="nsew")
        # --------------------------------------------------------

        # ส่วน List รายการ
        self.itemList_frame = tk.Label(self.root, text="Section 3", bg="lightcoral")
        self.itemList_frame.grid(row=1, column=1, sticky="nsew")
        # --------------------------------------------------------
        
        # ส่วนชื่อพนักงาน
        self.employee_frame = tk.Label(self.root, text="รหัสพนักงาน : 00000000 ชื่อ: XXXXXXXXX XXXXXXXXX", bg="red", font=("Kanit", 20),height=2)
        self.employee_frame.grid(row=2, column=0, sticky="wns", padx=(20, 0))
        # --------------------------------------------------------

        # ส่วนปุ่ม
        self.button_frame = tk.Label(self.root, bg="yellow",height=2)
        self.button_frame.grid(row=2, column=1, sticky="nsew")
        
        self.clear_button = tk.Button(self.button_frame, text="Clear All", bg="#cc0000", fg="white", font=("Kanit", 20), width=15)
        self.clear_button.pack(side='left')
        
        self.send_button = tk.Button(self.button_frame, text="Send Data", bg="#6aa84f", fg="white", font=("Kanit", 20), width=15)
        self.send_button.pack(side='right')
        # --------------------------------------------------------

        # Configure row and column weights for resizing
        self.root.grid_columnconfigure(0, weight=4)
        self.root.grid_columnconfigure(1, weight=1)
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_rowconfigure(1, weight=1)
        self.root.grid_rowconfigure(2, weight=1)

    def update_camera_frame(self):
        ret, frame = self.cap.read()
        if not ret:
            return

        # Resize frame to fit the video_label
        frame_width = self.camera_frame.winfo_width() or 640
        frame_height = self.camera_frame.winfo_height() or 480
        frame = cv2.resize(frame, (frame_width, frame_height))
        
        # Decode QR codes
        barcodes = decode(frame)

        # Convert frame to RGB for PIL
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame_pil = Image.fromarray(frame_rgb)
        draw = ImageDraw.Draw(frame_pil)

        for d in barcodes:
            qr_data = d.data.decode('utf-8')

            if qr_data not in self.scanned_qr_data:
                self.scanned_qr_data.add(qr_data)  # Add new QR data to set
                print(qr_data)

            # Draw rectangle and text on the frame
            top_left = (d.rect.left, d.rect.top)
            bottom_right = (d.rect.left + d.rect.width, d.rect.top + d.rect.height)
            draw.rectangle([top_left, bottom_right], outline=(1, 255, 0), width=3)
            draw.text((d.rect.left, d.rect.top + d.rect.height), qr_data, fill=(0, 0, 255))

        # Convert back to BGR format for OpenCV
        frame_bgr = cv2.cvtColor(np.array(frame_pil), cv2.COLOR_RGB2BGR)

        # Convert to ImageTk for display in Tkinter
        imgtk = ImageTk.PhotoImage(image=frame_pil)
        self.camera_frame.imgtk = imgtk
        self.camera_frame.config(image=imgtk)

        self.root.after(10, self.update_camera_frame)

        
    def on_closing(self):
        self.cap.release()  # Release the camera when closing the app
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = SimpleApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()
