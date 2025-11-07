from PyQt6.QtWidgets import (
    QPushButton, QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QLineEdit, QTextEdit, QListWidget, QComboBox, QRadioButton,
    QButtonGroup, QStackedWidget, QFrame, QInputDialog, QDialog
)
from PyQt6.QtCore import QPropertyAnimation, QEasingCurve, pyqtProperty, QRect, Qt
from PyQt6.QtGui import QColor, QCursor, QFont
from study_modes import StudyModes
from theme_manager import Theme

class AnimatedButton(QPushButton):
    def __init__(self, text: str):
        super().__init__(text)
        self._color = QColor(100, 150, 200)
        self.animation = QPropertyAnimation(self, b"color")
        self.animation.setDuration(200)
        self.animation.setEasingCurve(QEasingCurve.Type.InOutQuad)
        self.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))

    def setup_theme_style(self, theme_colors):
        self._color = QColor(theme_colors['accent'])
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {theme_colors['button']};
                color: {theme_colors['text']};
                border: 1px solid {theme_colors['border']};
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: 500;
                min-width: 80px;
            }}
            QPushButton:hover {{
                background-color: {theme_colors['button_hover']};
                border: 1px solid {theme_colors['accent']};
            }}
            QPushButton:pressed {{
                background-color: {theme_colors['accent']};
                color: white;
            }}
        """)

    @pyqtProperty(QColor)
    def color(self):
        return self._color
    
    @color.setter
    def color(self, value):
        self._color = value
        self.setStyleSheet(f"background-color: {value.name()}; color: white; border: none; padding: 8px;")
    
    def enterEvent(self, event):
        if hasattr(self.parent(), 'theme_manager'):
            theme_colors = self.parent().theme_manager._themes[self.parent().theme_manager.get_current_theme()]
            self.animation.setEndValue(QColor(theme_colors['button_hover']))
            self.animation.start()
        super().enterEvent(event)
    
    def leaveEvent(self, event):
        if hasattr(self.parent(), 'theme_manager'):
            theme_colors = self.parent().theme_manager._themes[self.parent().theme_manager.get_current_theme()]
            self.animation.setEndValue(QColor(theme_colors['button']))
            self.animation.start()
        super().leaveEvent(event)

class UICreator:
    @staticmethod
    def create_main_page(main_window):
        layout = QVBoxLayout(main_window.main_page)
        layout.setSpacing(20)
        
        title = QLabel('智能背单词')
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setFont(QFont('Arial', 24))
        layout.addWidget(title)
        
        # 创建按钮并设置主题样式
        theme_colors = main_window.theme_manager._themes[main_window.theme_manager.get_current_theme()]
        
        btn_vocab = AnimatedButton('单词本管理')
        btn_vocab.setup_theme_style(theme_colors)
        btn_vocab.clicked.connect(lambda: main_window.switch_page(main_window.vocabulary_page))
        
        btn_stats = AnimatedButton('学习统计')
        btn_stats.setup_theme_style(theme_colors)
        btn_stats.clicked.connect(lambda: main_window.switch_page(main_window.stats_page))
        
        btn_wrong_words = AnimatedButton('错题本')
        btn_wrong_words.setup_theme_style(theme_colors)
        btn_wrong_words.clicked.connect(lambda: main_window.switch_page(main_window.wrong_words_page))
        
        btn_settings = AnimatedButton('学习设置')
        btn_settings.setup_theme_style(theme_colors)
        btn_settings.clicked.connect(lambda: main_window.switch_page(main_window.settings_page))
        
        btn_study = AnimatedButton('开始学习')
        btn_study.setup_theme_style(theme_colors)
        btn_study.clicked.connect(lambda: StudyModes.start_study(main_window))

        for btn in [btn_vocab, btn_stats, btn_wrong_words, btn_settings, btn_study]:
            btn.setMinimumHeight(50)
            layout.addWidget(btn)

    @staticmethod
    def create_vocabulary_page(main_window):
        layout = QHBoxLayout(main_window.vocabulary_page)
        theme_colors = main_window.theme_manager._themes[main_window.theme_manager.get_current_theme()]
        
        left_layout = QVBoxLayout()
        
        btn_back = AnimatedButton('返回')
        btn_back.setup_theme_style(theme_colors)
        btn_back.clicked.connect(lambda: main_window.switch_page(main_window.main_page))
        left_layout.addWidget(btn_back)
        
        main_window.vocab_list = QListWidget()
        main_window.vocab_list.itemClicked.connect(main_window.on_vocab_selected)
        left_layout.addWidget(main_window.vocab_list)
        
        btn_layout = QHBoxLayout()
        btn_add_vocab = AnimatedButton('新建单词本')
        btn_add_vocab.setup_theme_style(theme_colors)
        btn_add_vocab.clicked.connect(main_window.add_vocabulary)
        btn_delete_vocab = AnimatedButton('删除单词本')
        btn_delete_vocab.setup_theme_style(theme_colors)
        btn_delete_vocab.clicked.connect(main_window.delete_vocabulary)
        btn_layout.addWidget(btn_add_vocab)
        btn_layout.addWidget(btn_delete_vocab)
        left_layout.addLayout(btn_layout)
        
        right_layout = QVBoxLayout()
        
        main_window.words_title = QLabel('请选择一个单词本')
        main_window.words_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_window.words_title.setFont(QFont('Arial', 16))
        right_layout.addWidget(main_window.words_title)
        
        main_window.words_list = QListWidget()
        right_layout.addWidget(main_window.words_list)
        
        word_btn_layout = QHBoxLayout()
        btn_add_word = AnimatedButton('添加单词')
        btn_add_word.setup_theme_style(theme_colors)
        btn_add_word.clicked.connect(lambda: main_window.switch_page(main_window.add_word_page))
        btn_edit_word = AnimatedButton('修改单词')
        btn_edit_word.setup_theme_style(theme_colors)
        btn_edit_word.clicked.connect(main_window.edit_word)
        btn_delete_word = AnimatedButton('删除单词')
        btn_delete_word.setup_theme_style(theme_colors)
        btn_delete_word.clicked.connect(main_window.delete_word)
        btn_export = AnimatedButton('导出单词本')
        btn_export.setup_theme_style(theme_colors)
        btn_export.clicked.connect(lambda: main_window.export_vocabulary())
        word_btn_layout.addWidget(btn_add_word)
        word_btn_layout.addWidget(btn_edit_word)
        word_btn_layout.addWidget(btn_delete_word)
        word_btn_layout.addWidget(btn_export)
        right_layout.addLayout(word_btn_layout)
        
        layout.addLayout(left_layout, stretch=1)
        layout.addLayout(right_layout, stretch=2)

    @staticmethod
    def create_add_word_page(main_window):
        layout = QVBoxLayout(main_window.add_word_page)
        theme_colors = main_window.theme_manager._themes[main_window.theme_manager.get_current_theme()]
        
        btn_back = AnimatedButton('返回')
        btn_back.setup_theme_style(theme_colors)
        btn_back.clicked.connect(lambda: main_window.switch_page(main_window.main_page))
        layout.addWidget(btn_back)
        
        main_window.vocab_combo = QComboBox()
        layout.addWidget(QLabel('选择单词本：'))
        layout.addWidget(main_window.vocab_combo)
        
        main_window.word_input = QLineEdit()
        main_window.word_input.setPlaceholderText('输入单词')
        layout.addWidget(QLabel('单词：'))
        layout.addWidget(main_window.word_input)
        
        main_window.meaning_input = QTextEdit()
        main_window.meaning_input.setPlaceholderText('输入释义')
        main_window.meaning_input.setMaximumHeight(100)
        layout.addWidget(QLabel('释义：'))
        layout.addWidget(main_window.meaning_input)
        
        btn_add = AnimatedButton('添加单词')
        btn_add.setup_theme_style(theme_colors)
        btn_add.clicked.connect(main_window.add_word)
        layout.addWidget(btn_add)

    @staticmethod
    def create_settings_page(main_window):
        layout = QVBoxLayout(main_window.settings_page)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        theme_colors = main_window.theme_manager._themes[main_window.theme_manager.get_current_theme()]
        
        # 返回按钮
        btn_back = AnimatedButton('返回')
        btn_back.setup_theme_style(theme_colors)
        btn_back.clicked.connect(lambda: main_window.switch_page(main_window.main_page))
        layout.addWidget(btn_back)
        
        # 主题选择部分
        theme_group = QButtonGroup()
        main_window.theme_radio_light = QRadioButton('浅色主题')
        main_window.theme_radio_dark = QRadioButton('深色主题')
        main_window.theme_radio_blue = QRadioButton('蓝色主题')
        main_window.theme_radio_green = QRadioButton('绿色主题')
        
        # 设置默认选中
        current_theme = main_window.theme_manager.get_current_theme()
        if current_theme == Theme.LIGHT:
            main_window.theme_radio_light.setChecked(True)
        elif current_theme == Theme.DARK:
            main_window.theme_radio_dark.setChecked(True)
        elif current_theme == Theme.BLUE:
            main_window.theme_radio_blue.setChecked(True)
        elif current_theme == Theme.GREEN:
            main_window.theme_radio_green.setChecked(True)
        
        theme_group.addButton(main_window.theme_radio_light)
        theme_group.addButton(main_window.theme_radio_dark)
        theme_group.addButton(main_window.theme_radio_blue)
        theme_group.addButton(main_window.theme_radio_green)
        
        # 主题选择容器
        theme_container = QWidget()
        theme_layout = QVBoxLayout(theme_container)
        theme_layout.setSpacing(10)
        
        theme_title = QLabel('界面主题')
        theme_title.setFont(QFont('Arial', 14, QFont.Weight.Bold))
        theme_layout.addWidget(theme_title)
        
        theme_layout.addWidget(main_window.theme_radio_light)
        theme_layout.addWidget(main_window.theme_radio_dark)
        theme_layout.addWidget(main_window.theme_radio_blue)
        theme_layout.addWidget(main_window.theme_radio_green)
        
        layout.addWidget(theme_container)
        
        # 分隔线
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setFrameShadow(QFrame.Shadow.Sunken)
        layout.addWidget(line)
        
        # 单词本选择
        vocab_container = QWidget()
        vocab_layout = QVBoxLayout(vocab_container)
        vocab_layout.setSpacing(10)
        
        vocab_title = QLabel('学习设置')
        vocab_title.setFont(QFont('Arial', 14, QFont.Weight.Bold))
        vocab_layout.addWidget(vocab_title)
        
        main_window.settings_vocab_combo = QComboBox()
        vocab_layout.addWidget(QLabel('选择单词本：'))
        vocab_layout.addWidget(main_window.settings_vocab_combo)
        
        # 学习模式选择
        mode_group = QButtonGroup()
        main_window.settings_radio_recognize = QRadioButton('认识/不认识')
        main_window.settings_radio_choice = QRadioButton('选择释义')
        main_window.settings_radio_spell = QRadioButton('拼写单词')
        main_window.settings_radio_recognize.setChecked(True)
        mode_group.addButton(main_window.settings_radio_recognize)
        mode_group.addButton(main_window.settings_radio_choice)
        mode_group.addButton(main_window.settings_radio_spell)
        
        vocab_layout.addWidget(QLabel('学习模式：'))
        vocab_layout.addWidget(main_window.settings_radio_recognize)
        vocab_layout.addWidget(main_window.settings_radio_choice)
        vocab_layout.addWidget(main_window.settings_radio_spell)
        
        layout.addWidget(vocab_container)
        
        # 保存设置按钮
        btn_save = AnimatedButton('保存设置')
        btn_save.setup_theme_style(theme_colors)
        btn_save.clicked.connect(lambda: StudyModes.save_settings(main_window))
        layout.addWidget(btn_save)
        
        # 添加弹性空间
        layout.addStretch()

    @staticmethod
    def create_stats_page(main_window):
        layout = QVBoxLayout(main_window.stats_page)
        theme_colors = main_window.theme_manager._themes[main_window.theme_manager.get_current_theme()]
        
        btn_back = AnimatedButton('返回')
        btn_back.setup_theme_style(theme_colors)
        btn_back.clicked.connect(lambda: main_window.switch_page(main_window.main_page))
        layout.addWidget(btn_back)
        
        # 添加统计类型选择
        main_window.stats_type_combo = QComboBox()
        main_window.stats_type_combo.addItems(['每日统计', '每周统计', '详细统计'])
        main_window.stats_type_combo.currentTextChanged.connect(main_window.update_stats_display)
        layout.addWidget(main_window.stats_type_combo)
        
        # 添加统计显示区域
        stats_area = QWidget()
        stats_layout = QVBoxLayout(stats_area)
        
        # 显示标题
        title = QLabel('学习统计')
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setFont(QFont('Arial', 18))
        stats_layout.addWidget(title)
        
        # 显示统计数据
        main_window.stats_list = QListWidget()
        stats_layout.addWidget(main_window.stats_list)
        
        layout.addWidget(stats_area)

    @staticmethod
    def create_wrong_words_page(main_window):
        layout = QVBoxLayout(main_window.wrong_words_page)
        theme_colors = main_window.theme_manager._themes[main_window.theme_manager.get_current_theme()]
        
        # 返回按钮
        btn_back = AnimatedButton('返回')
        btn_back.setup_theme_style(theme_colors)
        btn_back.clicked.connect(lambda: main_window.switch_page(main_window.main_page))
        layout.addWidget(btn_back)
        
        # 标题
        title = QLabel('错题本')
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setFont(QFont('Arial', 18))
        layout.addWidget(title)
        
        # 错题列表
        main_window.wrong_words_list = QListWidget()
        layout.addWidget(main_window.wrong_words_list)
        
        # 按钮布局
        button_layout = QHBoxLayout()
        
        # 清除错题按钮
        btn_clear = AnimatedButton('清除错题')
        btn_clear.setup_theme_style(theme_colors)
        btn_clear.clicked.connect(main_window.clear_wrong_word)
        button_layout.addWidget(btn_clear)
        
        # 清空错题本按钮
        btn_clear_all = AnimatedButton('清空错题本')
        btn_clear_all.setup_theme_style(theme_colors)
        btn_clear_all.clicked.connect(main_window.clear_all_wrong_words)
        button_layout.addWidget(btn_clear_all)
        
        layout.addLayout(button_layout)

    @staticmethod
    def create_study_page(main_window):
        layout = QVBoxLayout(main_window.study_page)
        theme_colors = main_window.theme_manager._themes[main_window.theme_manager.get_current_theme()]
        
        btn_back = AnimatedButton('返回')
        btn_back.setup_theme_style(theme_colors)
        btn_back.clicked.connect(lambda: main_window.switch_page(main_window.main_page))
        layout.addWidget(btn_back)
        
        main_window.study_area = QWidget()
        main_window.study_layout = QVBoxLayout(main_window.study_area)
        layout.addWidget(main_window.study_area)
