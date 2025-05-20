import sys
import cv2
import numpy as np
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget, QSlider, QHBoxLayout
from PyQt5.QtGui import QFont
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QImage, QPixmap



class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Initialize HSV values
        self.hue_min, self.sat_min, self.val_min = 10, 50, 50
        self.hue_max, self.sat_max, self.val_max = 25, 255, 255

        # Set up the main window
        self.setWindowTitle("Webcam HSV Color Detection")
        self.setGeometry(100, 100, 800, 600)

        # Create a central widget and layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

        # Add a label to display the webcam feed
        self.video_label = QLabel(self)
        self.layout.addWidget(self.video_label)

        # Add trackbars for HSV adjustment
        self.create_trackbars()

        # Initialize the webcam
        self.cap = cv2.VideoCapture(1)
        if not self.cap.isOpened():
            print("Error: Could not open webcam.")
            sys.exit()

        # Set up a timer to update the webcam feed
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(20)  # Update every 20 ms

    def create_trackbars(self):
        """Create trackbars for adjusting HSV values."""
        self.hue_min_slider, self.hue_min_label = self.create_slider_with_label("Hue Min", 0, 179, self.hue_min)
        self.hue_max_slider, self.hue_max_label = self.create_slider_with_label("Hue Max", 0, 179, self.hue_max)
        self.sat_min_slider, self.sat_min_label = self.create_slider_with_label("Sat Min", 0, 255, self.sat_min)
        self.sat_max_slider, self.sat_max_label = self.create_slider_with_label("Sat Max", 0, 255, self.sat_max)
        self.val_min_slider, self.val_min_label = self.create_slider_with_label("Val Min", 0, 255, self.val_min)
        self.val_max_slider, self.val_max_label = self.create_slider_with_label("Val Max", 0, 255, self.val_max)

    def create_slider_with_label(self, label_text, min_val, max_val, default_val):
        """Helper function to create a slider with a label displaying its value."""
        # Create a horizontal layout for the slider and label
        slider_layout = QHBoxLayout()

        # Create a label for the slider
        label = QLabel(f"{label_text}: {default_val}")
        slider_layout.addWidget(label)

        # Create the slider
        slider = QSlider(Qt.Horizontal)
        slider.setMinimum(min_val)
        slider.setMaximum(max_val)
        slider.setValue(default_val)
        slider.valueChanged.connect(lambda value: label.setText(f"{label_text}: {value}"))
        slider_layout.addWidget(slider)

        # Add the slider layout to the main layout
        self.layout.addLayout(slider_layout)

        return slider, label

    def update_frame(self):
        """Update the webcam feed and apply the HSV mask."""
        ret, frame = self.cap.read()
        if not ret:
            print("Error: Could not read frame.")
            return

        # Get current trackbar values
        self.hue_min = self.hue_min_slider.value()
        self.hue_max = self.hue_max_slider.value()
        self.sat_min = self.sat_min_slider.value()
        self.sat_max = self.sat_max_slider.value()
        self.val_min = self.val_min_slider.value()
        self.val_max = self.val_max_slider.value()

        # Convert the frame to HSV
        hsv_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        # Create a mask using the HSV range
        lower_hsv = np.array([self.hue_min, self.sat_min, self.val_min])
        upper_hsv = np.array([self.hue_max, self.sat_max, self.val_max])
        mask = cv2.inRange(hsv_frame, lower_hsv, upper_hsv)

        # Apply the mask to the original frame
        result = cv2.bitwise_and(frame, frame, mask=mask)

        # Convert the result to QImage for display in PyQt
        result_rgb = cv2.cvtColor(result, cv2.COLOR_BGR2RGB)
        h, w, ch = result_rgb.shape
        bytes_per_line = ch * w
        q_img = QImage(result_rgb.data, w, h, bytes_per_line, QImage.Format_RGB888)

        # Display the result in the QLabel
        self.video_label.setPixmap(QPixmap.fromImage(q_img))

    def closeEvent(self, event):
        """Release the webcam when the window is closed."""
        self.cap.release()
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setFont(QFont("Arial"))  # Set a default font
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())