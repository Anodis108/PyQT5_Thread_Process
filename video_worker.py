import sys
import time
import cv2
import psutil
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout, QScrollArea
)
from PyQt5.QtCore import Qt, QThread, QObject, pyqtSignal as Signal, pyqtSlot as Slot
from PyQt5.QtGui import QPixmap, QImage

# ✅ Worker phát video
class VideoWorker(QObject):
    frame_updated = Signal(QImage)
    fps_updated = Signal(float)  # Gửi FPS về UI
    finished = Signal()

    def __init__(self, video_path):
        super().__init__()
        self.video_path = video_path
        self.running = True
        self.is_paused: bool = False
        self.last_time = time.time()  # Thời điểm khung hình trước đó

    @Slot()
    def run(self):
        cap = cv2.VideoCapture(self.video_path)
        if not cap.isOpened():
            print(f"Không thể mở video: {self.video_path}")
            self.finished.emit()
            return

        while self.running and cap.isOpened():
            if self.is_paused:
                time.sleep(0.1)
                continue
            ret, frame = cap.read()
            if not ret:
                break

            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = frame.shape
            bytes_per_line = ch * w
            q_image = QImage(frame.data, w, h, bytes_per_line, QImage.Format_RGB888)

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

# ✅ Widget phát video
class VideoPlayerWidget(QWidget):
    def __init__(self, video_path):
        super().__init__()
        self.video_path = video_path
        self.init_ui()
        self.setup_worker()

    def init_ui(self):
        self.layout = QVBoxLayout()

        self.video_label = QLabel(self)
        self.video_label.setAlignment(Qt.AlignCenter)
        self.video_label.setFixedSize(320, 180)
        self.layout.addWidget(self.video_label)

        # ✅ Label hiển thị FPS
        self.fps_label = QLabel("FPS: 0.00", self)
        self.layout.addWidget(self.fps_label)
        
        # Thêm nút Play/Pause
        self.play_button = QPushButton("Play", self)
        self.play_button.clicked.connect(self.toggle_video)
        self.layout.addWidget(self.play_button)
    
        self.setLayout(self.layout)

    def setup_worker(self):
        self.thread: QThread  = QThread()
        self.worker = VideoWorker(self.video_path)
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

# ✅ Cửa sổ chính (10 video)
class MainWindow(QMainWindow):
    def __init__(self, num):
        super().__init__()
        self.setGeometry(100, 100, 400, 400)
        self.setWindowTitle("Multi Video Player (QThread)")
        self.video_paths = ["video.mp4"] * num  # Chạy 10 video
        self.video_widgets = []

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
        self.widget.setLayout(self.layout)

    def setup_system_usage_thread(self) -> None:
        """✅ Khởi tạo luồng cập nhật hệ thống"""
        self.system_thread: QThread = QThread()
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

# ✅ Chạy ứng dụng
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow(1)
    window.show()
    sys.exit(app.exec_())
