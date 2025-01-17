import keyboard

class KeyboardListener:
    def __init__(self, data_handler, ui_updater):
        self.data_handler = data_handler
        self.ui_updater = ui_updater

    def start_listening(self):
        # 左键事件
        keyboard.on_press_key("left", lambda _: self.switch_field(-1))
        # 右键事件
        keyboard.on_press_key("right", lambda _: self.switch_field(1))
        # 上键事件
        keyboard.on_press_key("up", lambda _: self.switch_character(-1))
        # 下键事件
        keyboard.on_press_key("down", lambda _: self.switch_character(1))

    def switch_field(self, direction):
        """切换字段并更新 UI"""
        self.data_handler.switch_field(direction)
        self.ui_updater.update_ui()
    
    def switch_character(self, direction):
        """切换人物并更新 UI"""
        self.data_handler.switch_character(direction)
        self.ui_updater.update_ui()

    def stop_listening(self): # 停止监听
        keyboard.unhook_all()
