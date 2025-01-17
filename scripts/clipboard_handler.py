import pyperclip


class ClipboardHandler:
    @staticmethod
    def get_clipboard_content():
        return pyperclip.paste().strip()

    @staticmethod
    def set_clipboard_content(content):
        pyperclip.copy(content)

