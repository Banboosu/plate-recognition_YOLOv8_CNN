1. 创建虚拟环境：
   安装 [uv](https://docs.astral.sh/uv/getting-started/)：
   使用终端
```
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

```
uv venv -p 3.11
uv pip install -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt
```

2. 等待所需模块安装完成之后，运行 detect_rec_plate.py 脚本即可执行车牌检测+车牌识别程序，检测图片或视频放在【T_T_imgs】文件夹，结果将会输出到【T_T_result】文件夹

3. 运行 GUI.py 可以使用图形化界面进行车牌识别

4. 摄像头实时识别车牌功能：
   - 运行 camera_rec_plate.py 可以使用摄像头进行实时车牌识别（仅命令行界面）
   - 运行 camera_gui.py 可以使用带有图形界面的摄像头实时车牌识别系统
   - 在图形界面中，可以选择摄像头 ID，开始/停止检测，以及截图保存功能
