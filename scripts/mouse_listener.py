import pyperclip
import threading
import time
import keyboard  # 替换 pynput 的键盘控制功能

class TextSelector:
    def __init__(self, callback):
        """
        初始化 TextSelector 模块。
        :param callback: 在选中文字时调用的函数，接收选中的文本作为参数。
        """
        self.callback = callback  # 回调函数
        self.running = False
        self.listener_thread = None

    def is_running(self): # 判断监听器是否正在运行
        return self.running

    def start(self):
        """启动监听器"""
        self.running = True
        self.listener_thread = threading.Thread(target=self._listen)
        self.listener_thread.daemon = True
        self.listener_thread.start()

    def stop(self):
        """停止监听器"""
        self.running = False
        if self.listener_thread and self.listener_thread.is_alive():
            self.listener_thread.join()

    def _listen(self):
        """监听逻辑"""
        while self.running:
            # 检测 Ctrl+C 组合键
            if keyboard.is_pressed('ctrl+c'):
                text = self._get_selected_text()
                if text:
                    self.callback(text)  # 调用回调函数
                else:
                    print("未检测到选中文字。")
                time.sleep(0.5)  # 防止重复触发

    def _get_selected_text(self):
        """读取剪贴板内容"""
        # 使用 pyperclip 获取剪贴板内容
        try:
            time.sleep(0.1)  # 等待剪贴板刷新
            text = pyperclip.paste()
            return text if text else None
        except Exception as e:
            print(f"读取剪贴板内容时出错: {e}")
            return None
