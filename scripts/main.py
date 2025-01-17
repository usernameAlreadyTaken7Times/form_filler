import tkinter as tk
from data_handler import DataHandler
from ui_updater import UIUpdater
from keyboard_listener import KeyboardListener
from mouse_listener import TextSelector
import threading

from pathlib import Path
import sys, os
import time
import gc
from multiprocessing import Process

def get_script_dir(): # 获取脚本所在目录
    if getattr(sys, 'frozen', False):  # 如果是打包后的情况
        # 获取打包后的可执行文件所在的目录的上级目录
        return Path(sys.executable).parent.parent
    else:  # 如果是脚本运行情况
        # 获取脚本文件所在的目录的上级目录
        return Path(__file__).parent.parent

# 数据库文件路径
# database_path = os.path.join(get_script_dir(), 'asset/data/csv_database.csv')
database_path = os.path.join(get_script_dir(), 'asset/data/xlsx_database.xlsx')

# 语言模型文件路径
# model_path = os.path.join(get_script_dir(), 'asset/models/cc.zh.300.bin')
model_path = os.path.join(get_script_dir(), 'asset/models/merge_sgns_bigram_char300.txt.bin')

# # 读取csv数据文件
# from data_handler import PreDataHandler_csv
# dict_data = PreDataHandler_csv(database_path)

# 读取xlsx数据文件
from data_handler import PreDataHandler_xlsx
dict_data = PreDataHandler_xlsx(database_path)

# 初始化数据和其他模块

root = tk.Tk()
root.title("表格填充助手v0.2, by Y.C.")
root.geometry("270x400")
root.attributes("-topmost", 1)

# 初始化数据模块
data_handler = DataHandler(dict_data=dict_data)
# 启动独立线程运行data_handler
def start_data_handler():
    data_handler.run()

data_handler_thread = threading.Thread(target=start_data_handler, daemon=True)
data_handler_thread.start()

# 静态界面结构

# 创建选择框
module_var = tk.BooleanVar(value=False)
check_button = tk.Checkbutton(root, text="加载语言模型(视规模额外占用1.5G-2.6G内存)", variable=module_var)
check_button.pack(pady=10)

# 创建一个框架用于存放语言模型加载模块
model_frame = tk.Frame(root)
model_frame.pack(pady=10)

from synonyms_server.model import SynonymAPI

# 添加模式确认按钮
global api  # Declare api as global to modify it inside the function
api = None
choose_status = False # 选择状态

def load_module():
    """加载语言模块的操作。"""
    global api # Declare api as global to modify it inside the function
    if module_var.get():
        # 启动加载进度
        status_label["text"] = "正在等待模块加载命令..."
        if isinstance(api, SynonymAPI):
            status_label["text"] = "语言模型已加载，无需重复加载！"
            confirm_button.config(state="disabled")
            check_button.config(state="disabled")
        else:
            api = SynonymAPI(model_path=model_path)
            
            def notify_model_loaded(success: bool, error: str):
                if success:
                    print("Model loaded successfully!")
                    status_label["text"] = "语言模型加载完成！"
                    confirm_button.config(state="disabled") # 禁用确认按钮
                    check_button.config(state="disabled") # 禁用选择框
                    clear_button.config(state="normal") # 启用清除按钮
                    global choose_status
                    choose_status = True
                    start_stop_button.config(state="normal") # 启用启动服务按钮
                    person_menu.config(state="normal") # 启用选择框

                    data_handler.set_model_status(True) # 设置模型状态为True
                    data_handler.set_model_host(api.get_host()) # 设置主机地址
                    data_handler.set_model_port(api.get_port()) # 设置端口号
                else:
                    print(f"Failed to load model: {error}")
                    status_label["text"] = "语言模型加载失败！"
                    data_handler.set_model_status(False) # 设置模型状态为False
            
            api.set_model_loaded_callback(notify_model_loaded)
            status_label["text"] = "开始加载语言模型！"
            threading.Thread(target=api.run, daemon=True).start()
    else:
        # if isinstance(api, SynonymAPI):
        #     api.stop()
        #     api = None
        status_label["text"] = "不加载语言模型。"
        confirm_button.config(state="disabled")
        check_button.config(state="disabled")
        clear_button.config(state="normal")
        global choose_status
        choose_status = True
        start_stop_button.config(state="normal") # 启用启动服务按钮
        person_menu.config(state="normal") # 启用选择框
        data_handler.set_model_status(False) # 设置模型状态为False



def on_confirm():
    """点击确认按钮后的操作。"""
    # 使用线程防止阻塞主线程
    threading.Thread(target=load_module).start()

confirm_button = tk.Button(model_frame, text="确认模式", command=on_confirm)
confirm_button.pack(side="left", padx=10, pady=10)

# 添加清除按钮，用于清除选择模式
def on_clear():
    """清除语言模型的操作。"""
    global api # Declare api as global to modify it inside the function
    if isinstance(api, SynonymAPI):
        api.stop()  # Ensure the model is properly stopped
        api = None
    status_label["text"] = "模式已清除！"
    confirm_button.config(state="normal")
    check_button.config(state="normal")
    clear_button.config(state="disabled")
    start_stop_button.config(state="disabled") # 启用启动服务按钮
    person_menu.config(state="disabled") # 启用选择框
    gc.collect() # 手动回收模型内存，释放空间

clear_button = tk.Button(model_frame, text="清除模式", command=on_clear)
clear_button.config(state="disabled") # 默认不可用
clear_button.pack(side="right", padx=10, pady=10)

# 添加状态标签,用于显示加载状态
status_label = tk.Label(root, text="正在等待模块加载命令...")
status_label.pack(pady=10)

# 添加分割线
separator = tk.Frame(height=2, bd=1, relief=tk.SUNKEN)
separator.pack(fill=tk.X, padx=5, pady=5)

# 定义服务
# 鼠标监听
def on_text_selected(selected_text):
    data_handler.copy_field_value(selected_text)
    ui_updater.update_ui()

selector = TextSelector(on_text_selected)

# 初始化界面
# 创建静态标签character_label
character_label = tk.Label(root, text="当前人物：-", font=("Arial", 12))
character_label.pack(pady=10)

# 创建静态标签filed_label
field_label = tk.Label(root, text="匹配字段：-", font=("Arial", 12))
field_label.pack(pady=10)

# 创建静态标签filed_value_label
field_value_label = tk.Label(root, text="剪切板内容：-", font=("Arial", 12), fg="green")
field_value_label.pack(pady=10)

# 动态更新逻辑
ui_updater = UIUpdater(data_handler, character_label, field_label, field_value_label)
# ui_updater.update_ui()

# 键盘监听
keyboard_listener = KeyboardListener(data_handler, ui_updater)


# 创建一个框架用于存放“人物”标签、下拉菜单和按钮
choose_frame = tk.Frame(root)
choose_frame.pack(pady=20)

# 静态标签“人物”
static_label = tk.Label(choose_frame, text="人物：", font=("Arial", 12))
static_label.grid(row=0, column=0, padx=5)

# 下拉选择框
def on_person_selected(selected_person):
    data_handler.select_person(selected_person, ui_updater) # 正常刷新ui，选择人物
    if not selector.is_running():
        # 清空界面
        character_label.config(text="当前人物：-")
        field_label.config(text="匹配字段：-")
        field_value_label.config(text="剪切板内容：-")

person_var = tk.StringVar()
person_var.set(data_handler.get_first_person())  # 默认选择第一个人
person_menu = tk.OptionMenu(choose_frame, person_var, *data_handler.get_all_persons(), command=on_person_selected)
person_menu.grid(row=0, column=1, pady=5)
# person_menu.config(state="disabled")  # 默认禁用

# 启动服务按钮只在语言模型加载完成后启用
if choose_status:
    person_menu.config(state="normal")
else:
    person_menu.config(state="disabled")


# 启动/停止服务按钮
def on_start_stop():
    """启动/停止服务按钮的操作。"""
    if selector.is_running():
        selector.stop()
        keyboard_listener.stop_listening()
        start_stop_button.config(text="启动服务")
        # 清空界面
        character_label.config(text="当前人物：-")
        field_label.config(text="匹配字段：-")
        field_value_label.config(text="剪切板内容：-")
        # 禁用选择框
        person_menu.config(state="disabled")
    else:
        selector.start()
        keyboard_listener.start_listening()
        start_stop_button.config(text="停止服务")

start_stop_button = tk.Button(choose_frame, text="启动服务", command=on_start_stop)
start_stop_button.grid(row=0, column=2, pady=5)

# 启动服务按钮只在语言模型加载完成后启用
if choose_status:
    start_stop_button.config(state="normal")
else:
    start_stop_button.config(state="disabled")


# 启动主界面
root.mainloop()
