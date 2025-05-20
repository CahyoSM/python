import os
import sys
from PIL import Image
from PyQt5.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, 
                             QLabel, QPushButton, QLineEdit, QComboBox, QFileDialog, 
                             QMessageBox, QGroupBox)

class ImageConverterApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Image Converter - Resize dan Ubah Ekstensi")
        self.setGeometry(100, 100, 500, 350)
        
        self.initUI()
        
    def initUI(self):
        # Widget utama
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        
        # Layout utama
        main_layout = QVBoxLayout()
        main_widget.setLayout(main_layout)
        
        # Group untuk memilih gambar
        input_group = QGroupBox("Input Gambar")
        input_layout = QVBoxLayout()
        
        self.btn_select_file = QPushButton("Pilih File Gambar")
        self.btn_select_file.clicked.connect(self.select_file)
        self.lbl_selected_file = QLabel("Tidak ada file dipilih")
        
        input_layout.addWidget(self.btn_select_file)
        input_layout.addWidget(self.lbl_selected_file)
        input_group.setLayout(input_layout)
        
        # Group untuk resize
        resize_group = QGroupBox("Resize Gambar")
        resize_layout = QHBoxLayout()
        
        lbl_width = QLabel("Width:")
        self.entry_width = QLineEdit()
        self.entry_width.setPlaceholderText("Kosongkan untuk mempertahankan rasio")
        
        lbl_height = QLabel("Height:")
        self.entry_height = QLineEdit()
        self.entry_height.setPlaceholderText("Kosongkan untuk mempertahankan rasio")
        
        resize_layout.addWidget(lbl_width)
        resize_layout.addWidget(self.entry_width)
        resize_layout.addWidget(lbl_height)
        resize_layout.addWidget(self.entry_height)
        resize_group.setLayout(resize_layout)
        
        # Group untuk ubah ekstensi
        convert_group = QGroupBox("Ubah Ekstensi")
        convert_layout = QHBoxLayout()
        
        lbl_format = QLabel("Format Output:")
        self.combo_format = QComboBox()
        self.combo_format.addItems(["jpg", "png", "webp", "bmp", "tiff", "gif"])
        
        convert_layout.addWidget(lbl_format)
        convert_layout.addWidget(self.combo_format)
        convert_group.setLayout(convert_layout)
        
        # Group untuk output
        output_group = QGroupBox("Output")
        output_layout = QVBoxLayout()
        
        self.btn_select_output = QPushButton("Pilih Folder Output")
        self.btn_select_output.clicked.connect(self.select_output_folder)
        self.lbl_output_folder = QLabel("Output akan disimpan di folder yang sama dengan input")
        
        output_layout.addWidget(self.btn_select_output)
        output_layout.addWidget(self.lbl_output_folder)
        output_group.setLayout(output_layout)
        
        # Tombol generate
        self.btn_generate = QPushButton("Generate")
        self.btn_generate.clicked.connect(self.process_image)
        
        # Tambahkan semua group ke layout utama
        main_layout.addWidget(input_group)
        main_layout.addWidget(resize_group)
        main_layout.addWidget(convert_group)
        main_layout.addWidget(output_group)
        main_layout.addWidget(self.btn_generate)
        
        # Variabel untuk menyimpan path
        self.input_file = ""
        self.output_folder = ""
        
    def select_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Pilih File Gambar", "", 
            "Image Files (*.jpg *.jpeg *.png *.bmp *.tiff *.gif *.webp)"
        )
        
        if file_path:
            self.input_file = file_path
            self.lbl_selected_file.setText(file_path)
            
            # Set folder output default ke folder yang sama dengan input
            self.output_folder = os.path.dirname(file_path)
    
    def select_output_folder(self):
        folder_path = QFileDialog.getExistingDirectory(self, "Pilih Folder Output")
        
        if folder_path:
            self.output_folder = folder_path
            self.lbl_output_folder.setText(f"Output akan disimpan di: {folder_path}")
    
    def process_image(self):
        if not self.input_file:
            QMessageBox.warning(self, "Peringatan", "Silakan pilih file gambar terlebih dahulu!")
            return
            
        try:
            # Buka gambar
            img = Image.open(self.input_file)
            
            # Resize gambar
            width = self.entry_width.text()
            height = self.entry_height.text()
            
            if width or height:
                # Dapatkan ukuran asli
                original_width, original_height = img.size
                
                # Hitung ukuran baru
                new_width = int(width) if width else original_width
                new_height = int(height) if height else original_height
                
                # Jika salah satu dimensi kosong, pertahankan rasio aspek
                if not width:
                    ratio = new_height / original_height
                    new_width = int(original_width * ratio)
                elif not height:
                    ratio = new_width / original_width
                    new_height = int(original_height * ratio)
                
                img = img.resize((new_width, new_height), Image.LANCZOS)
            
            # Tentukan format output
            output_format = self.combo_format.currentText()
            
            # Tentukan nama file output
            base_name = os.path.splitext(os.path.basename(self.input_file))[0]
            output_filename = f"{base_name}_converted.{output_format}"
            
            # Jika folder output tidak dipilih, gunakan folder yang sama dengan input
            output_path = os.path.join(self.output_folder, output_filename)
            
            # Simpan gambar
            if output_format.lower() == 'jpg' or output_format.lower() == 'jpeg':
                img.convert('RGB').save(output_path, quality=95)
            else:
                img.save(output_path)
            
            QMessageBox.information(self, "Sukses", f"Gambar berhasil diproses dan disimpan di:\n{output_path}")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Terjadi kesalahan saat memproses gambar:\n{str(e)}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ImageConverterApp()
    window.show()
    sys.exit(app.exec_())