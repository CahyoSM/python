import sys
import os
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton,
    QFileDialog, QTableWidget, QTableWidgetItem, QComboBox,
    QMessageBox, QLabel
)
from PyQt5.QtCore import Qt
from PIL import Image

class ImageResizerApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Image Resizer & Format Converter")
        self.setGeometry(100, 100, 500, 400)

        self.image_path = None

        layout = QVBoxLayout()

        self.select_btn = QPushButton("Pilih Gambar")
        self.select_btn.clicked.connect(self.select_image)
        layout.addWidget(self.select_btn)

        self.image_label = QLabel("Belum ada gambar dipilih.")
        layout.addWidget(self.image_label)

        self.table = QTableWidget(3, 2)
        self.table.setHorizontalHeaderLabels(["Width", "Height"])
        layout.addWidget(self.table)

        self.ext_dropdown = QComboBox()
        self.ext_dropdown.addItems(["JPEG", "PNG", "BMP", "WEBP"])
        layout.addWidget(self.ext_dropdown)

        self.convert_btn = QPushButton("Resize & Convert")
        self.convert_btn.clicked.connect(self.process_image)
        layout.addWidget(self.convert_btn)

        self.setLayout(layout)

    def select_image(self):
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(self, "Pilih Gambar", "", "Images (*.png *.jpg *.jpeg *.bmp *.webp)")
        if file_path:
            self.image_path = file_path
            self.image_label.setText(f"Gambar: {os.path.basename(file_path)}")

    def process_image(self):
        if not self.image_path:
            QMessageBox.warning(self, "Error", "Silakan pilih gambar terlebih dahulu.")
            return

        try:
            img = Image.open(self.image_path)
            output_format = self.ext_dropdown.currentText().lower()
            base_name = os.path.splitext(os.path.basename(self.image_path))[0]

            output_dir = os.path.join(os.path.dirname(self.image_path), "output")
            os.makedirs(output_dir, exist_ok=True)

            for row in range(self.table.rowCount()):
                try:
                    width_item = self.table.item(row, 0)
                    height_item = self.table.item(row, 1)
                    if not width_item or not height_item:
                        continue
                    width = int(width_item.text())
                    height = int(height_item.text())
                    resized = img.resize((width, height), Image.Resampling.LANCZOS)
                    output_path = os.path.join(output_dir, f"{base_name}_{width}x{height}.{output_format}")
                    resized.save(output_path, output_format.upper())
                except Exception as e:
                    print(f"Error at row {row}: {e}")
            QMessageBox.information(self, "Sukses", f"Gambar berhasil diproses dan disimpan di folder: {output_dir}")
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ImageResizerApp()
    window.show()
    sys.exit(app.exec_())
