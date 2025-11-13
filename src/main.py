import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout
from data_manager import DatabaseManager
from ui_components import UICreator
from ui_controller import UIController
from study_modes import StudyModes
from theme_manager import ThemeManager, Theme

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.theme_manager = ThemeManager()
        self.theme_manager.theme_changed.connect(self.apply_theme)
        self.db = DatabaseManager()
        self.current_vocabulary = None
        self.current_vocab_id = None
        self.study_mode = 'recognize'
        self.study_type = 'word'
        self.statusBar().showMessage('就绪')
        
        # 添加统计页面和错题本页面
        self.stats_page = QWidget()
        self.wrong_words_page = QWidget()
        
        self.init_ui()
        
    def apply_theme(self, theme_name):
        UICreator.apply_theme_to_window(self, theme_name)
        
    def init_ui(self):
        self.setWindowTitle('智能背单词')
        self.setGeometry(100, 100, 800, 600)
        
        # 创建主窗口部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 创建堆叠窗口部件
        self.stack = UIController.create_stacked_widget(self)
        
        # 设置主布局
        layout = QVBoxLayout(central_widget)
        layout.addWidget(self.stack)
        
        # 设置初始页面
        self.stack.setCurrentWidget(self.main_page)
        
        # 初始化数据
        self.db.update_vocab_list(self.vocab_list)
        self.db.update_vocab_combo(self.vocab_combo)
        self.db.update_vocab_combo(self.settings_vocab_combo)
        
    def switch_page(self, page):
        UIController.switch_page(self, page)
        
    def on_vocab_selected(self, item):
        UIController.on_vocab_selected(self, item)
        
    def edit_word(self):
        UIController.edit_word(self)
        
    def search_word(self):
        UIController.search_word(self)
        
    def delete_word(self):
        UIController.delete_word(self)
        
    def add_vocabulary(self):
        UIController.add_vocabulary(self)
        
    def export_vocabulary(self):
        UIController.export_vocabulary(self)
        
    def delete_vocabulary(self):
        UIController.delete_vocabulary(self)
        
    def add_word(self):
        UIController.add_word(self)
        
    def update_stats_display(self):
        UIController.update_stats_display(self)
        
    def clear_wrong_word(self):
        UIController.clear_wrong_word(self)
        
    def clear_all_wrong_words(self):
        UIController.clear_all_wrong_words(self)

def main():
    app = QApplication(sys.argv)
    
    # 设置应用样式
    app.setStyle('Fusion')
    
    # 创建并显示主窗口
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())

if __name__ == '__main__':
    main()