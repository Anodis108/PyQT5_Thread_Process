import sys
import time
import cv2
import psutil
from typing import List
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout, QScrollArea
)
from PyQt5.QtCore import Qt, QThread, QObject, pyqtSignal as Signal, pyqtSlot as Slot
from PyQt5.QtGui import QPixmap, QImage

# ✅ Hàm lấy thông tin CPU & RAM
def get_system_usage() -> str:
    cpu_usage: float = psutil.cpu_percent()
    ram_usage: float = psutil.virtual_memory().percent
    return f"CPU: {cpu_usage}% | RAM: {ram_usage}%"

# ✅ Worker cập nhật thông tin hệ thống
class SystemUsageWorker(QObject):
    updated: Signal = Signal(str)  # Gửi tín hiệu cập nhật UI

    def __init__(self) -> None:
        super().__init__()
        self.running: bool = True

    @Slot()
    def update_system_usage(self) -> None:
        while self.running:
            system_usage: str = get_system_usage()
            self.updated.emit(system_usage)  # Gửi tín hiệu
            time.sleep(1)
            
# ✅ Worker phát video (Chạy trong luồng riêng)
class VideoWorker(QObject):
    frame_updated: Signal = Signal(QImage)  # Gửi frame mới về UI
    fps_updated = Signal(float)  # Gửi FPS về UI
    finished: Signal = Signal()  # Khi video kết thúc

    def __init__(self, video_path: str) -> None:
        super().__init__()
        self.video_path: str = video_path
        self.running: bool = True
        self.is_paused: bool = False
        self.last_time = time.time()  # Thời điểm khung hình trước đó

    @Slot()
    def run(self) -> None:
        cap: cv2.VideoCapture = cv2.VideoCapture(self.video_path)
        if not cap.isOpened():
            print("Không mở được video!")
            self.finished.emit()
            return

        while self.running and cap.isOpened():
            if self.is_paused:
                time.sleep(0.1)
                continue

            ret: bool
            frame: cv2.typing.MatLike
            ret, frame = cap.read()
            if not ret:
                break

            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h: int
            w: int
            ch: int
            h, w, ch = frame.shape
            bytes_per_line: int = ch * w
            q_image: QImage = QImage(frame.data, w, h, bytes_per_line, QImage.Format_RGB888)

            # Tính toán FPS
            current_time = time.time()
            fps = 1.0 / (current_time - self.last_time)
            self.last_time = current_time  # Cập nhật thời gian
            
            self.frame_updated.emit(q_image)
            self.fps_updated.emit(fps)
            
            time.sleep(0.03)  # Giả lập tốc độ video

        cap.release()
        if self.running:
            self.finished.emit()

# ✅ Widget riêng cho từng video
class VideoPlayerWidget(QWidget):
    def __init__(self, video_path: str) -> None:
        super().__init__()
        self.video_path: str = video_path
        self.init_ui()
        self.setup_worker()

    def init_ui(self) -> None:
        self.layout: QVBoxLayout = QVBoxLayout()

        # ✅ Label hiển thị video
        self.video_label: QLabel = QLabel(self)
        self.video_label.setAlignment(Qt.AlignCenter)
        self.video_label.setFixedSize(640, 360)
        self.layout.addWidget(self.video_label)

        # ✅ Label hiển thị FPS
        self.fps_label = QLabel("FPS: 0.00", self)
        self.layout.addWidget(self.fps_label)
        
        # ✅ Nút Play/Pause riêng
        self.play_button: QPushButton = QPushButton("Play")
        self.play_button.clicked.connect(self.toggle_video)
        self.layout.addWidget(self.play_button)

        self.setLayout(self.layout)

    def setup_worker(self) -> None:
        """✅ Khởi tạo Worker và QThread cho video"""
        self.thread: QThread = QThread()
        self.worker: VideoWorker = VideoWorker(self.video_path)
        self.worker.moveToThread(self.thread)

        self.thread.started.connect(self.worker.run)
        self.worker.frame_updated.connect(self.update_frame)
        self.worker.fps_updated.connect(self.update_fps)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)

        # ✅ Tự động khởi chạy video ngay khi ứng dụng khởi động
        self.thread.start()
        self.play_button.setText("Pause")
        
    def toggle_video(self) -> None:
        """✅ Play/Pause video"""
        if not self.thread.isRunning():
            self.thread.start()
            self.play_button.setText("Pause")
        else:
            self.worker.is_paused = not self.worker.is_paused
            self.play_button.setText("Play" if self.worker.is_paused else "Pause")

    @Slot(QImage)
    def update_frame(self, q_image: QImage) -> None:
        """✅ Cập nhật frame lên QLabel"""
        pixmap: QPixmap = QPixmap.fromImage(q_image).scaled(640, 360, Qt.KeepAspectRatio)
        self.video_label.setPixmap(pixmap)

    @Slot(float)
    def update_fps(self, fps: float) -> None:
        """✅  Cập nhật FPS lên QLabel"""
        self.fps_label.setText(f"FPS: {fps:.2f}")
    
    def stop_video(self) -> None:
        """✅ Dừng video khi đóng ứng dụng"""
        self.worker.running = False
        self.thread.quit()
        self.thread.wait()

# ✅ Giao diện chính
class MainWindow(QMainWindow):
    def __init__(self, num_thread) -> None:
        super().__init__()
        self.setGeometry(100, 100, 700, 800)
        self.setWindowTitle("Multi Video Player (QThread)")
        self.video_paths: List[str] = ["video.mp4"] * num_thread  # Danh sách video
        self.video_widgets: List[VideoPlayerWidget] = []
        
        self.init_ui()
        self.setup_system_usage_thread()

    def init_ui(self) -> None:
        self.widget: QWidget = QWidget()
        self.setCentralWidget(self.widget)

        self.layout: QVBoxLayout = QVBoxLayout()
        
        # ✅ ScrollArea chứa video
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_widget = QWidget()
        self.video_layout: QHBoxLayout = QHBoxLayout(self.scroll_widget)
        
        # ✅ Thêm nhiều VideoPlayerWidget
        for video_path in self.video_paths:
            video_widget: VideoPlayerWidget = VideoPlayerWidget(video_path)
            self.video_widgets.append(video_widget)
            self.video_layout.addWidget(video_widget)

        self.scroll_area.setWidget(self.scroll_widget)
        self.layout.addWidget(self.scroll_area)
        
        self.system_usage_label: QLabel = QLabel(get_system_usage(), self)
        self.layout.addWidget(self.system_usage_label)

        self.widget.setLayout(self.layout)

    def setup_system_usage_thread(self) -> None:
        """✅ Khởi tạo luồng cập nhật hệ thống"""
        self.system_thread: QThread = QThread()
        self.system_worker: SystemUsageWorker = SystemUsageWorker()
        self.system_worker.moveToThread(self.system_thread)

        self.system_thread.started.connect(self.system_worker.update_system_usage)
        self.system_worker.updated.connect(self.system_usage_label.setText)

        self.system_thread.start()

    def closeEvent(self, event) -> None:
        """✅ Đảm bảo dừng tất cả luồng khi đóng cửa sổ"""
        for video_widget in self.video_widgets:
            video_widget.stop_video()

        if hasattr(self, 'system_worker'):
            self.system_worker.running = False
            self.system_thread.quit()
            self.system_thread.wait()

        event.accept()

# ✅ Chạy ứng dụng PyQt5
app: QApplication = QApplication(sys.argv)
window: MainWindow = MainWindow(5)
window.show()
sys.exit(app.exec_())
