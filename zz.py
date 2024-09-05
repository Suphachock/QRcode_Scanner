import cv2
from pyzbar.pyzbar import decode
from PIL import Image, ImageDraw, ImageTk
import ttkbootstrap as ttk
from ttkbootstrap.dialogs import Messagebox
import sys

if sys.platform == 'linux':
    from picamera2 import Picamera2
    import RPi.GPIO as GPIO

class QRCodeScannerApp:
    def __init__(self, root):
        """Initialize the QR Code Scanner application."""
        self.root = root
        self.scanned_qr_data = set()
        self.current_mode = "Scan User Data"
        self.latest_user_data = ""

        self.setup_camera()
        self.setup_gpio()

        self.root.title("Beautiful GUI with ttkbootstrap")
        self.root.geometry("800x600")
        self.style = ttk.Style()
        self.style.configure("TLabel", font=("Kanit", 15))
        self.style.configure("TButton", font=("Kanit", 14))

        self.create_widgets()
        self.update_frame()

    def setup_camera(self):
        """Initialize the camera based on the platform."""
        if sys.platform == 'linux':
            self.cap = Picamera2()
            # self.cap.configure(self.cap.create_preview_configuration(main={"size": (640, 480)}))
            self.cap.start()
            self.cap.set_controls({"AfMode": 2},{"FrameRate": 60})
            
        else:
            self.cap = cv2.VideoCapture(0)


    def setup_gpio(self):
        """Initialize GPIO pins for button interactions."""
        if sys.platform == 'linux':
            GPIO.setmode(GPIO.BCM)
            self.mode_button_pin = 17
            self.clear_button_pin = 27
            self.send_button_pin = 22

            GPIO.setup(self.mode_button_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
            GPIO.setup(self.clear_button_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
            GPIO.setup(self.send_button_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

            GPIO.add_event_detect(self.mode_button_pin, GPIO.FALLING, callback=self.toggle_mode, bouncetime=300)
            GPIO.add_event_detect(self.clear_button_pin, GPIO.FALLING, callback=lambda channel: self.clear_all(), bouncetime=300)
            GPIO.add_event_detect(self.send_button_pin, GPIO.FALLING, callback=lambda channel: self.send_data(), bouncetime=300)

    def create_widgets(self):
        """Create and layout the GUI widgets."""
        self.root.grid_rowconfigure(1, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_columnconfigure(1, weight=1)

        self.user_label = ttk.Label(self.root, text="ชื่อพนักงาน :  ")
        self.user_label.grid(row=0, column=0, padx=(20, 10), pady=(15, 5), sticky="w")

        self.department = ttk.Label(self.root, text="แผนก : เตา 1")
        self.department.grid(row=0, column=1, padx=(20, 20), pady=(15, 5), sticky="e")

        self.video_frame = ttk.Frame(self.root, bootstyle="dark", borderwidth=2, relief="solid")
        self.video_frame.grid(row=1, column=0, padx=(20, 0), pady=(0, 20), sticky="nsew")

        self.video_label = ttk.Label(self.video_frame)
        self.video_label.grid(row=0, column=0, sticky="nsew")
        self.video_frame.grid_rowconfigure(0, weight=1)
        self.video_frame.grid_columnconfigure(0, weight=1)

        self.qr_listbox_frame = ttk.Frame(self.root, bootstyle="secondary", borderwidth=2, relief="solid")
        self.qr_listbox_frame.grid(row=1, column=1, padx=(20, 20), pady=(0, 20), sticky="nsew")

        self.mode_button = ttk.Button(self.root, text="โหมดสแกนชื่อพนักงาน", bootstyle="primary", command=self.toggle_mode)
        self.mode_button.grid(row=2, column=0, padx=(20, 0), pady=30, sticky="ew")

        self.buttons_frame = ttk.Frame(self.root)
        self.buttons_frame.grid(row=2, column=1, padx=(20, 20), pady=30, sticky="ew")

        self.clear_button = ttk.Button(self.buttons_frame, text="Clear All", bootstyle="danger", command=self.clear_all, width=15)
        self.clear_button.pack(side='left', padx=(0))

        self.send_button = ttk.Button(self.buttons_frame, text="Send Data", bootstyle="success", command=self.send_data, width=15)
        self.send_button.pack(side='right', padx=(5, 0))

        self.update_button_states()

    def toggle_mode(self):
        """Toggle between scanning QR Code data and user data."""
        if self.current_mode == "Scan QR Code":
            self.current_mode = "Scan User Data"
            self.mode_button.config(text="โหมดสแกนชื่อพนักงาน", bootstyle="primary")
        else:
            self.current_mode = "Scan QR Code"
            self.mode_button.config(text="โหมดสแกนกระจก", bootstyle="warning")

        self.update_button_states()

    def update_button_states(self):
        """Enable or disable buttons based on the current mode."""
        if self.current_mode == "Scan User Data":
            self.clear_button["state"] = "disabled"
            self.send_button["state"] = "disabled"
        else:
            self.clear_button["state"] = "normal"
            self.send_button["state"] = "normal"

    def update_frame(self):
        """Capture and process each video frame."""
        if sys.platform == 'linux':
            frame = self.cap.capture_array()
        else:
            ret, frame = self.cap.read()
            if not ret:
                return

        frame_width = self.video_label.winfo_width()
        frame_height = self.video_label.winfo_height()

        frame = cv2.resize(frame, (frame_width, frame_height))

        barcodes = decode(frame)
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame_pil = Image.fromarray(frame_rgb)
        draw = ImageDraw.Draw(frame_pil)

        for d in barcodes:
            qr_data = d.data.decode('utf-8')

            if self.current_mode == "Scan QR Code" and qr_data not in self.scanned_qr_data:
                self.scanned_qr_data.add(qr_data)
                self.add_qr_to_frame(qr_data)

            if self.current_mode == "Scan User Data":
                self.latest_user_data = qr_data
                self.update_user_display()

            top_left = (d.rect.left, d.rect.top)
            bottom_right = (d.rect.left + d.rect.width, d.rect.top + d.rect.height)
            draw.rectangle([top_left, bottom_right], outline=(0, 255, 0), width=3)
            draw.text((d.rect.left, d.rect.top + d.rect.height), qr_data, fill=(255, 0, 0))

        imgtk = ImageTk.PhotoImage(image=frame_pil)
        self.video_label.imgtk = imgtk
        self.video_label.configure(image=imgtk)

        self.root.after(10, self.update_frame)

    def update_user_display(self):
        """Update the displayed user data."""
        self.user_label.config(text=f"ชื่อพนักงาน : {self.latest_user_data}")

    def add_qr_to_frame(self, qr_data):
        """Add a QR data label and delete button to the frame."""
        qr_frame = ttk.Frame(self.qr_listbox_frame)
        qr_label = ttk.Label(qr_frame, text=qr_data, anchor='w', font=("Helvetica", 16))
        qr_label.pack(side='left', fill='x', expand=True)

        # delete_button = ttk.Button(qr_frame, text="X", command=lambda: self.delete_qr(qr_data, qr_frame), bootstyle="danger", width=2)
        # delete_button.pack(side='right')

        qr_frame.pack(fill='x', padx=5, pady=3)

    # def delete_qr(self, qr_data, qr_frame):
    #     """Delete the QR data from the frame and set."""
    #     qr_frame.destroy()
    #     self.scanned_qr_data.discard(qr_data)

    def send_data(self):
        """Send the scanned QR data for further processing."""
        if self.scanned_qr_data and self.latest_user_data:
            print("Sending data:", self.scanned_qr_data)
            Messagebox.show_info("ส่งข้อมูลไปยัง Appsheet สำเร็จ!", "Success")
            self.clear_all()
        else:
            Messagebox.show_error("ไม่พบข้อมูลการสแกนหรือชื่อพนักงาน!", "Error")

    def clear_all(self):
        """Clear all QR data entries from the UI and the set."""
        for widget in self.qr_listbox_frame.winfo_children():
            widget.destroy()
        self.scanned_qr_data.clear()

    def __del__(self):
        """Clean up resources."""
        if sys.platform == 'linux':
            GPIO.cleanup()
        if self.cap:
            self.cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    root = ttk.Window(themename="superhero")
    app = QRCodeScannerApp(root)
    root.mainloop()
