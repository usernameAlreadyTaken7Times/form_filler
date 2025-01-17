from clipboard_handler import ClipboardHandler

class UIUpdater:
    def __init__(self, data_handler, character_field, field_label, value_label):
        self.data_handler = data_handler
        self.character_field = character_field
        self.field_label = field_label
        self.value_label = value_label

    def init_update(self):
        """初始化更新界面"""
        self.update_ui()
        pass



    def update_ui(self):
        """仅更新界面"""
        character_field = self.data_handler.get_current_person()
        current_field = self.data_handler.get_current_field()
        current_value = self.data_handler.get_current_value()

        # 更新界面显示
        self.character_field.config(text=f"当前人物：{character_field}")
        self.field_label.config(text=f"匹配字段：{current_field}")
        self.value_label.config(text=f"值(已复制到剪贴板)：{current_value}")

