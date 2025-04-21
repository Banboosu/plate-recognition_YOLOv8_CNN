import cv2
import torch
import tkinter as tk
from PIL import Image, ImageTk
import threading
import time
from plate_recognition.plate_rec import init_model
from detect_rec_plate import load_model, det_rec_plate, draw_result

class CameraApp:
    def __init__(self, window, window_title):
        self.window = window
        self.window.title(window_title)
        self.window.geometry('1000x700')
        
        # 初始化模型
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.detect_model = load_model(r"weights/yolov8s.pt", self.device)
        self.plate_rec_model = init_model(self.device, 'weights/plate_rec_color.pth', is_color=True)
        
        # 打印模型参数量
        total = sum(p.numel() for p in self.detect_model.parameters())
        total_1 = sum(p.numel() for p in self.plate_rec_model.parameters())
        print(f"yolov8 detect params: {total/1e6:.2f}M, rec params: {total_1/1e6:.2f}M")
        
        # 创建UI元素
        self.top_frame = tk.Frame(window)
        self.top_frame.pack(side=tk.TOP, fill=tk.X)
        
        self.btn_start = tk.Button(self.top_frame, text="开始检测", width=15, command=self.start_camera)
        self.btn_start.pack(side=tk.LEFT, padx=10, pady=10)
        
        self.btn_stop = tk.Button(self.top_frame, text="停止检测", width=15, command=self.stop_camera, state=tk.DISABLED)
        self.btn_stop.pack(side=tk.LEFT, padx=10, pady=10)
        
        self.btn_snapshot = tk.Button(self.top_frame, text="截图保存", width=15, command=self.take_snapshot, state=tk.DISABLED)
        self.btn_snapshot.pack(side=tk.LEFT, padx=10, pady=10)
        
        self.cam_label = tk.Label(self.top_frame, text="摄像头ID:")
        self.cam_label.pack(side=tk.LEFT, padx=10, pady=10)
        
        self.cam_id = tk.StringVar(value="0")
        self.cam_entry = tk.Entry(self.top_frame, textvariable=self.cam_id, width=5)
        self.cam_entry.pack(side=tk.LEFT, padx=5, pady=10)
        
        # 图像显示区域
        self.canvas = tk.Label(window)
        self.canvas.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 结果显示区域
        self.result_frame = tk.Frame(window, height=100)
        self.result_frame.pack(side=tk.BOTTOM, fill=tk.X)
        
        self.result_label = tk.Label(self.result_frame, text="车牌识别结果将显示在这里", font=("Arial", 14))
        self.result_label.pack(side=tk.TOP, pady=10)
        
        self.fps_label = tk.Label(self.result_frame, text="FPS: 0", font=("Arial", 12))
        self.fps_label.pack(side=tk.TOP, pady=5)
        
        # 摄像头变量
        self.cap = None
        self.is_running = False
        self.thread = None
        self.current_image = None
        self.last_result = ""
        
        # FPS计算变量
        self.fps_counter = 0
        self.last_time = time.time()
        self.fps = 0
        
        # 窗口关闭事件
        self.window.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        self.delay = 15  # 15ms刷新
        self.window.mainloop()
    
    def start_camera(self):
        try:
            cam_id = int(self.cam_id.get())
            self.cap = cv2.VideoCapture(cam_id)
            
            if not self.cap.isOpened():
                tk.messagebox.showerror("错误", f"无法打开摄像头 {cam_id}")
                return
            
            self.is_running = True
            self.thread = threading.Thread(target=self.update_frame)
            self.thread.daemon = True
            self.thread.start()
            
            self.btn_start.config(state=tk.DISABLED)
            self.btn_stop.config(state=tk.NORMAL)
            self.btn_snapshot.config(state=tk.NORMAL)
            self.cam_entry.config(state=tk.DISABLED)
        except Exception as e:
            tk.messagebox.showerror("错误", f"启动摄像头时发生错误: {str(e)}")
    
    def stop_camera(self):
        self.is_running = False
        if self.thread:
            self.thread.join(1.0)
        if self.cap and self.cap.isOpened():
            self.cap.release()
        
        self.btn_start.config(state=tk.NORMAL)
        self.btn_stop.config(state=tk.DISABLED)
        self.btn_snapshot.config(state=tk.DISABLED)
        self.cam_entry.config(state=tk.NORMAL)
        self.result_label.config(text="车牌识别结果将显示在这里")
        self.fps_label.config(text="FPS: 0")
    
    def update_frame(self):
        while self.is_running:
            ret, frame = self.cap.read()
            if ret:
                # 复制一份原始帧用于识别
                frame_ori = frame.copy()
                
                # 车牌检测与识别
                dict_list = det_rec_plate(frame, frame_ori, self.detect_model, self.plate_rec_model)
                
                # 在画面上绘制结果
                result_frame, result_str = draw_result(frame, dict_list)
                
                # 计算FPS
                self.fps_counter += 1
                if time.time() - self.last_time > 1.0:
                    self.fps = self.fps_counter
                    self.fps_counter = 0
                    self.last_time = time.time()
                    
                    # 更新FPS显示（在主线程中）
                    self.window.after(0, lambda: self.fps_label.config(text=f"FPS: {self.fps}"))
                
                # 更新结果（在主线程中）
                if result_str:
                    self.last_result = result_str
                    self.window.after(0, lambda: self.result_label.config(text=f"识别结果: {self.last_result}"))
                
                # 转换图像格式以在Tkinter中显示
                cv_img = cv2.cvtColor(result_frame, cv2.COLOR_BGR2RGB)
                pil_img = Image.fromarray(cv_img)
                self.current_image = ImageTk.PhotoImage(image=pil_img)
                
                # 在主线程中更新图像
                self.window.after(0, lambda: self.canvas.config(image=self.current_image))
    
    def take_snapshot(self):
        if self.current_image:
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            filename = f"snapshot_{timestamp}.jpg"
            
            # 将当前帧保存为图像文件
            if self.cap and self.cap.isOpened():
                ret, frame = self.cap.read()
                if ret:
                    frame_ori = frame.copy()
                    dict_list = det_rec_plate(frame, frame_ori, self.detect_model, self.plate_rec_model)
                    result_frame, _ = draw_result(frame, dict_list)
                    cv2.imwrite(filename, result_frame)
                    tk.messagebox.showinfo("保存成功", f"图像已保存为 {filename}")
                else:
                    tk.messagebox.showerror("错误", "无法获取摄像头画面")
            else:
                tk.messagebox.showerror("错误", "摄像头未打开")
    
    def on_closing(self):
        self.stop_camera()
        self.window.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = CameraApp(root, "摄像头车牌识别系统") 