import sys
import time
import psutil
import subprocess
from PyQt5.QtWidgets import QApplication, QLabel, QMainWindow, QVBoxLayout, QWidget, QPushButton
from PyQt5.QtCore import QTimer, Qt, QProcess
from PyQt5.QtGui import QFont

# ✅ Hàm theo dõi CPU & RAM
def get_system_usage():
    return f"CPU: {psutil.cpu_percent()}% | RAM: {psutil.virtual_memory().percent}%"

# ✅ Cửa sổ chính để theo dõi tài nguyên hệ thống
class MonitorWindow(QMainWindow):
    def __init__(self, num_process):
        super().__init__()
        self.num_process = num_process
        self.setWindowTitle("Multi-Process Monitor (QProcess)")
        self.setGeometry(100, 100, 400, 250)

        self.label = QLabel(get_system_usage(), self)
        self.label.setFont(QFont("Arial", 14))
        self.label.setAlignment(Qt.AlignCenter)

        # ✅ Nút để dừng tất cả tiến trình
        self.stop_button = QPushButton("Stop All Processes", self)
        self.stop_button.clicked.connect(self.stop_all_processes)

        layout = QVBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(self.stop_button)

        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)

        # ✅ QTimer cập nhật thông tin CPU & RAM mỗi giây
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_usage)
        self.timer.start(1000)

        # ✅ Danh sách các tiến trình QProcess
        self.processes = []
        self.start_processes()

    def update_usage(self):
        self.label.setText(get_system_usage())

    def start_processes(self):
        """✅ Khởi chạy 2 tiến trình `multiThread_for_MultiProces.py` bằng QProcess"""
        for _ in range(self.num_process):
            process = QProcess(self)
            process.start(sys.executable, ["multiThread_for_MultiProces.py"])
            self.processes.append(process)

    def stop_all_processes(self):
        """✅ Dừng tất cả tiến trình khi nhấn nút"""
        for process in self.processes:
            if process.state() != QProcess.NotRunning:
                process.kill()
        self.processes.clear()

    def closeEvent(self, event):
        """✅ Đảm bảo dừng tất cả tiến trình khi đóng cửa sổ"""
        self.stop_all_processes()
        event.accept()

# ✅ Chạy ứng dụng PyQt5
app = QApplication(sys.argv)
window = MonitorWindow(2)
window.show()
sys.exit(app.exec_())
