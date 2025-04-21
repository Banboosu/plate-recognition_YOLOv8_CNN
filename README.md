   1. 建议单独创建一个虚拟环境，下载 requirements.txt 中指定的版本，不然有些模块的版本会冲突，尤其是 torch
   2. 创建好虚拟环境之后，切换到虚拟环境下，比如终端这样： (venv) PS D:\Desktop\plate-recognition_YOLOv8_CNN-main>
   3. 路径前有一个 (venv) 就说明已经在虚拟环境下了，然后在终端运行下面两个指令：

```python
python.exe -m pip install --upgrade pip
```

```python
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

4. 等待所需模块安装完成之后，运行 detect_rec_plate.py 脚本即可执行车牌检测+车牌识别程序，检测图片或视频放在【T_T_imgs】文件夹，结果将会输出到【T_T_result】文件夹

5. 运行 GUI.py 可以使用图形化界面进行车牌识别

6. 摄像头实时识别车牌功能：
   - 运行 camera_rec_plate.py 可以使用摄像头进行实时车牌识别（仅命令行界面）
   - 运行 camera_gui.py 可以使用带有图形界面的摄像头实时车牌识别系统
   - 在图形界面中，可以选择摄像头ID，开始/停止检测，以及截图保存功能

