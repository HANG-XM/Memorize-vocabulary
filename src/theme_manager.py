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
                'background': '#fafafa',      # 柔和的浅灰背景
                'background_secondary': '#ffffff', # 卡片背景
                'text': '#1a1a1a',           # 深黑色文字，更好的对比度
                'text_secondary': '#666666', # 次要文字
                'button': '#f0f0f0',         # 浅灰按钮
                'button_hover': '#e0e0e0',   # 悬停时的浅灰
                'button_active': '#d0d0d0',  # 激活状态的按钮
                'accent': '#1976d2',         # 蓝色主调
                'accent_light': '#e3f2fd',   # 浅蓝色
                'secondary': '#424242',      # 次要文字
                'border': '#e0e0e0',         # 更柔和的边框颜色
                'border_light': '#f0f0f0',   # 浅边框
                'success': '#2e7d32',        # 深绿色
                'success_light': '#e8f5e8',  # 浅绿色背景
                'error': '#c62828',          # 深红色
                'error_light': '#ffebee',    # 浅红色背景
                'warning': '#f57c00',        # 橙色
                'warning_light': '#fff3e0',  # 浅橙色背景
                'combo_bg': '#ffffff',       # 下拉框背景
                'combo_text': '#1a1a1a',     # 下拉框文字
                'list_bg': '#ffffff',        # 列表背景
                'list_text': '#1a1a1a',      # 列表文字
                'list_selected': '#1976d2',  # 列表选中颜色
                'radio_text': '#1a1a1a',     # 单选按钮文字颜色
                'radio_indicator': '#1976d2', # 单选按钮指示器颜色
                'shadow': 'rgba(0,0,0,0.1)', # 阴影颜色
            },
            Theme.DARK: {
                'background': '#121212',      # 深色背景
                'background_secondary': '#1e1e1e', # 卡片背景
                'text': '#ffffff',            # 纯白文字
                'text_secondary': '#b0b0b0',  # 次要文字
                'button': '#2d2d2d',          # 深灰按钮
                'button_hover': '#3d3d3d',    # 悬停时的浅灰
                'button_active': '#4d4d4d',   # 激活状态的按钮
                'accent': '#90caf9',          # 浅蓝色主调
                'accent_light': '#0d47a1',    # 深蓝色
                'secondary': '#b0b0b0',       # 次要文字
                'border': '#404040',          # 边框颜色
                'border_light': '#2d2d2d',    # 浅边框
                'success': '#81c784',         # 成功绿色
                'success_light': '#1b5e20',   # 深绿色背景
                'error': '#e57373',           # 错误红色
                'error_light': '#b71c1c',      # 深红色背景
                'warning': '#ffb74d',         # 警告橙色
                'warning_light': '#e65100',    # 深橙色背景
                'combo_bg': '#2d2d2d',        # 下拉框背景
                'combo_text': '#ffffff',      # 下拉框文字
                'list_bg': '#2d2d2d',         # 列表背景
                'list_text': '#ffffff',       # 列表文字
                'list_selected': '#90caf9',   # 列表选中颜色
                'radio_text': '#ffffff',     # 单选按钮文字颜色
                'radio_indicator': '#90caf9', # 单选按钮指示器颜色
                'shadow': 'rgba(255,255,255,0.1)', # 阴影颜色
            },
            Theme.BLUE: {
                'background': '#f0f8ff',      # 更柔和的浅蓝背景
                'background_secondary': '#ffffff', # 卡片背景
                'text': '#0d47a1',            # 深蓝文字
                'text_secondary': '#1565c0',   # 次要文字
                'button': '#e1f5fe',          # 浅蓝按钮
                'button_hover': '#b3e5fc',    # 悬停时的蓝色
                'button_active': '#81d4fa',   # 激活状态的按钮
                'accent': '#1976d2',          # 蓝色主调
                'accent_light': '#e3f2fd',    # 浅蓝色
                'secondary': '#1565c0',       # 次要文字
                'border': '#90caf9',          # 边框颜色
                'border_light': '#e3f2fd',    # 浅边框
                'success': '#2e7d32',         # 深绿色
                'success_light': '#e8f5e8',   # 浅绿色背景
                'error': '#c62828',           # 深红色
                'error_light': '#ffebee',     # 浅红色背景
                'warning': '#f57c00',         # 橙色
                'warning_light': '#fff3e0',   # 浅橙色背景
                'combo_bg': '#ffffff',        # 下拉框背景
                'combo_text': '#0d47a1',      # 下拉框文字
                'list_bg': '#ffffff',         # 列表背景
                'list_text': '#0d47a1',       # 列表文字
                'list_selected': '#1976d2',  # 列表选中颜色
                'radio_text': '#0d47a1',     # 单选按钮文字颜色
                'radio_indicator': '#1976d2', # 单选按钮指示器颜色
                'shadow': 'rgba(13,71,161,0.1)', # 阴影颜色
            },
            Theme.GREEN: {
                'background': '#f1f8e9',      # 浅绿背景
                'background_secondary': '#ffffff', # 卡片背景
                'text': '#1b5e20',            # 深绿文字
                'text_secondary': '#2e7d32',   # 次要文字
                'button': '#dcedc8',          # 浅绿按钮
                'button_hover': '#c5e1a5',    # 悬停时的绿色
                'button_active': '#aed581',   # 激活状态的按钮
                'accent': '#388e3c',          # 绿色主调
                'accent_light': '#e8f5e9',    # 浅绿色
                'secondary': '#2e7d32',       # 次要文字
                'border': '#81c784',          # 边框颜色
                'border_light': '#c8e6c9',    # 浅边框
                'success': '#2e7d32',         # 深绿色
                'success_light': '#e8f5e9',   # 浅绿色背景
                'error': '#c62828',           # 深红色
                'error_light': '#ffebee',     # 浅红色背景
                'warning': '#f57c00',         # 橙色
                'warning_light': '#fff3e0',   # 浅橙色背景
                'combo_bg': '#ffffff',        # 下拉框背景
                'combo_text': '#1b5e20',      # 下拉框文字
                'list_bg': '#ffffff',         # 列表背景
                'list_text': '#1b5e20',       # 列表文字
                'list_selected': '#388e3c',  # 列表选中颜色
                'radio_text': '#1b5e20',     # 单选按钮文字颜色
                'radio_indicator': '#388e3c', # 单选按钮指示器颜色
                'shadow': 'rgba(27,94,32,0.1)', # 阴影颜色
            }
        }
    
    def get_current_theme(self):
        return self._current_theme
    
    def set_theme(self, theme: Theme):
        self._current_theme = theme
        self.theme_changed.emit(theme.value)
    
    def get_style(self, element: str):
        return self._themes[self._current_theme].get(element, '')
