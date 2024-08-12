import cv2
from pyzbar.pyzbar import decode
from PIL import Image, ImageDraw, ImageFont, ImageTk
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox

class QRCodeScannerApp:
    def __init__(self, root):
        # Initialize camera and font
        self.camera_id = 1
        self.cap = cv2.VideoCapture(self.camera_id)
        self.scanned_qr_data = set()
        self.current_mode = "Scan User Data"  # Default mode
        self.latest_user_data = ""  # Store the latest user data

        # Initialize font (with error handling)
        try:
            self.font = ImageFont.truetype("arial.ttf", 20)
        except IOError:
            self.font = ImageFont.load_default()  # Use default font if not found

        # Set up the GUI
        self.root = root
        self.root.title("QR Code Scanner")
        self.root.geometry("1000x700")
        self.root.configure(bg="#f0f0f0")  # Light gray background
        self.create_widgets()
        self.update_frame()

    def create_widgets(self):
        # Configure grid weights for responsiveness
        self.root.grid_rowconfigure(1, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_columnconfigure(1, weight=1)

        # User data display
        self.user_label = tk.Label(self.root, text="ชื่อพนักงาน :  ", font=("Kanit", 15), bg="#f0f0f0")
        self.user_label.grid(row=0, column=0, padx=(20, 10), pady=(15, 5), sticky="w")

        self.department = tk.Label(self.root, text="แผนก : เตา 1", font=("Kanit", 15), bg="#f0f0f0")
        self.department.grid(row=0, column=1, padx=(20, 20), pady=(15, 5), sticky="e")

        # Video frame with border
        self.video_frame = tk.Frame(self.root, bg="black", borderwidth=2, relief="solid")
        self.video_frame.grid(row=1, column=0, padx=(20, 0), pady=(0, 20), sticky="nsew")

        # Video label to fill the frame
        self.video_label = tk.Label(self.video_frame)
        self.video_label.grid(row=0, column=0, sticky="nsew")

        # Make the video label fill the frame
        self.video_frame.grid_rowconfigure(0, weight=1)
        self.video_frame.grid_columnconfigure(0, weight=1)

        # Create a frame to display scanned QR codes with delete buttons
        self.qr_listbox_frame = tk.Frame(self.root, bg="#e0e0e0", borderwidth=2, relief="solid")
        self.qr_listbox_frame.grid(row=1, column=1, padx=(20, 20), pady=(0, 20), sticky="nsew")

        # Mode toggle button
        self.mode_button = tk.Button(self.root, text="โหมดสแกนชื่อพนักงาน", font=("Kanit", 14), command=self.toggle_mode,bg="#3d85c6")
        self.mode_button.grid(row=2, column=0, padx=(20, 0), pady=30, sticky="ew")

        # Buttons at the bottom of the QR list
        self.buttons_frame = tk.Frame(self.root, bg="#f0f0f0")
        self.buttons_frame.grid(row=2, column=1, padx=(20, 20), pady=30, sticky="ew")

        # Clear button with red style
        self.clear_button = tk.Button(self.buttons_frame, text="Clear All", command=self.clear_all, bg="#cc0000", fg="white", font=("Kanit", 14), width=15)
        self.clear_button.pack(side='left', padx=(0))

        # Send button with green style
        self.send_button = tk.Button(self.buttons_frame, text="Send Data", command=self.send_data, bg="#6aa84f", fg="white", font=("Kanit", 14), width=15)
        self.send_button.pack(side='right', padx=(5, 0))

        # Initialize button states based on the default mode
        self.update_button_states()



    def toggle_mode(self):
        """Toggle between scanning QR Code data and user data."""
        if self.current_mode == "Scan QR Code":
            self.current_mode = "Scan User Data"
            self.mode_button.config(text="โหมดสแกนชื่อพนักงาน")
            self.mode_button.config(bg="#3d85c6")
        else:
            self.current_mode = "Scan QR Code"
            self.mode_button.config(text="โหมดสแกนกระจก")
            self.mode_button.config(bg="#f1c232")

        # Update button states based on the current mode
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
        ret, frame = self.cap.read()
        if not ret:
            return  # If frame capture fails, return

        # Get the current size of the video label
        frame_width = self.video_label.winfo_width() or 640
        frame_height = self.video_label.winfo_height() or 480

        # Resize frame to fit the video_label
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
        qr_frame = tk.Frame(self.qr_listbox_frame)
        qr_label = ttk.Label(qr_frame, text=qr_data, anchor='w', font=("Helvetica", 10))
        qr_label.pack(side='left', fill='x', expand=True)
        
        delete_button = tk.Button(qr_frame, text="X", command=lambda: self.delete_qr(qr_data, qr_frame), bg="#cc0000", fg="white", font=("Kanit", 14))
        delete_button.pack(side='right')

        qr_frame.pack(fill='x', padx=5, pady=3)

    def delete_qr(self, qr_data, qr_frame):
        """Delete the QR data from the frame and set."""
        qr_frame.destroy()  # Remove the frame from the UI
        self.scanned_qr_data.discard(qr_data)  # Remove the data from the set

    def send_data(self):
        """Send the scanned QR data for further processing."""
        if self.scanned_qr_data and self.latest_user_data:
            # Here you would send the data to an external system or process it.
            print("Sending data:", self.scanned_qr_data)
            
            # Display a message box indicating success
            messagebox.showinfo("Success", "ส่งข้อมูลไปยัง Appsheet สำเร็จ!")
            
            # Clear the scanned QR data
            self.clear_all()  # Use the existing clear_all method to reset the UI and data
        else:  
            messagebox.showerror("Error", "ไม่พบข้อมูลการสแกนหรือชื่อพนักงาน!")

    def clear_all(self):
        """Clear all QR data entries from the UI and the set."""
        for widget in self.qr_listbox_frame.winfo_children():
            widget.destroy()
        self.scanned_qr_data.clear()

    def __del__(self):
        # Release resources
        self.cap.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    root = tk.Tk()
    app = QRCodeScannerApp(root)
    root.mainloop()
