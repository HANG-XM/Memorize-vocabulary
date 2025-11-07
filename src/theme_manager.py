# src/theme_manager.py
from PyQt6.QtCore import QObject, pyqtSignal
from PyQt6.QtWidgets import QApplication
from enum import Enum

class Theme(Enum):
    LIGHT = "light"
    DARK = "dark"
    BLUE = "blue"
    GREEN = "green"

class ThemeManager(QObject):
    theme_changed = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self._current_theme = Theme.LIGHT
        self._themes = {
            Theme.LIGHT: {
                'background': '#ffffff',      # 纯白背景
                'text': '#212121',           # 深灰色文字
                'button': '#f5f5f5',         # 浅灰按钮
                'button_hover': '#e0e0e0',   # 悬停时的浅灰
                'accent': '#1976d2',         # 蓝色主调
                'secondary': '#424242',      # 次要文字
                'border': '#bdbdbd',         # 边框颜色
                'success': '#4caf50',        # 成功绿色
                'error': '#f44336',          # 错误红色
                'warning': '#ff9800',        # 警告橙色
                'combo_bg': '#ffffff',       # 下拉框背景
                'combo_text': '#212121',     # 下拉框文字
                'list_bg': '#ffffff',        # 列表背景
                'list_text': '#212121',      # 列表文字
                'list_selected': '#1976d2',  # 列表选中颜色
                'radio_text': '#212121',     # 单选按钮文字颜色
                'radio_indicator': '#1976d2', # 单选按钮指示器颜色
            },
            Theme.DARK: {
                'background': '#121212',      # 更深的背景
                'text': '#ffffff',            # 纯白文字
                'button': '#2d2d2d',          # 深灰按钮
                'button_hover': '#3d3d3d',    # 悬停时的浅灰
                'accent': '#90caf9',          # 浅蓝色主调
                'secondary': '#b0b0b0',       # 次要文字
                'border': '#404040',          # 边框颜色
                'success': '#81c784',         # 成功绿色
                'error': '#e57373',           # 错误红色
                'warning': '#ffb74d',         # 警告橙色
                'combo_bg': '#2d2d2d',        # 下拉框背景
                'combo_text': '#ffffff',      # 下拉框文字
                'list_bg': '#2d2d2d',         # 列表背景
                'list_text': '#ffffff',       # 列表文字
                'list_selected': '#90caf9',   # 列表选中颜色
                'radio_text': '#ffffff',     # 单选按钮文字颜色
                'radio_indicator': '#90caf9', # 单选按钮指示器颜色
            },
            Theme.BLUE: {
                'background': '#f3f8ff',      # 浅蓝背景
                'text': '#0d47a1',            # 深蓝文字
                'button': '#e3f2fd',          # 浅蓝按钮
                'button_hover': '#bbdefb',    # 悬停时的蓝色
                'accent': '#1976d2',          # 蓝色主调
                'secondary': '#1565c0',       # 次要文字
                'border': '#90caf9',          # 边框颜色
                'success': '#4caf50',         # 成功绿色
                'error': '#f44336',           # 错误红色
                'warning': '#ff9800',         # 警告橙色
                'combo_bg': '#e3f2fd',        # 下拉框背景
                'combo_text': '#0d47a1',      # 下拉框文字
                'list_bg': '#e3f2fd',         # 列表背景
                'list_text': '#0d47a1',       # 列表文字
                'list_selected': '#1976d2',  # 列表选中颜色
                'radio_text': '#0d47a1',     # 单选按钮文字颜色
                'radio_indicator': '#1976d2', # 单选按钮指示器颜色
            },
            Theme.GREEN: {
                'background': '#f1f8e9',      # 浅绿背景
                'text': '#1b5e20',            # 深绿文字
                'button': '#dcedc8',          # 浅绿按钮
                'button_hover': '#c5e1a5',    # 悬停时的绿色
                'accent': '#388e3c',          # 绿色主调
                'secondary': '#2e7d32',       # 次要文字
                'border': '#81c784',          # 边框颜色
                'success': '#4caf50',         # 成功绿色
                'error': '#f44336',           # 错误红色
                'warning': '#ff9800',         # 警告橙色
                'combo_bg': '#dcedc8',        # 下拉框背景
                'combo_text': '#1b5e20',      # 下拉框文字
                'list_bg': '#dcedc8',         # 列表背景
                'list_text': '#1b5e20',       # 列表文字
                'list_selected': '#388e3c',  # 列表选中颜色
                'radio_text': '#1b5e20',     # 单选按钮文字颜色
                'radio_indicator': '#388e3c', # 单选按钮指示器颜色
            }
        }
    
    def get_current_theme(self):
        return self._current_theme
    
    def set_theme(self, theme: Theme):
        self._current_theme = theme
        self.theme_changed.emit(theme.value)
    
    def get_style(self, element: str):
        return self._themes[self._current_theme].get(element, '')
