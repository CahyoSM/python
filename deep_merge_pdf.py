import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QPushButton, QListWidget, QLabel, QFileDialog, QMessageBox)
from PyQt5.QtCore import Qt
from PyPDF2 import PdfMerger

class PDFMergerApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PDF Merger")
        self.setGeometry(100, 100, 600, 400)
        
        self.initUI()
        self.pdf_files = []
    
    def initUI(self):
        # Widget utama
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        
        # Layout utama
        main_layout = QVBoxLayout()
        main_widget.setLayout(main_layout)
        
        # Label judul
        title_label = QLabel("PDF Merger - Gabungkan File PDF")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title_label)
        
        # List widget untuk menampilkan file PDF
        self.list_widget = QListWidget()
        main_layout.addWidget(self.list_widget)
        
        # Layout untuk tombol
        button_layout = QHBoxLayout()
        
        # Tombol tambah file
        add_button = QPushButton("Tambah PDF")
        add_button.clicked.connect(self.add_pdf)
        button_layout.addWidget(add_button)
        
        # Tombol hapus file
        remove_button = QPushButton("Hapus Terpilih")
        remove_button.clicked.connect(self.remove_pdf)
        button_layout.addWidget(remove_button)
        
        # Tombol naikkan urutan
        up_button = QPushButton("Naikkan")
        up_button.clicked.connect(self.move_up)
        button_layout.addWidget(up_button)
        
        # Tombol turunkan urutan
        down_button = QPushButton("Turunkan")
        down_button.clicked.connect(self.move_down)
        button_layout.addWidget(down_button)
        
        main_layout.addLayout(button_layout)
        
        # Tombol merge
        merge_button = QPushButton("Gabungkan PDF")
        merge_button.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold;")
        merge_button.clicked.connect(self.merge_pdfs)
        main_layout.addWidget(merge_button)
        
        # Status bar
        self.statusBar().showMessage("Siap")
    
    def add_pdf(self):
        files, _ = QFileDialog.getOpenFileNames(
            self, "Pilih file PDF", "", "PDF Files (*.pdf)"
        )
        
        if files:
            for file in files:
                if file not in self.pdf_files:
                    self.pdf_files.append(file)
                    self.list_widget.addItem(file)
            
            self.statusBar().showMessage(f"{len(self.pdf_files)} file PDF ditambahkan")
    
    def remove_pdf(self):
        selected_items = self.list_widget.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Peringatan", "Tidak ada file yang dipilih untuk dihapus")
            return
            
        for item in selected_items:
            self.pdf_files.remove(item.text())
            self.list_widget.takeItem(self.list_widget.row(item))
        
        self.statusBar().showMessage(f"{len(selected_items)} file dihapus")
    
    def move_up(self):
        current_row = self.list_widget.currentRow()
        if current_row > 0:
            item_text = self.list_widget.takeItem(current_row)
            self.list_widget.insertItem(current_row - 1, item_text)
            self.list_widget.setCurrentRow(current_row - 1)
            
            # Update list pdf_files
            self.pdf_files.insert(current_row - 1, self.pdf_files.pop(current_row))
    
    def move_down(self):
        current_row = self.list_widget.currentRow()
        if current_row < self.list_widget.count() - 1 and current_row >= 0:
            item_text = self.list_widget.takeItem(current_row)
            self.list_widget.insertItem(current_row + 1, item_text)
            self.list_widget.setCurrentRow(current_row + 1)
            
            # Update list pdf_files
            self.pdf_files.insert(current_row + 1, self.pdf_files.pop(current_row))
    
    def merge_pdfs(self):
        if len(self.pdf_files) < 2:
            QMessageBox.warning(self, "Peringatan", "Minimal 2 file PDF untuk digabungkan")
            return
            
        output_file, _ = QFileDialog.getSaveFileName(
            self, "Simpan PDF Gabungan", "", "PDF Files (*.pdf)"
        )
        
        if not output_file:
            return
            
        if not output_file.lower().endswith('.pdf'):
            output_file += '.pdf'
        
        try:
            merger = PdfMerger()
            
            for pdf in self.pdf_files:
                merger.append(pdf)
            
            merger.write(output_file)
            merger.close()
            
            QMessageBox.information(self, "Sukses", f"File PDF berhasil digabungkan dan disimpan sebagai:\n{output_file}")
            self.statusBar().showMessage("Penggabungan selesai")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Terjadi kesalahan saat menggabungkan PDF:\n{str(e)}")
            self.statusBar().showMessage("Gagal menggabungkan PDF")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PDFMergerApp()
    window.show()
    sys.exit(app.exec_())