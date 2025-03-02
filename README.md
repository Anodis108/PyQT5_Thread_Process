# PyQT5_Thread_Process
## 1. Giới thiệu
- Tree:
```bash
├── compare_QProcess.py
├── compare_QThread.py
├── Mix_Thread_Process.py
├── multiThread_for_Proces.py
├── README.md
├── video.mp4
└── video_worker.py
```
a. compare_QProcess.py
- File này để so thực hiện tạo 1 app với n Process
- Mỗi Process sẽ có thể gọi 1 Thread từ file video_worker.py  
-> Tổng thread: m
b. compare_QThread.py
- FIle này sẽ chạy 1 loop, với n Thread tự đặt
-> Tổng Thread: n
c. Mix_Thread_Process.py
- File này chạy m Process tự đặt
- Mỗi Process sẽ chạy n Thread tự đặt trong multiThread_for_Proces.py
-> Tổng Thread: m * n
## 2. Hướng dẫn
- compare_QProcess.py: thay đổi window = MonitorWindow(5) trước khi chạy
- compare_QThread.py: thay đổi window: MainWindow = MainWindow(5) trc khi chạy
- Mix_Thread_Process.py: thay đổi window = MainWindow(5) trong file multiThread_for_MultiProces.py và window = MonitorWindow(2) trong Mix_Thread_Process.py trc khi chạy
## 3. Đánh giá
Link báo cáo: https://docs.google.com/document/d/1YCd4vDJFnISj0Dy5Ep2XLPx6E3_n_PhP-FbCkvwLo4E/edit?usp=sharing 
### Đánh giá hiệu suất của MultiProcess, MultiThread, Mix Thread and Process

| Số Thread | Phương thức              | CPU sử dụng (%) | RAM sử dụng (%) | FPS trung bình |
|-----------|--------------------------|------------------|----------------|---------------|
| **5**     | MultiProcess             | 23 %           | 50%            | 30 FPS        |
|           | MultiThread              | 26 %           | 51%            | 30 FPS        |
|           | Mix Thread and Process   | 28 %           | 51%            | 30 FPS        |
| **10**    | MultiProcess             | 34 %           | 54%            | 30 FPS        |
|           | MultiThread              | 30 %           | 54%            | 30 FPS        |
|           | Mix Thread and Process   | 34 %           | 55%            | 30 FPS        |
| **12**    | MultiProcess             | 48 %           | 57%            | 30 FPS        |
|           | MultiThread              | 54 %           | 56%            | 30 FPS        |
|           | Mix Thread and Process 6*2   | 51 %           | 56%            | 28 FPS        |
|           | Mix Thread and Process 3*4  | 81 %           | 56%            | 25 FPS        |
| **20**    | MultiProcess             | 100 %           | 61%            | 16 FPS        |
|           | MultiThread              | 68 %           | 56%            | 20 FPS        |
|           | Mix Thread and Process   | 77 %           | 56%            | 20 FPS        |
