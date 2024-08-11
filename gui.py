import cv2
from pyzbar.pyzbar import decode
from PIL import Image, ImageDraw, ImageFont, ImageTk
import tkinter as tk
from tkinter import ttk

class QRCodeScannerApp:
    def __init__(self, root):
        # Initialize camera and font
        self.camera_id = 1
        self.cap = cv2.VideoCapture(self.camera_id)
        self.scanned_qr_data = set()
        self.current_mode = "Scan QR Code"  # Default mode
        self.latest_user_data = ""  # Store the latest user data

        # Initialize font
        self.font = ImageFont.truetype("arial.ttf", 20)  # Adjust font size as needed

        # Set up the GUI
        self.root = root
        self.root.title("QR Code Scanner")
        self.root.geometry("1200x700")
        self.root.configure(bg="#f0f0f0")  # Light gray background
        self.create_widgets()
        self.update_frame()

    def create_widgets(self):
        # Create a style for ttk widgets
        style = ttk.Style()
        style.configure("TButton", font=("Kanit", 12), padding=6)
        style.configure("TLabel", font=("Kanit", 12), background="#f0f0f0")

        # User data display
        self.user_label = ttk.Label(self.root, text="ชื่อพนักงาน :  ", background="#f0f0f0")
        self.user_label.grid(row=0, column=0, padx=(20, 30), pady=15, sticky="w")

        self.department = ttk.Label(self.root, text="แผนก :  ", background="#f0f0f0")
        self.department.grid(row=0, column=1, padx=(20, 30), pady=15, sticky="w")

        # Video frame with border
        self.video_frame = tk.Frame(self.root, bg="black", borderwidth=2, relief="solid")
        self.video_frame.grid(row=1, column=0, padx=(20, 0), pady=(0,20), sticky="nsew")
        self.video_frame.grid_rowconfigure(0, weight=1)
        self.video_frame.grid_columnconfigure(0, weight=1)
        
        # Video label with border, set to fill the frame
        self.video_label = tk.Label(self.video_frame)
        self.video_label.grid(row=0, column=0, sticky="nsew")

        # Create a frame to display scanned QR codes with delete buttons
        self.qr_listbox_frame = tk.Frame(self.root, bg="#e0e0e0", borderwidth=2, relief="solid")
        self.qr_listbox_frame.grid(row=1, column=1, padx=(20, 20), pady=(0,20), sticky="nsew")

        # Mode toggle button
        self.mode_button = ttk.Button(self.root, text="Switch to User Data Mode", command=self.toggle_mode)
        self.mode_button.grid(row=2, column=0, padx=(20, 0), pady=30, sticky="ew")

        # Buttons at the bottom of the QR list
        buttons_frame = ttk.Frame(self.root, style="TFrame")
        buttons_frame.grid(row=2, column=1, padx=(20, 20), pady=30, sticky="ew")

        clear_button = ttk.Button(buttons_frame, text="Clear All", command=self.clear_all)
        clear_button.pack(side='left', padx=(0))

        send_button = ttk.Button(buttons_frame, text="Send Data", command=self.send_data)
        send_button.pack(side='right', padx=(5, 0))

        # Configure grid to expand
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_columnconfigure(1, weight=1)
        self.root.grid_rowconfigure(1, weight=1)


    def toggle_mode(self):
        """Toggle between scanning QR Code data and user data."""
        if self.current_mode == "Scan QR Code":
            self.current_mode = "Scan User Data"
            self.mode_button.config(text="Switch to QR Code Mode")
        else:
            self.current_mode = "Scan QR Code"
            self.mode_button.config(text="Switch to User Data Mode")

    def update_frame(self):
        ret, frame = self.cap.read()
        if not ret:
            return  # If frame capture fails, return

        # Resize frame to fit the video_label
        # Adjust the width and height according to your video_label's size
        frame_width = self.video_label.winfo_width()
        frame_height = self.video_label.winfo_height()
        frame = cv2.resize(frame, (frame_width, frame_height))

        # Decode QR codes
        barcodes = decode(frame)

        # Convert frame to RGB for PIL (needed for drawing)
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame_pil = Image.fromarray(frame_rgb)
        draw = ImageDraw.Draw(frame_pil)

        for d in barcodes:
            qr_data = d.data.decode('utf-8')

            if self.current_mode == "Scan QR Code" and qr_data not in self.scanned_qr_data:
                self.scanned_qr_data.add(qr_data)  # Add new QR data to set
                self.add_qr_to_frame(qr_data)  # Add to frame

            if self.current_mode == "Scan User Data":
                self.latest_user_data = qr_data  # Update latest user data
                self.update_user_display()

            # Draw rectangle and text on the frame
            top_left = (d.rect.left, d.rect.top)
            bottom_right = (d.rect.left + d.rect.width, d.rect.top + d.rect.height)
            draw.rectangle([top_left, bottom_right], outline=(0, 255, 0), width=3)
            draw.text((d.rect.left, d.rect.top + d.rect.height), qr_data, font=self.font, fill=(255, 0, 0))

        # Convert the image to ImageTk format for tkinter (keep RGB for Tkinter display)
        imgtk = ImageTk.PhotoImage(image=frame_pil)
        self.video_label.imgtk = imgtk
        self.video_label.configure(image=imgtk)

        # Schedule the next frame update
        self.root.after(10, self.update_frame)



    def update_user_display(self):
        """Update the displayed user data."""
        self.user_label.config(text=f"ชื่อพนักงาน : {self.latest_user_data}")

    def add_qr_to_frame(self, qr_data):
        """Add a QR data label and delete button to the frame."""
        qr_frame = ttk.Frame(self.qr_listbox_frame, padding=5)
        qr_label = ttk.Label(qr_frame, text=qr_data, anchor='w', font=("Helvetica", 10))
        delete_button = ttk.Button(qr_frame, text="Delete", command=lambda: self.delete_qr(qr_data, qr_frame))

        qr_label.pack(side='left', fill='x', expand=True)
        delete_button.pack(side='right')

        qr_frame.pack(fill='x', padx=5, pady=3)

    def delete_qr(self, qr_data, qr_frame):
        """Delete the QR data from the frame and set."""
        qr_frame.destroy()  # Remove the frame from the UI
        self.scanned_qr_data.discard(qr_data)  # Remove the data from the set

    def send_data(self):
        """Send the scanned QR data for further processing."""
        if self.scanned_qr_data:
            # Here you would send the data to an external system or process it.
            print("Sending data:", self.scanned_qr_data)
            # For this example, we'll just print it to the console.

    def clear_all(self):
        """Clear all QR data entries from the UI and the set."""
        for widget in self.qr_listbox_frame.winfo_children():
            widget.destroy()
        self.scanned_qr_data.clear()
        self.latest_user_data = ""
        self.update_user_display()

    def __del__(self):
        # Release resources
        self.cap.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    root = tk.Tk()
    app = QRCodeScannerApp(root)
    root.mainloop()
