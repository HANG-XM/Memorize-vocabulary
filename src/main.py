import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QTextEdit, QMessageBox, QInputDialog,
    QDialog, QStackedWidget, QFileDialog, QComboBox, QListWidget, QRadioButton
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from data_manager import DatabaseManager
from ui_components import AnimatedButton, UICreator
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
        theme_colors = self.theme_manager._themes[Theme(theme_name)]
        
        # 设置主窗口样式
        self.setStyleSheet(f"""
            QMainWindow {{
                background-color: {theme_colors['background']};
                color: {theme_colors['text']};
            }}
            QLabel {{
                color: {theme_colors['text']};
                font-size: 14px;
            }}
            QLineEdit, QTextEdit {{
                background-color: {theme_colors['button']};
                color: {theme_colors['text']};
                border: 1px solid {theme_colors['border']};
                padding: 5px;
                border-radius: 4px;
            }}
            QLineEdit:focus, QTextEdit:focus {{
                border: 2px solid {theme_colors['accent']};
            }}
            QListWidget {{
                background-color: {theme_colors['list_bg']};
                color: {theme_colors['list_text']};
                border: 1px solid {theme_colors['border']};
                border-radius: 4px;
                padding: 5px;
            }}
            QListWidget::item {{
                padding: 5px;
                border-bottom: 1px solid {theme_colors['border']};
            }}
            QListWidget::item:selected {{
                background-color: {theme_colors['list_selected']};
                color: {theme_colors['text']};
            }}
            QComboBox {{
                background-color: {theme_colors['combo_bg']};
                color: {theme_colors['combo_text']};
                border: 1px solid {theme_colors['border']};
                padding: 5px;
                border-radius: 4px;
            }}
            QComboBox::drop-down {{
                border: none;
                width: 20px;
            }}
            QComboBox::down-arrow {{
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid {theme_colors['combo_text']};
            }}
            QComboBox QAbstractItemView {{
                background-color: {theme_colors['combo_bg']};
                color: {theme_colors['combo_text']};
                selection-background-color: {theme_colors['list_selected']};
            }}
            QRadioButton {{
                color: {theme_colors['radio_text']};
                spacing: 8px;
            }}
            QRadioButton::indicator {{
                width: 16px;
                height: 16px;
                border: 2px solid {theme_colors['border']};
                border-radius: 8px;
                background-color: {theme_colors['button']};
            }}
            QRadioButton::indicator:checked {{
                background-color: {theme_colors['radio_indicator']};
                border-color: {theme_colors['radio_indicator']};
            }}
            QRadioButton::indicator:hover {{
                border-color: {theme_colors['accent']};
            }}
            QCheckBox {{
                color: {theme_colors['text']};
                spacing: 8px;
                font-weight: 500;
                background-color: transparent;
            }}
            QCheckBox::indicator {{
                width: 16px;
                height: 16px;
                border: 2px solid {theme_colors['border']};
                border-radius: 4px;
                background-color: {theme_colors['button']};
            }}
            QCheckBox::indicator:checked {{
                background-color: {theme_colors['accent']};
                border-color: {theme_colors['accent']};
            }}
            QCheckBox::indicator:hover {{
                border-color: {theme_colors['accent']};
            }}
            QCheckBox:disabled {{
                color: {theme_colors['text_secondary']};
            }}
            QCheckBox::indicator:disabled {{
                background-color: {theme_colors['border_light']};
                border-color: {theme_colors['border']};
            }}
            QProgressBar {{
                border: 1px solid {theme_colors['border']};
                border-radius: 4px;
                text-align: center;
                color: {theme_colors['text']};
            }}
            QProgressBar::chunk {{
                background-color: {theme_colors['accent']};
                border-radius: 3px;
            }}
        """)
        
        # 更新所有子窗口部件
        self.update_children_theme(self.centralWidget(), theme_colors)

    def update_children_theme(self, widget, theme_colors):
        """优化主题更新性能 - 预编译样式表"""
        # 预编译样式表，避免重复字符串格式化
        button_style = f"""
            QPushButton {{
                background-color: {theme_colors['button']};
                color: {theme_colors['text']};
                border: 1px solid {theme_colors['border']};
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: 500;
            }}
            QPushButton:hover {{
                background-color: {theme_colors['button_hover']};
                border: 1px solid {theme_colors['accent']};
            }}
            QPushButton:pressed {{
                background-color: {theme_colors['accent']};
                color: {theme_colors['text']};
            }}
            QPushButton:disabled {{
                background-color: {theme_colors['border']};
                color: {theme_colors['secondary']};
            }}
        """
        
        # 使用广度优先搜索，避免递归深度过大
        widgets_to_process = [widget]
        while widgets_to_process:
            current_widget = widgets_to_process.pop(0)
            
            for child in current_widget.children():
                if isinstance(child, AnimatedButton):
                    child.setStyleSheet(button_style)
                widgets_to_process.append(child)
            
    def update_stats(self):
        self.stats_list.clear()
        stats = self.db.get_daily_stats(self.current_vocab_id)
        for date, total, correct, accuracy in stats:
            self.stats_list.addItem(f"{date}: 学习 {total} 个单词，正确率 {accuracy}%")
        
    def update_wrong_words(self):
        self.wrong_words_list.clear()
        wrong_words = self.db.get_wrong_words()
        for word, meaning, count in wrong_words:
            self.wrong_words_list.addItem(f"{word}: {meaning} (错误次数: {count})")

    def clear_wrong_word(self):
        current_item = self.wrong_words_list.currentItem()
        if current_item:
            word = current_item.text().split(":")[0]
            self.db.remove_wrong_word(word)
            self.update_wrong_words()
            self.statusBar().showMessage('错题已清除', 2000)

    def clear_all_wrong_words(self):
        reply = QMessageBox.question(self, '确认', '确定要清空所有错题吗？',
                                   QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            self.db.cursor.execute('DELETE FROM wrong_words')
            self.db.conn.commit()
            self.update_wrong_words()
            self.statusBar().showMessage('错题本已清空', 2000)
        
    def init_ui(self):
        self.setWindowTitle('智能背单词')
        self.setGeometry(100, 100, 800, 600)
        
        # 创建主窗口部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 创建堆叠窗口部件
        self.stack = QStackedWidget()
        
        # 创建各个页面
        self.main_page = QWidget()
        self.vocabulary_page = QWidget()
        self.add_word_page = QWidget()
        self.study_page = QWidget()
        self.settings_page = QWidget()
        
        # 将所有页面添加到堆叠窗口
        self.stack.addWidget(self.main_page)
        self.stack.addWidget(self.vocabulary_page)
        self.stack.addWidget(self.add_word_page)
        self.stack.addWidget(self.study_page)
        self.stack.addWidget(self.settings_page)
        self.stack.addWidget(self.stats_page)
        self.stack.addWidget(self.wrong_words_page)
        
        # 初始化各个页面
        UICreator.create_main_page(self)
        UICreator.create_vocabulary_page(self)
        UICreator.create_add_word_page(self)
        UICreator.create_study_page(self)
        UICreator.create_settings_page(self)
        UICreator.create_stats_page(self)
        UICreator.create_wrong_words_page(self)
        
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
        if page in [self.main_page, self.vocabulary_page, self.add_word_page, 
                    self.study_page, self.settings_page, self.stats_page, self.wrong_words_page]:
            if page == self.stats_page:
                self.update_stats()
            elif page == self.wrong_words_page:
                self.update_wrong_words()
            self.stack.setCurrentWidget(page)
        
    def on_vocab_selected(self, item):
        vocab_id = int(item.text().split('(ID: ')[1].rstrip(')'))
        self.current_vocabulary = vocab_id
        self.words_title.setText(f'单词本: {item.text().split(" (ID:")[0]}')
        self.db.update_words_list(self.words_list, self.current_vocabulary)
        
    def edit_word(self):
        current_item = self.words_list.currentItem()
        if not current_item or not self.current_vocabulary:
            QMessageBox.warning(self, '提示', '请先选择要修改的单词！')
            return
            
        # 从带序号的文本中提取原始单词
        text = current_item.text().split(": ", 1)[0]
        word = text.split(". ", 1)[1] if ". " in text else text
        
        # 获取该单词的所有词性和释义
        pos_meanings = self.db.get_word_pos_meanings(word, self.current_vocabulary)
        
        # 获取单词类型
        word_type = 'word'  # 默认类型
        if pos_meanings:
            # 从数据库中获取单词类型
            self.db.cursor.execute('SELECT DISTINCT type FROM word_pos_meanings WHERE word = ? AND vocabulary_id = ?', 
                                (word, self.current_vocabulary))
            result = self.db.cursor.fetchone()
            if result:
                word_type = result[0]
        
        dialog = QDialog(self)
        dialog.setWindowTitle('修改单词')
        dialog.setMinimumWidth(500)
        layout = QVBoxLayout(dialog)
        layout.setSpacing(10)
        
        # 添加单词输入框
        word_label = QLabel('单词：')
        word_input = QLineEdit(word)
        layout.addWidget(word_label)
        layout.addWidget(word_input)
        
        # 添加类型选择
        type_label = QLabel('类型：')
        type_combo = QComboBox()
        type_combo.addItems(['单词', '短语'])
        type_combo.setCurrentText('单词' if word_type == 'word' else '短语')
        type_layout = QHBoxLayout()
        type_layout.addWidget(type_label)
        type_layout.addWidget(type_combo)
        layout.addLayout(type_layout)
        
        # 创建词性释义输入区域
        pos_meaning_container = QWidget()
        pos_meaning_layout = QVBoxLayout(pos_meaning_container)
        pos_meaning_layout.setSpacing(10)
        
        pos_title = QLabel('词性与释义：')
        pos_title.setFont(QFont('Arial', 12, QFont.Weight.Bold))
        pos_meaning_layout.addWidget(pos_title)
        
        # 为每个词性释义创建输入框
        for pos, meaning in pos_meanings:
            pair_widget = QWidget()
            pair_layout = QHBoxLayout(pair_widget)
            pair_layout.setSpacing(10)
            
            # 词性选择下拉框
            pos_combo = QComboBox()
            pos_combo.addItems(['n.', 'adj.', 'adv.', 'v.', 'prep.', 'conj.', 'pron.', 'art.', 'num.', 'interj.'])
            pos_combo.setCurrentText(pos)
            pos_combo.setMinimumWidth(80)
            pair_layout.addWidget(QLabel('词性：'))
            pair_layout.addWidget(pos_combo)
            
            # 释义输入框
            meaning_input = QTextEdit()
            meaning_input.setPlaceholderText('输入该词性下的释义')
            meaning_input.setMaximumHeight(60)
            meaning_input.setMinimumWidth(200)
            meaning_input.setPlainText(meaning)
            pair_layout.addWidget(QLabel('释义：'))
            pair_layout.addWidget(meaning_input)
            
            # 删除按钮
            delete_button = AnimatedButton('删除')
            delete_button.setup_theme_style(self.theme_manager._themes[self.theme_manager.get_current_theme()])
            delete_button.setMaximumWidth(60)
            delete_button.clicked.connect(lambda: pos_meaning_layout.removeWidget(pair_widget))
            pair_layout.addWidget(delete_button)
            
            pos_meaning_layout.addWidget(pair_widget)
        
        # 添加新词性的按钮
        add_pos_button = AnimatedButton('添加词性')
        add_pos_button.setup_theme_style(self.theme_manager._themes[self.theme_manager.get_current_theme()])
        add_pos_button.clicked.connect(lambda: UICreator.add_pos_meaning_pair(dialog))
        pos_meaning_layout.addWidget(add_pos_button)
        
        # 创建滚动区域
        from PyQt6.QtWidgets import QScrollArea
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setMinimumHeight(200)
        scroll_area.setWidget(pos_meaning_container)
        layout.addWidget(scroll_area)
        
        # 添加确定和取消按钮
        confirm_layout = QHBoxLayout()
        ok_button = AnimatedButton('确定')
        cancel_button = AnimatedButton('取消')
        confirm_layout.addWidget(ok_button)
        confirm_layout.addWidget(cancel_button)
        layout.addLayout(confirm_layout)
        
        # 连接按钮信号
        def handle_ok():
            new_word = word_input.text().strip()
            
            # 获取单词类型
            word_type = 'word' if type_combo.currentText() == '单词' else 'phrase'
            
            # 获取所有词性释义对
            new_pos_meanings = []
            for i in range(pos_meaning_layout.count()):
                pair_widget = pos_meaning_layout.itemAt(i).widget()
                if pair_widget and isinstance(pair_widget, QWidget):
                    pos_combo = pair_widget.findChild(QComboBox)
                    meaning_input = pair_widget.findChild(QTextEdit)
                    if pos_combo and meaning_input:
                        pos = pos_combo.currentText()
                        meaning = meaning_input.toPlainText().strip()
                        if meaning:  # 只添加有释义的词性
                            new_pos_meanings.append((pos, meaning))
            
            if new_word and new_pos_meanings:
                # 先删除原有的词性释义
                self.db.delete_word(word, self.current_vocabulary)
                # 添加新的词性释义（包含类型信息）
                success, message = self.db.add_word_with_pos_meanings_and_type(new_word, new_pos_meanings, word_type, self.current_vocabulary)
                
                if success:
                    self.db.update_words_list(self.words_list, self.current_vocabulary)
                    self.statusBar().showMessage('单词修改成功！', 2000)
                    dialog.accept()
                else:
                    self.statusBar().showMessage(message, 2000)
            else:
                self.statusBar().showMessage('请填写完整信息！', 2000)
        
        ok_button.clicked.connect(handle_ok)
        cancel_button.clicked.connect(dialog.reject)
        
        # 显示对话框
        dialog.exec()
    def search_word(self):
        search_text = self.search_input.text().strip().lower()
        if not search_text:
            self.db.update_words_list(self.words_list, self.current_vocabulary)
            return
            
        if not self.current_vocabulary:
            QMessageBox.warning(self, '提示', '请先选择单词本！')
            return
            
        words = self.db.search_words(self.current_vocabulary, search_text)
        self.words_list.clear()
        for word, meaning in words:
            self.words_list.addItem(f"{word}: {meaning}")
    def delete_word(self):
        current_item = self.words_list.currentItem()
        if current_item and self.current_vocabulary:
            # 从带序号的文本中提取原始单词
            text = current_item.text().split(": ", 1)[0]
            word = text.split(". ", 1)[1] if ". " in text else text
            self.db.delete_word(word, self.current_vocabulary)
            self.db.update_words_list(self.words_list, self.current_vocabulary)
                
    def add_vocabulary(self):
        name, ok = QInputDialog.getText(self, '新建单词本', '请输入单词本名称：')
        if ok and name:
            success, message = self.db.add_vocabulary(name)
            if success:
                self.db.update_vocab_list(self.vocab_list)
                self.db.update_vocab_combo(self.vocab_combo)
                self.db.update_vocab_combo(self.settings_vocab_combo)
                QMessageBox.information(self, '成功', message)
            else:
                QMessageBox.warning(self, '错误', message)
                
    def export_vocabulary(self):
        if not self.current_vocabulary:
            QMessageBox.warning(self, '提示', '请先选择要导出的单词本！')
            return
        
        file_path, _ = QFileDialog.getSaveFileName(
            self, '导出单词本', 
            f'vocabulary_{self.current_vocabulary}.csv',
            'CSV文件 (*.csv)'
        )
        
        if file_path:
            success, message = self.db.export_vocabulary(self.current_vocabulary, file_path)
            if success:
                QMessageBox.information(self, '成功', message)
            else:
                QMessageBox.warning(self, '错误', message)
                
    def delete_vocabulary(self):
        current_item = self.vocab_list.currentItem()
        if current_item:
            vocab_id = int(current_item.text().split('(ID: ')[1].rstrip(')'))
            reply = QMessageBox.question(self, '确认', '确定要删除这个单词本吗？这将删除其中的所有单词！',
                                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if reply == QMessageBox.StandardButton.Yes:
                self.db.delete_vocabulary(vocab_id)
                self.db.update_vocab_list(self.vocab_list)
                self.db.update_vocab_combo(self.vocab_combo)
                self.db.update_vocab_combo(self.settings_vocab_combo)
                
    def add_word(self):
        word = self.word_input.text().strip()
        if not word:
            QMessageBox.warning(self, '提示', '请输入单词！')
            return
        
        # 获取单词类型
        word_type = 'word' if self.word_type_combo.currentText() == '单词' else 'phrase'
        
        # 获取所有词性释义对
        pos_meanings = []
        for i in range(self.pos_meaning_layout.count()):
            pair_widget = self.pos_meaning_layout.itemAt(i).widget()
            if pair_widget:
                pos_combo = pair_widget.findChild(QComboBox)
                meaning_input = pair_widget.findChild(QTextEdit)
                if pos_combo and meaning_input:
                    pos = pos_combo.currentText()
                    meaning = meaning_input.toPlainText().strip()
                    if meaning:  # 只添加有释义的词性
                        pos_meanings.append((pos, meaning))
        
        if not pos_meanings:
            QMessageBox.warning(self, '提示', '请至少添加一个词性和释义！')
            return
        
        vocab_id = self.vocab_combo.currentData()
        success, message = self.db.add_word_with_pos_meanings_and_type(word, pos_meanings, word_type, vocab_id)
        
        if success:
            self.word_input.clear()
            # 清除所有词性释义对
            while self.pos_meaning_layout.count():
                item = self.pos_meaning_layout.takeAt(0)
                if item.widget():
                    item.widget().deleteLater()
            # 添加一个默认的空词性释义对
            UICreator.add_pos_meaning_pair(self)
            self.statusBar().showMessage(message, 2000)
            self.db.update_words_list(self.words_list, vocab_id)
        else:
            self.statusBar().showMessage(message, 2000)
    def update_stats_display(self):
        self.stats_list.clear()
        stats_type = self.stats_type_combo.currentText()
        
        if stats_type == '每日统计':
            stats = self.db.get_daily_stats(self.current_vocab_id)
            for date, total, correct, accuracy in stats:
                self.stats_list.addItem(f"{date}: 学习 {total} 个单词，正确率 {accuracy}%")
        elif stats_type == '每周统计':
            stats = self.db.get_weekly_stats(self.current_vocab_id)
            for week, total, correct, accuracy in stats:
                self.stats_list.addItem(f"第{week}周: 学习 {total} 个单词，正确率 {accuracy}%")
        elif stats_type == '详细统计':
            stats = self.db.get_detailed_stats(self.current_vocab_id)
            for date, mode, total, correct, accuracy in stats:
                self.stats_list.addItem(f"{date} [{mode}]: 学习 {total} 个单词，正确率 {accuracy}%")
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
