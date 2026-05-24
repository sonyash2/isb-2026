import sys
import os
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QTextEdit, QFileDialog, QMessageBox,
    QGroupBox, QProgressBar, QRadioButton, QButtonGroup
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from hash_utils import calculate_hash, save_hash, verify_integrity


class HashWorker(QThread):
    """Поток для вычисления хеша без блокировки интерфейса."""
    progress = pyqtSignal(int)
    finished = pyqtSignal(str)
    error = pyqtSignal(str)
    
    def __init__(self, file_path, algorithm):
        super().__init__()
        self.file_path = file_path
        self.algorithm = algorithm
    
    def run(self):
        try:
            hash_value = calculate_hash(self.file_path, self.algorithm, progress=False)
            self.finished.emit(hash_value)
        except Exception as e:
            self.error.emit(str(e))


class VerifyWorker(QThread):
    """Поток для проверки целостности."""
    finished = pyqtSignal(bool, str, str)
    error = pyqtSignal(str)
    
    def __init__(self, file_path, hash_file):
        super().__init__()
        self.file_path = file_path
        self.hash_file = hash_file
    
    def run(self):
        try:
            is_valid, current_hash, saved_hash = verify_integrity(
                self.file_path, self.hash_file, progress=False
            )
            self.finished.emit(is_valid, current_hash, saved_hash)
        except Exception as e:
            self.error.emit(str(e))


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Контроль целостности файлов")
        self.setMinimumSize(600, 500)
        
        self.current_file = None
        self.hash_file = None
        
        self.setup_ui()
    
    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        file_group = QGroupBox("Выбор файла")
        file_layout = QHBoxLayout()
        
        self.file_label = QLabel("Файл не выбран")
        self.file_btn = QPushButton("Выбрать файл")
        self.file_btn.clicked.connect(self.select_file)
        
        file_layout.addWidget(self.file_label)
        file_layout.addWidget(self.file_btn)
        file_group.setLayout(file_layout)
        layout.addWidget(file_group)
        
        algo_group = QGroupBox("Алгоритм хеширования")
        algo_layout = QHBoxLayout()
        
        self.sha256_radio = QRadioButton("SHA-256")
        self.sha256_radio.setChecked(True)
        self.md5_radio = QRadioButton("MD5")
        self.sha1_radio = QRadioButton("SHA-1")
        
        algo_layout.addWidget(self.sha256_radio)
        algo_layout.addWidget(self.md5_radio)
        algo_layout.addWidget(self.sha1_radio)
        algo_group.setLayout(algo_layout)
        layout.addWidget(algo_group)
        
        actions_layout = QHBoxLayout()
        
        self.calc_btn = QPushButton("Вычислить хеш")
        self.calc_btn.clicked.connect(self.calculate_hash)
        self.calc_btn.setEnabled(False)
        
        self.save_btn = QPushButton("Сохранить хеш")
        self.save_btn.clicked.connect(self.save_hash)
        self.save_btn.setEnabled(False)
        
        self.verify_btn = QPushButton("Проверить целостность")
        self.verify_btn.clicked.connect(self.verify_integrity)
        self.verify_btn.setEnabled(False)
        
        actions_layout.addWidget(self.calc_btn)
        actions_layout.addWidget(self.save_btn)
        actions_layout.addWidget(self.verify_btn)
        layout.addLayout(actions_layout)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        result_group = QGroupBox("Результат")
        result_layout = QVBoxLayout()
        
        self.result_text = QTextEdit()
        self.result_text.setReadOnly(True)
        
        result_layout.addWidget(self.result_text)
        result_group.setLayout(result_layout)
        layout.addWidget(result_group)
    
    def select_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Выберите файл", "", "Все файлы (*.*)"
        )
        if file_path:
            self.current_file = file_path
            self.file_label.setText(os.path.basename(file_path))
            self.calc_btn.setEnabled(True)
            self.save_btn.setEnabled(True)
            self.verify_btn.setEnabled(True)
            self.result_text.clear()
    
    def get_algorithm(self):
        if self.sha256_radio.isChecked():
            return 'sha256'
        elif self.md5_radio.isChecked():
            return 'md5'
        else:
            return 'sha1'
    
    def calculate_hash(self):
        if not self.current_file:
            return
        
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0) 
        self.calc_btn.setEnabled(False)
        
        self.worker = HashWorker(self.current_file, self.get_algorithm())
        self.worker.finished.connect(self.on_hash_computed)
        self.worker.error.connect(self.on_error)
        self.worker.start()
    
    def on_hash_computed(self, hash_value):
        self.progress_bar.setVisible(False)
        self.calc_btn.setEnabled(True)
        
        self.result_text.clear()
        self.result_text.append("=== ВЫЧИСЛЕНИЕ ХЕША ===")
        self.result_text.append(f"Файл: {os.path.basename(self.current_file)}")
        self.result_text.append(f"Алгоритм: {self.get_algorithm().upper()}")
        self.result_text.append(f"Хеш: {hash_value}")
    
    def save_hash(self):
        if not self.current_file:
            return
       
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)
        self.save_btn.setEnabled(False)
        
        self.save_worker = HashWorker(self.current_file, self.get_algorithm())
        self.save_worker.finished.connect(self.on_hash_for_save)
        self.save_worker.error.connect(self.on_error)
        self.save_worker.start()
    
    def on_hash_for_save(self, hash_value):
        self.progress_bar.setVisible(False)
        
        hash_path = save_hash(self.current_file, hash_value)
        self.hash_file = hash_path
        
        self.result_text.clear()
        self.result_text.append("=== СОХРАНЕНИЕ ХЕША ===")
        self.result_text.append(f"Хеш сохранен в: {hash_path}")
        self.result_text.append(f"Значение: {hash_value}")
        
        self.save_btn.setEnabled(True)
    
    def verify_integrity(self):
        if not self.current_file:
            return
        
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)
        self.verify_btn.setEnabled(False)
        
        self.verify_worker = VerifyWorker(self.current_file, self.hash_file)
        self.verify_worker.finished.connect(self.on_verify_complete)
        self.verify_worker.error.connect(self.on_error)
        self.verify_worker.start()
    
    def on_verify_complete(self, is_valid, current_hash, saved_hash):
        self.progress_bar.setVisible(False)
        self.verify_btn.setEnabled(True)
        
        self.result_text.clear()
        self.result_text.append("=== ПРОВЕРКА ЦЕЛОСТНОСТИ ===")
        self.result_text.append(f"Текущий хеш: {current_hash}")
        self.result_text.append(f"Сохраненный хеш: {saved_hash}")
        
        if is_valid:
            self.result_text.append("\nРЕЗУЛЬТАТ: ФАЙЛ НЕ ИЗМЕНЕН")
            self.result_text.append("Целостность подтверждена.")
            QMessageBox.information(self, "Результат", "Файл не изменен. Целостность подтверждена.")
        else:
            self.result_text.append("\nРЕЗУЛЬТАТ: ФАЙЛ ИЗМЕНЕН")
            self.result_text.append("Целостность нарушена!")
            QMessageBox.warning(self, "Результат", "Файл был изменен! Целостность нарушена.")
    
    def on_error(self, error_msg):
        self.progress_bar.setVisible(False)
        self.calc_btn.setEnabled(True)
        self.save_btn.setEnabled(True)
        self.verify_btn.setEnabled(True)
        
        QMessageBox.critical(self, "Ошибка", error_msg)


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()