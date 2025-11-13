from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QTextEdit, 
    QMessageBox, QInputDialog, QDialog, QStackedWidget, QFileDialog, 
    QComboBox, QListWidget, QRadioButton, QScrollArea
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from ui_components import AnimatedButton, UICreator
from theme_manager import Theme

class UIController:
    """UI控制器，负责处理UI事件和业务逻辑"""
    
    @staticmethod
    def create_stacked_widget(main_window):
        """创建堆叠窗口部件"""
        main_window.stack = QStackedWidget()
        
        # 创建各个页面
        main_window.main_page = QWidget()
        main_window.vocabulary_page = QWidget()
        main_window.add_word_page = QWidget()
        main_window.study_page = QWidget()
        main_window.settings_page = QWidget()
        
        # 将所有页面添加到堆叠窗口
        main_window.stack.addWidget(main_window.main_page)
        main_window.stack.addWidget(main_window.vocabulary_page)
        main_window.stack.addWidget(main_window.add_word_page)
        main_window.stack.addWidget(main_window.study_page)
        main_window.stack.addWidget(main_window.settings_page)
        main_window.stack.addWidget(main_window.stats_page)
        main_window.stack.addWidget(main_window.wrong_words_page)
        
        # 初始化各个页面
        UICreator.create_main_page(main_window)
        UICreator.create_vocabulary_page(main_window)
        UICreator.create_add_word_page(main_window)
        UICreator.create_study_page(main_window)
        UICreator.create_settings_page(main_window)
        UICreator.create_stats_page(main_window)
        UICreator.create_wrong_words_page(main_window)
        
        return main_window.stack
    
    @staticmethod
    def switch_page(main_window, page):
        """切换页面"""
        if page in [main_window.main_page, main_window.vocabulary_page, main_window.add_word_page, 
                    main_window.study_page, main_window.settings_page, main_window.stats_page, main_window.wrong_words_page]:
            if page == main_window.stats_page:
                UIController.update_stats(main_window)
            elif page == main_window.wrong_words_page:
                UIController.update_wrong_words(main_window)
            main_window.stack.setCurrentWidget(page)
    
    @staticmethod
    def on_vocab_selected(main_window, item):
        """单词本选择事件"""
        vocab_id = int(item.text().split('(ID: ')[1].rstrip(')'))
        main_window.current_vocabulary = vocab_id
        main_window.words_title.setText(f'单词本: {item.text().split(" (ID:")[0]}')
        main_window.db.update_words_list(main_window.words_list, main_window.current_vocabulary)
    
    @staticmethod
    def edit_word(main_window):
        """编辑单词"""
        current_item = main_window.words_list.currentItem()
        if not current_item or not main_window.current_vocabulary:
            QMessageBox.warning(main_window, '提示', '请先选择要修改的单词！')
            return
            
        # 从带序号的文本中提取原始单词
        text = current_item.text().split(": ", 1)[0]
        word = text.split(". ", 1)[1] if ". " in text else text
        
        # 获取该单词的所有词性和释义
        pos_meanings = main_window.db.get_word_pos_meanings(word, main_window.current_vocabulary)
        
        # 获取单词类型
        word_type = 'word'  # 默认类型
        if pos_meanings:
            # 从数据库中获取单词类型
            main_window.db.cursor.execute('SELECT DISTINCT type FROM word_pos_meanings WHERE word = ? AND vocabulary_id = ?', 
                                (word, main_window.current_vocabulary))
            result = main_window.db.cursor.fetchone()
            if result:
                word_type = result[0]
        
        dialog = QDialog(main_window)
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
            delete_button.setup_theme_style(main_window.theme_manager._themes[main_window.theme_manager.get_current_theme()])
            delete_button.setMaximumWidth(60)
            delete_button.clicked.connect(lambda: pos_meaning_layout.removeWidget(pair_widget))
            pair_layout.addWidget(delete_button)
            
            pos_meaning_layout.addWidget(pair_widget)
        
        # 添加新词性的按钮
        add_pos_button = AnimatedButton('添加词性')
        add_pos_button.setup_theme_style(main_window.theme_manager._themes[main_window.theme_manager.get_current_theme()])
        add_pos_button.clicked.connect(lambda: UICreator.add_pos_meaning_pair(dialog))
        pos_meaning_layout.addWidget(add_pos_button)
        
        # 创建滚动区域
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
                main_window.db.delete_word(word, main_window.current_vocabulary)
                # 添加新的词性释义（包含类型信息）
                success, message = main_window.db.add_word_with_pos_meanings_and_type(new_word, new_pos_meanings, word_type, main_window.current_vocabulary)
                
                if success:
                    main_window.db.update_words_list(main_window.words_list, main_window.current_vocabulary)
                    main_window.statusBar().showMessage('单词修改成功！', 2000)
                    dialog.accept()
                else:
                    main_window.statusBar().showMessage(message, 2000)
            else:
                main_window.statusBar().showMessage('请填写完整信息！', 2000)
        
        ok_button.clicked.connect(handle_ok)
        cancel_button.clicked.connect(dialog.reject)
        
        # 显示对话框
        dialog.exec()
    
    @staticmethod
    def search_word(main_window):
        """搜索单词"""
        search_text = main_window.search_input.text().strip().lower()
        if not search_text:
            main_window.db.update_words_list(main_window.words_list, main_window.current_vocabulary)
            return
            
        if not main_window.current_vocabulary:
            QMessageBox.warning(main_window, '提示', '请先选择单词本！')
            return
            
        words = main_window.db.search_words(main_window.current_vocabulary, search_text)
        main_window.words_list.clear()
        for word, meaning in words:
            main_window.words_list.addItem(f"{word}: {meaning}")
    
    @staticmethod
    def delete_word(main_window):
        """删除单词"""
        current_item = main_window.words_list.currentItem()
        if current_item and main_window.current_vocabulary:
            # 从带序号的文本中提取原始单词
            text = current_item.text().split(": ", 1)[0]
            word = text.split(". ", 1)[1] if ". " in text else text
            main_window.db.delete_word(word, main_window.current_vocabulary)
            main_window.db.update_words_list(main_window.words_list, main_window.current_vocabulary)
    
    @staticmethod
    def add_vocabulary(main_window):
        """添加单词本"""
        name, ok = QInputDialog.getText(main_window, '新建单词本', '请输入单词本名称：')
        if ok and name:
            success, message = main_window.db.add_vocabulary(name)
            if success:
                main_window.db.update_vocab_list(main_window.vocab_list)
                main_window.db.update_vocab_combo(main_window.vocab_combo)
                main_window.db.update_vocab_combo(main_window.settings_vocab_combo)
                QMessageBox.information(main_window, '成功', message)
            else:
                QMessageBox.warning(main_window, '错误', message)
    
    @staticmethod
    def export_vocabulary(main_window):
        """导出单词本"""
        if not main_window.current_vocabulary:
            QMessageBox.warning(main_window, '提示', '请先选择要导出的单词本！')
            return
        
        file_path, _ = QFileDialog.getSaveFileName(
            main_window, '导出单词本', 
            f'vocabulary_{main_window.current_vocabulary}.csv',
            'CSV文件 (*.csv)'
        )
        
        if file_path:
            success, message = main_window.db.export_vocabulary(main_window.current_vocabulary, file_path)
            if success:
                QMessageBox.information(main_window, '成功', message)
            else:
                QMessageBox.warning(main_window, '错误', message)
    
    @staticmethod
    def delete_vocabulary(main_window):
        """删除单词本"""
        current_item = main_window.vocab_list.currentItem()
        if current_item:
            vocab_id = int(current_item.text().split('(ID: ')[1].rstrip(')'))
            reply = QMessageBox.question(main_window, '确认', '确定要删除这个单词本吗？这将删除其中的所有单词！',
                                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if reply == QMessageBox.StandardButton.Yes:
                main_window.db.delete_vocabulary(vocab_id)
                main_window.db.update_vocab_list(main_window.vocab_list)
                main_window.db.update_vocab_combo(main_window.vocab_combo)
                main_window.db.update_vocab_combo(main_window.settings_vocab_combo)
    
    @staticmethod
    def add_word(main_window):
        """添加单词"""
        word = main_window.word_input.text().strip()
        if not word:
            QMessageBox.warning(main_window, '提示', '请输入单词！')
            return
        
        # 获取单词类型
        word_type = 'word' if main_window.word_type_combo.currentText() == '单词' else 'phrase'
        
        # 获取所有词性释义对
        pos_meanings = []
        for i in range(main_window.pos_meaning_layout.count()):
            pair_widget = main_window.pos_meaning_layout.itemAt(i).widget()
            if pair_widget:
                pos_combo = pair_widget.findChild(QComboBox)
                meaning_input = pair_widget.findChild(QTextEdit)
                if pos_combo and meaning_input:
                    pos = pos_combo.currentText()
                    meaning = meaning_input.toPlainText().strip()
                    if meaning:  # 只添加有释义的词性
                        pos_meanings.append((pos, meaning))
        
        if not pos_meanings:
            QMessageBox.warning(main_window, '提示', '请至少添加一个词性和释义！')
            return
        
        vocab_id = main_window.vocab_combo.currentData()
        success, message = main_window.db.add_word_with_pos_meanings_and_type(word, pos_meanings, word_type, vocab_id)
        
        if success:
            main_window.word_input.clear()
            # 清除所有词性释义对
            while main_window.pos_meaning_layout.count():
                item = main_window.pos_meaning_layout.takeAt(0)
                if item.widget():
                    item.widget().deleteLater()
            # 添加一个默认的空词性释义对
            UICreator.add_pos_meaning_pair(main_window)
            main_window.statusBar().showMessage(message, 2000)
            main_window.db.update_words_list(main_window.words_list, vocab_id)
        else:
            main_window.statusBar().showMessage(message, 2000)
    
    @staticmethod
    def update_stats(main_window):
        """更新统计信息"""
        main_window.stats_list.clear()
        stats = main_window.db.get_daily_stats(main_window.current_vocab_id)
        for date, total, correct, accuracy in stats:
            main_window.stats_list.addItem(f"{date}: 学习 {total} 个单词，正确率 {accuracy}%")
    
    @staticmethod
    def update_wrong_words(main_window):
        """更新错题本"""
        main_window.wrong_words_list.clear()
        wrong_words = main_window.db.get_wrong_words()
        for word, meaning, count in wrong_words:
            main_window.wrong_words_list.addItem(f"{word}: {meaning} (错误次数: {count})")
    
    @staticmethod
    def update_stats_display(main_window):
        """更新统计显示"""
        main_window.stats_list.clear()
        stats_type = main_window.stats_type_combo.currentText()
        
        if stats_type == '每日统计':
            stats = main_window.db.get_daily_stats(main_window.current_vocab_id)
            for date, total, correct, accuracy in stats:
                main_window.stats_list.addItem(f"{date}: 学习 {total} 个单词，正确率 {accuracy}%")
        elif stats_type == '每周统计':
            stats = main_window.db.get_weekly_stats(main_window.current_vocab_id)
            for week, total, correct, accuracy in stats:
                main_window.stats_list.addItem(f"第{week}周: 学习 {total} 个单词，正确率 {accuracy}%")
        elif stats_type == '详细统计':
            stats = main_window.db.get_detailed_stats(main_window.current_vocab_id)
            for date, mode, total, correct, accuracy in stats:
                main_window.stats_list.addItem(f"{date} [{mode}]: 学习 {total} 个单词，正确率 {accuracy}%")
    
    @staticmethod
    def clear_wrong_word(main_window):
        """清除错题"""
        current_item = main_window.wrong_words_list.currentItem()
        if current_item:
            word = current_item.text().split(":")[0]
            main_window.db.remove_wrong_word(word)
            UIController.update_wrong_words(main_window)
            main_window.statusBar().showMessage('错题已清除', 2000)
    
    @staticmethod
    def clear_all_wrong_words(main_window):
        """清空错题本"""
        reply = QMessageBox.question(main_window, '确认', '确定要清空所有错题吗？',
                                   QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            main_window.db.cursor.execute('DELETE FROM wrong_words')
            main_window.db.conn.commit()
            UIController.update_wrong_words(main_window)
            main_window.statusBar().showMessage('错题本已清空', 2000)