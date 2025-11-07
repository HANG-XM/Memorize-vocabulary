from PyQt6.QtWidgets import QPushButton, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QMessageBox, QProgressBar
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
import random
from typing import Optional

class StudyModes:
    @staticmethod
    def create_recognize_mode(study_layout, words):
        from ui_components import AnimatedButton
        word, meaning = random.choice(words)
        
        # 创建进度指示器
        progress_layout = QHBoxLayout()
        progress_label = QLabel("学习进度：")
        progress_bar = QProgressBar()
        progress_bar.setRange(0, len(words))
        progress_bar.setValue(0)
        progress_layout.addWidget(progress_label)
        progress_layout.addWidget(progress_bar)
        study_layout.addLayout(progress_layout)
        
        # 显示单词
        word_label = QLabel(word)
        word_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        word_label.setFont(QFont('Arial', 24))
        study_layout.addWidget(word_label)
        
        # 添加状态标签
        status_label = QLabel()
        status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        status_label.setStyleSheet("color: green; font-size: 16px;")
        study_layout.addWidget(status_label)
        
        # 显示释义按钮
        btn_show = AnimatedButton('显示释义')
        btn_show.clicked.connect(lambda: StudyModes.show_meaning(meaning, status_label))
        study_layout.addWidget(btn_show)
        
        # 创建一个容器来放置按钮
        button_container = QWidget()
        button_layout = QHBoxLayout(button_container)
        
        # 认识/不认识按钮
        btn_know = AnimatedButton('认识')
        btn_unknown = AnimatedButton('不认识')
        button_layout.addWidget(btn_know)
        button_layout.addWidget(btn_unknown)
        
        study_layout.addWidget(button_container)
        
        return btn_know, btn_unknown
        
    @staticmethod
    def show_meaning(meaning: str, status_label: QLabel) -> None:
        status_label.setText(f"释义: {meaning}")
        status_label.setStyleSheet("""
            QLabel {
                color: #2196F3;
                font-size: 16px;
                padding: 10px;
                background-color: #E3F2FD;
                border-radius: 4px;
            }
        """)

    @staticmethod
    def handle_choice(is_correct: bool, word: str, correct_meaning: str, 
                    status_label: Optional[QLabel] = None, 
                    main_window: Optional[object] = None) -> None:
        if is_correct:
            if status_label:
                status_label.setText("✓ 回答正确！")
                status_label.setStyleSheet("color: #4CAF50; font-size: 16px; font-weight: bold;")
        else:
            if status_label:
                status_label.setText(f"✗ 回答错误！\n正确答案是：{correct_meaning}")
                status_label.setStyleSheet("color: #F44336; font-size: 16px;")
        
        # 延迟1.5秒后自动进入下一个单词
        from PyQt6.QtCore import QTimer
        if main_window:
            QTimer.singleShot(1500, lambda: StudyModes.start_study(main_window))

    @staticmethod
    def save_settings(main_window):
        # 保存选中的单词本
        vocab_id = main_window.settings_vocab_combo.currentData()
        if not vocab_id:
            QMessageBox.warning(main_window, '错误', '请选择单词本！')
            return
        
        # 保存选中的学习模式
        if main_window.settings_radio_recognize.isChecked():
            main_window.study_mode = 'recognize'
        elif main_window.settings_radio_choice.isChecked():
            main_window.study_mode = 'choice'
        elif main_window.settings_radio_spell.isChecked():
            main_window.study_mode = 'spell'
        
        main_window.current_vocab_id = vocab_id
        QMessageBox.information(main_window, '成功', '设置已保存！')
        main_window.switch_page(main_window.main_page)       

    @staticmethod
    def create_choice_mode(study_layout, words, main_window=None):
        from ui_components import AnimatedButton
        word, correct_meaning = random.choice(words)
        
        # 显示单词
        word_label = QLabel(word)
        word_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        word_label.setFont(QFont('Arial', 24))
        study_layout.addWidget(word_label)
        
        # 创建选项
        meanings = [correct_meaning]
        while len(meanings) < 4:
            _, meaning = random.choice(words)
            if meaning not in meanings:
                meanings.append(meaning)
        random.shuffle(meanings)
        
        # 创建选项按钮
        buttons = []
        status_label = QLabel()
        status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        study_layout.addWidget(status_label)
        
        for i, meaning in enumerate(meanings):
            btn = AnimatedButton(meaning)
            is_correct = meaning == correct_meaning
            # 使用functools.partial来正确捕获变量值
            from functools import partial
            btn.clicked.connect(partial(StudyModes.handle_choice, is_correct=is_correct, 
                                    word=word, correct_meaning=correct_meaning, 
                                    status_label=status_label, main_window=main_window))
            buttons.append((btn, is_correct))
            study_layout.addWidget(btn)
            
        return buttons

    @staticmethod
    def create_spell_mode(study_layout, words):
        from ui_components import AnimatedButton
        word, meaning = random.choice(words)
        
        # 显示释义
        meaning_label = QLabel(meaning)
        meaning_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        meaning_label.setFont(QFont('Arial', 18))
        study_layout.addWidget(meaning_label)
        
        # 输入框
        spell_input = QLineEdit()
        spell_input.setPlaceholderText('请输入单词')
        study_layout.addWidget(spell_input)
        
        # 检查按钮
        btn_check = AnimatedButton('检查答案')
        study_layout.addWidget(btn_check)
        
        return spell_input, btn_check, word

    @staticmethod
    def handle_recognize(main_window, known):
        if known:
            main_window.statusBar().showMessage('已标记为认识', 2000)
        else:
            main_window.statusBar().showMessage('已标记为不认识', 2000)
        vocab_id = getattr(main_window, 'current_vocab_id', None)
        words = main_window.db.get_words(vocab_id)
        main_window.current_word = random.choice(words)
        StudyModes.start_study(main_window)

    @staticmethod
    def next_word(main_window):
        StudyModes.start_study(main_window)

    @staticmethod
    def check_answer(main_window, is_correct, words):
        if is_correct:
            QMessageBox.information(main_window, '正确', '回答正确！')
        else:
            QMessageBox.warning(main_window, '错误', '回答错误！')
        StudyModes.next_word(main_window)

    @staticmethod
    def check_spelling(main_window, input_word, correct_word, words):
        if input_word.lower() == correct_word.lower():
            main_window.statusBar().showMessage('拼写正确！', 2000)
        else:
            main_window.statusBar().showMessage(f'拼写错误！正确答案是：{correct_word}', 3000)
        StudyModes.next_word(main_window)

    @staticmethod
    def start_study(main_window):
        # 使用保存的设置而不是从界面获取
        vocab_id = getattr(main_window, 'current_vocab_id', None)
        if not vocab_id:
            QMessageBox.warning(main_window, '错误', '请先在学习设置中选择单词本！')
            main_window.switch_page(main_window.settings_page)
            return
        
        # 切换到学习页面
        main_window.switch_page(main_window.study_page)
        
        words = main_window.db.get_words(vocab_id)
        if not words:
            QMessageBox.warning(main_window, '错误', '该单词本中没有单词！')
            return
            
        # 清除现有内容
        while main_window.study_layout.count():
            item = main_window.study_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        main_window.current_word = random.choice(words)
        
        # 使用保存的学习模式
        mode = getattr(main_window, 'study_mode', 'recognize')
        if mode == 'recognize':
            btn_know, btn_unknown = StudyModes.create_recognize_mode(main_window.study_layout, [main_window.current_word])
            btn_know.clicked.connect(lambda: StudyModes.handle_recognize(main_window, True))
            btn_unknown.clicked.connect(lambda: StudyModes.handle_recognize(main_window, False))
        elif mode == 'choice':
            buttons = StudyModes.create_choice_mode(main_window.study_layout, words, main_window=main_window)
        elif mode == 'spell':
            spell_input, btn_check, correct_word = StudyModes.create_spell_mode(main_window.study_layout, words)
            btn_check.clicked.connect(lambda: StudyModes.check_spelling(main_window, spell_input.text(), correct_word, words))
