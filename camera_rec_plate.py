import cv2
import torch
import time
import numpy as np
from plate_recognition.plate_rec import init_model
from detect_rec_plate import load_model, det_rec_plate, draw_result

def main():
    # 初始化模型
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    detect_model = load_model(r"weights/yolov8s.pt", device)
    plate_rec_model = init_model(device, 'weights/plate_rec_color.pth', is_color=True)
    
    # 打印模型参数量
    total = sum(p.numel() for p in detect_model.parameters())
    total_1 = sum(p.numel() for p in plate_rec_model.parameters())
    print("yolov8 detect params: %.2fM, rec params: %.2fM" % (total / 1e6, total_1 / 1e6))
    
    # 设置摄像头
    cap = cv2.VideoCapture(0)  # 使用默认摄像头，如果有多个摄像头，可以改为1,2等
    
    # 检查摄像头是否成功打开
    if not cap.isOpened():
        print("无法打开摄像头")
        return
    
    # 获取摄像头的帧宽和帧高
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    
    # 设置窗口
    cv2.namedWindow("车牌识别", cv2.WINDOW_NORMAL)
    cv2.resizeWindow("车牌识别", width, height)
    
    # 设置视频保存
    save_video = False  # 是否保存视频
    if save_video:
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter('camera_result.mp4', fourcc, fps, (width, height))
    
    print("按 'q' 键退出")
    
    last_time = time.time()
    fps_counter = 0
    fps_display = 0
    
    while True:
        ret, frame = cap.read()
        
        if not ret:
            print("无法获取画面")
            break
        
        # 复制一份原始帧用于识别
        frame_ori = frame.copy()
        
        # 车牌检测与识别
        dict_list = det_rec_plate(frame, frame_ori, detect_model, plate_rec_model)
        
        # 在画面上绘制结果
        result_frame, result_str = draw_result(frame, dict_list)
        
        # 计算帧率
        fps_counter += 1
        if time.time() - last_time > 1.0:
            fps_display = fps_counter
            fps_counter = 0
            last_time = time.time()
        
        # 在画面上显示帧率
        cv2.putText(result_frame, f"FPS: {fps_display}", (10, 30), 
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        
        # 显示处理后的画面
        cv2.imshow("车牌识别", result_frame)
        
        # 如果需要保存视频
        if save_video:
            out.write(result_frame)
        
        # 按 'q' 退出
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    # 释放资源
    cap.release()
    if save_video:
        out.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main() 