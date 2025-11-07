import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QTextEdit, QMessageBox, QInputDialog,
    QDialog, QStackedWidget, QFileDialog
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from data_manager import DatabaseManager
from ui_components import AnimatedButton, UICreator
from study_modes import StudyModes

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.db = DatabaseManager()
        self.current_vocabulary = None
        self.current_vocab_id = None
        self.study_mode = 'recognize'
        self.statusBar().showMessage('就绪')
        self.init_ui()
        
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
        
        # 初始化各个页面
        UICreator.create_main_page(self)
        UICreator.create_vocabulary_page(self)
        UICreator.create_add_word_page(self)
        UICreator.create_study_page(self)
        UICreator.create_settings_page(self)
        
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
        if page in [self.main_page, self.vocabulary_page, self.add_word_page, self.study_page, self.settings_page]:
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
            
        word, meaning = current_item.text().split(": ", 1)
        
        dialog = QDialog(self)
        dialog.setWindowTitle('修改单词')
        dialog.setMinimumWidth(400)
        layout = QVBoxLayout(dialog)
        layout.setSpacing(10)
        
        # 添加单词输入框
        word_label = QLabel('单词：')
        word_input = QLineEdit(word)
        layout.addWidget(word_label)
        layout.addWidget(word_input)
        
        # 添加释义输入框
        meaning_label = QLabel('释义：')
        meaning_input = QTextEdit(meaning)
        meaning_input.setMaximumHeight(100)
        layout.addWidget(meaning_label)
        layout.addWidget(meaning_input)
        
        # 添加按钮
        button_layout = QHBoxLayout()
        ok_button = AnimatedButton('确定')
        cancel_button = AnimatedButton('取消')
        button_layout.addWidget(ok_button)
        button_layout.addWidget(cancel_button)
        layout.addLayout(button_layout)
        
        # 连接按钮信号
        ok_button.clicked.connect(dialog.accept)
        cancel_button.clicked.connect(dialog.reject)
        
        # 显示对话框
        if dialog.exec() == QDialog.DialogCode.Accepted:
            new_word = word_input.text().strip()
            new_meaning = meaning_input.toPlainText().strip()
            
            if new_word and new_meaning:
                # 更新数据库
                self.db.update_word(word, new_word, new_meaning, self.current_vocabulary)
                # 更新显示
                self.db.update_words_list(self.words_list, self.current_vocabulary)
                self.statusBar().showMessage('单词修改成功！', 2000)
            else:
                self.statusBar().showMessage('请填写完整信息！', 2000)

    def delete_word(self):
        current_item = self.words_list.currentItem()
        if current_item and self.current_vocabulary:
            word = current_item.text().split(":")[0]
            reply = QMessageBox.question(self, '确认', f'确定要删除单词"{word}"吗？',
                                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if reply == QMessageBox.StandardButton.Yes:
                self.db.delete_word(word)
                self.db.update_words_list(self.words_list, self.current_vocabulary)
                
    def add_vocabulary(self):
        name, ok = QInputDialog.getText(self, '新建单词本', '请输入单词本名称：')
        if ok and name:
            success, message = self.db.add_vocabulary(name)
            if success:
                self.db.update_vocab_list(self.vocab_list)
                self.db.update_vocab_combo(self.vocab_combo)
                self.db.update_study_vocab_combo(self.study_vocab_combo)
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
                self.db.update_study_vocab_combo(self.study_vocab_combo)
                
    def add_word(self):
        word = self.word_input.text().strip()
        meaning = self.meaning_input.toPlainText().strip()
        vocab_id = self.vocab_combo.currentData()
        
        if not word or not meaning:
            QMessageBox.warning(self, '提示', '请填写完整的单词和释义！')
            return
        
        success, message = self.db.add_word(word, meaning, vocab_id)
        if success:
            self.word_input.clear()
            self.meaning_input.clear()
            self.statusBar().showMessage(message, 2000)
        else:
            self.statusBar().showMessage(message, 2000)

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
