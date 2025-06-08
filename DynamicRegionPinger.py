from package_installer import install_requirements
install_requirements()  # Install missing packages before running the script

import cv2
import mss
import tkinter as tk
from tkinter import Button
import numpy as np
import time
import winsound
import cv2
import os


class ScreenCaptureApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Select Monitor")
        self.selected_monitor = None
        self.region = None
        self.reference = cv2.imread( "ReferenceImage.png", cv2.IMREAD_UNCHANGED)  # Load reference image

        # Get available monitors
        with mss.mss() as sct:
            self.monitors = sct.monitors[1:]  # Ignore primary (full display)
        
        # Create buttons for each monitor
        for idx, mon in enumerate(self.monitors):
            btn = Button(self.root, text=f"Monitor {idx+1}: {mon['width']}x{mon['height']}",
                         command=lambda m=mon: self.select_monitor(m))
            btn.pack()
        
        self.root.mainloop()

    def select_monitor(self, monitor):
        """Select monitor and close the Tkinter window."""
        self.selected_monitor = monitor
        self.root.destroy()  # Close Tkinter window
        self.capture_screen()

    def capture_screen(self):
        """Capture and display full-screen image of selected monitor."""
        with mss.mss() as sct:
            screenshot = sct.grab(self.selected_monitor)
        
        img = np.array(screenshot)
        img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)  # Convert to BGR
        
        # Show image and enable region selection
        cv2.imshow("Select Region", img)
        cv2.setMouseCallback("Select Region", self.select_region, img)
        cv2.waitKey(0)
        cv2.destroyAllWindows()  # Close previous screen

    def select_region(self, event, x, y, flags, img):
        """Allow user to drag-select a region and save selection."""
        if event == cv2.EVENT_LBUTTONDOWN:
            self.region = [x, y]  # Start point
        elif event == cv2.EVENT_LBUTTONUP:
            self.region += [x, y]  # End point
            
            # Ensure valid region coordinates
            if self.region[2] > self.region[0] and self.region[3] > self.region[1]:
                cropped_img = img[self.region[1]:self.region[3], self.region[0]:self.region[2]]
                cv2.imshow("Selected Region Only", cropped_img)
                cv2.waitKey(1)
                cv2.destroyAllWindows()

                # **Write monitor & region selection to file**
                save_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "selected_region.txt")
                with open(save_path, "w") as file:
                    file.write(f"Monitor: {self.selected_monitor['width']}x{self.selected_monitor['height']}\n")
                    file.write(f"Selected Region: {self.region}\n")

                print(f"Selection saved to {save_path}")

                # Move straight into scanning
                self.scan_region()


    def scan_region(self):
        """Continuously scan the selected screen region for a matching icon and display it."""
        print("Scanning region for match...")
        match_active = False
        match_count = 0
        max_match_limit = 5
        cooldown_time = 2
        last_detection_time = 0

        while True:
            time.sleep(0.5)  # Reduce CPU load
            
            with mss.mss() as sct:
                screenshot = sct.grab({
                    "top": self.selected_monitor["top"] + self.region[1],
                    "left": self.selected_monitor["left"] + self.region[0],
                    "width": self.region[2] - self.region[0],
                    "height": self.region[3] - self.region[1]
                })
            
            img = np.array(screenshot)
            img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
            img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            reference_gray = cv2.cvtColor(self.reference, cv2.COLOR_BGR2GRAY)

            result = cv2.matchTemplate(img_gray, reference_gray, cv2.TM_CCOEFF_NORMED)
            threshold = 0.92
            locations = np.where(result >= threshold)

            if locations[0].size > 0 and (time.time() - last_detection_time > cooldown_time):
                last_detection_time = time.time()
                match_count += 1
                print("Match found!")
                winsound.Beep(1000, 300)

                if match_count > max_match_limit:
                    break
            
            # **Update the displayed region**
            cv2.imshow("Scanning Selected Region", img)

            # **Check if window was closed**
            if cv2.getWindowProperty("Scanning Selected Region", cv2.WND_PROP_VISIBLE) < 1:
                print("Window closed. Exiting...")
                break
            
            if cv2.waitKey(1) & 0xFF == 27:  # Press 'Esc' to exit loop
                break

        cv2.destroyAllWindows()  # Close when scanning stops
        exit()  # **Ensure program exits completely**



if __name__ == "__main__":
    ScreenCaptureApp()
