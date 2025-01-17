import tkinter as tk

def toggle_button():
    global button  # 引用全局变量
    if button is None:  # 如果按钮未定义
        button = tk.Button(root, text="动态创建的按钮", command=button_action)
        button.pack(pady=10)
        status_label.config(text="按钮已创建")
    else:  # 如果按钮已定义
        button.destroy()  # 销毁按钮
        button = None
        status_label.config(text="按钮已销毁")

def button_action():
    status_label.config(text="按钮被点击！")

# 创建主窗口
root = tk.Tk()
root.title("动态组件示例")
root.geometry("300x200")

# 占位符初始化
button = None

# 控制按钮的切换按钮
toggle_btn = tk.Button(root, text="切换按钮状态", command=toggle_button)
toggle_btn.pack(pady=10)

# 状态标签
status_label = tk.Label(root, text="等待操作...")
status_label.pack(pady=20)

# 运行主窗口
root.mainloop()
