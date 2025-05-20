import sys
import cv2
import numpy as np
import serial
import serial.tools.list_ports
from PyQt5.QtWidgets import (
    QApplication, QWidget, QPushButton, QVBoxLayout, QLabel, QComboBox, QMessageBox, QGroupBox, QHBoxLayout
)
from PyQt5.QtCore import QThread, pyqtSignal, Qt
from PyQt5.QtGui import QImage, QPixmap


# Thread for OpenCV video capture and color detection
class VideoThread(QThread):
    change_pixmap_signal = pyqtSignal(QImage)  # Signal to send frames to the GUI

    def __init__(self, serial_port=None, baudrate=9600):
        super().__init__()
        self._run_flag = True  # Flag to control the thread
        self._color_detected = False  # Flag to track if color is currently detected
        self.serial_port = serial_port
        self.baudrate = baudrate
        self.serial_connection = None
        self.boolSendSer = [False,False,False]
        self.countour_val = [0,0,0]

    def run(self):
        # Define the HSV ranges for the colors to detect
        # lower_red = np.array([3, 138, 217])
        # upper_red = np.array([7, 199, 255])
        lower_red = np.array([7, 197, 209])
        upper_red = np.array([12, 214, 238])

        # lower_green = np.array([48, 65, 147])
        # upper_green = np.array([69, 255, 255])
        lower_green = np.array([34, 122, 106])
        upper_green = np.array([67, 191, 199])

        lower_yellow = np.array([22, 151, 166])
        upper_yellow = np.array([55, 255, 255])


        # Start webcam
        cap = cv2.VideoCapture(1)

        while self._run_flag:
            ret, frame = cap.read()
            if not ret:
                break

            # Convert the frame to HSV color space
            hsv_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

            # Create masks for each color
            mask_red = cv2.inRange(hsv_frame, lower_red, upper_red)
            mask_green = cv2.inRange(hsv_frame, lower_green, upper_green)
            mask_yellow = cv2.inRange(hsv_frame, lower_yellow, upper_yellow)

            # Combine masks to detect any of the three colors
            combined_mask = cv2.bitwise_or(mask_red, cv2.bitwise_or(mask_green, mask_yellow))

            # Find contours in the combined mask
            contours, _ = cv2.findContours(combined_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            # self._color_detected = False
           
                
            # Draw bounding boxes and labels for detected colors
            for contour in contours:
                x, y, w, h = cv2.boundingRect(contour)

                # Determine which color is detected
                if cv2.contourArea(contour) > 400:  # Filter out small contours
                    # Check for red
                    if np.any(mask_red[y:y+h, x:x+w]):
                        self.countour_val[2] = contour
                        color = "Red"
                        if not self.boolSendSer[2] and self.serial_connection :
                            self.serial_connection.write(b'<2>\n')
                            self.boolSendSer[2] = True 
                            for i in range(len(self.boolSendSer)):
                                if i!=2:
                                    self.boolSendSer[i] = False
                        box_color = (0, 0, 255)  # Red in BGR
                    # Check for green
                    elif np.any(mask_green[y:y+h, x:x+w]):
                        self.countour_val[1] = contour
                        color = "Green"
                        if not self.boolSendSer[1] and self.serial_connection :
                            self.serial_connection.write(b'<1>\n')
                            self.boolSendSer[1] = True   
                            for i in range(len(self.boolSendSer)):
                                if i!=1:
                                    self.boolSendSer[i] = False         
                        box_color = (0, 255, 0)  # Green in BGR
                    # Check for yellow
                    elif np.any(mask_yellow[y:y+h, x:x+w]):
                        self.countour_val[0] = contour
                        color = "Yellow"
                        if not self.boolSendSer[0] and self.serial_connection :
                            self.serial_connection.write(b'<0>\n')
                            self.boolSendSer[0] = True
                            for i in range(len(self.boolSendSer)):
                                if i!=0:
                                    self.boolSendSer[i] = False 
                        box_color = (0, 255, 255)  # Yellow in BGR
                    else:
                        color = "no"
                        for i in range(len(self.boolSendSer)):
                            self.boolSendSer[i] = False
                        # self._color_detected = False
                        continue

                    # Draw bounding box and label
                    cv2.rectangle(frame, (x, y), (x + w, y + h), box_color, 2)
                    cv2.putText(frame, color, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, box_color, 2)

                    # Send serial output only once when color is detected
                    # if  self.serial_connection and self._color_detected == False :
                    #     # self.serial_connection.write(f'<{print_color}>\n'.encode())  # Send color name over serial
                    #     self.serial_connection.write(b'halo 0\n')
                    #     self._color_detected = True  # Set flag to True
                        
                    

            # Reset the flag when no color is detected
            if not contours:
                # self._color_detected = False
                for i in range(len(self.boolSendSer)):
                    self.boolSendSer[i] = False

            # Convert the frame to RGB for display in the GUI
            rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = rgb_image.shape
            bytes_per_line = ch * w
            qt_image = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)

            # Emit the signal to update the GUI
            self.change_pixmap_signal.emit(qt_image)

        # Release the webcam and close the serial port when the thread stops
        cap.release()
        if self.serial_connection:
            self.serial_connection.close()

    def stop(self):
        """Stop the thread."""
        self._run_flag = False
        self.wait()

    def set_serial_connection(self, port, baudrate):
        """Initialize the serial connection."""
        try:
            self.serial_connection = serial.Serial(port, baudrate)
            return True
        except Exception as e:
            print(f"Serial connection error: {e}")
            return False
        
    def set_serial_disconnect(self):
        """Initialize the serial connection."""
        try:
            self.serial_connection.close()
            return True
        except Exception as e:
            print(f"Serial connection error: {e}")
            return False


# Main GUI Window
class App(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Deteksi Tomat dengan OpenCV")
        self.setGeometry(100, 100, 800, 600)

        self.f_connectSerial = False
        # Create a label to display the video feed
        self.image_label = QLabel(self)
        self.image_label.setAlignment(Qt.AlignCenter)  # Center the video feed
        self.image_label.setMinimumSize(640, 480)  # Set minimum size for the video feed

        # Create a group box for serial settings
        self.serial_group = QGroupBox("Serial Settings", self)

        # Create drop-down menus for serial port and baud rate
        self.port_combo = QComboBox(self)
        self.baudrate_combo = QComboBox(self)
        self.baudrate_combo.addItems(["9600", "19200", "38400", "57600", "115200"])

        # Populate the serial port drop-down
        self.populate_serial_ports()

        # Create buttons
        self.connect_button = QPushButton("Connect Serial", self)
        # self.connect_button.clicked.connect(self.clickSerial)
        # Layout for the serial group
        serial_layout = QHBoxLayout()
        serial_layout.addWidget(QLabel("Port:"))
        serial_layout.addWidget(self.port_combo)
        serial_layout.addWidget(QLabel("Baud Rate:"))
        serial_layout.addWidget(self.baudrate_combo)
        serial_layout.addWidget(self.connect_button)
        self.serial_group.setLayout(serial_layout)

        # Create buttons for start and stop detection
        self.start_button = QPushButton("Start Detection", self)
        self.stop_button = QPushButton("Stop Detection", self)

        # Connect buttons to functions
        self.connect_button.clicked.connect(self.initiate_serial)
        self.start_button.clicked.connect(self.start_detection)
        self.stop_button.clicked.connect(self.stop_detection)

        # Main layout
        layout = QVBoxLayout()
        layout.addWidget(self.image_label)
        layout.addWidget(self.serial_group)
        layout.addWidget(self.start_button)
        layout.addWidget(self.stop_button)
        self.setLayout(layout)

        # Video thread
        self.video_thread = VideoThread()
        self.video_thread.change_pixmap_signal.connect(self.update_image)

    # def clickSerial(self):
    #     self.connect_button.setText("Disconnect Serial")
    
    def populate_serial_ports(self):
        """Populate the serial port drop-down with available ports."""
        try:
            ports = serial.tools.list_ports.comports()
            if not ports:
                print("No COM ports found using `serial.tools.list_ports.comports()`.")
                # Fallback for Windows
                if sys.platform == 'win32':
                    for i in range(256):
                        port_name = f'COM{i}'
                        try:
                            ser = serial.Serial(port_name)
                            ser.close()
                            self.port_combo.addItem(port_name)
                            print(f"Found port: {port_name}")
                        except serial.SerialException:
                            pass
                # Fallback for Linux/Mac
                else:
                    import glob
                    ports = glob.glob('/dev/ttyUSB*') + glob.glob('/dev/ttyACM*')
                    for port in ports:
                        self.port_combo.addItem(port)
                        print(f"Found port: {port}")
            else:
                for port in ports:
                    print(f"Found port: {port.device} - {port.description}")
                    self.port_combo.addItem(port.device)
        except Exception as e:
            print(f"Error while fetching COM ports: {e}")
    
    def initiate_serial(self):
        """Initialize the serial connection."""
        port = self.port_combo.currentText()
        baudrate = int(self.baudrate_combo.currentText())
        if not self.f_connectSerial:
            if self.video_thread.set_serial_connection(port, baudrate):
                QMessageBox.information(self, "Berhasil", "Terhubung Ke Port Serial")
                self.connect_button.setText("Disconnect Serial")
            else:
                QMessageBox.critical(self, "Error", "Gagal terhubung.")
            self.f_connectSerial = True
        elif self.f_connectSerial:
            if self.video_thread.set_serial_disconnect():
                QMessageBox.information(self, "Berhasil", "Terputus dari Serial!")
                self.connect_button.setText("Connect Serial")
            else:
                QMessageBox.critical(self, "Error", "Gagal Terputus dari Serial.")
            self.f_connectSerial = False

    def start_detection(self):
        """Start the video thread."""
        self.video_thread.start()

    def stop_detection(self):
        """Stop the video thread."""
        self.video_thread.stop()

    def update_image(self, qt_image):
        """Update the image label with a new frame."""
        self.image_label.setPixmap(QPixmap.fromImage(qt_image).scaled(
            self.image_label.width(), self.image_label.height(), Qt.KeepAspectRatio
        ))


# Run the application
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = App()
    window.show()
    sys.exit(app.exec_())