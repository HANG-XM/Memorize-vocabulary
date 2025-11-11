from PyQt6.QtWidgets import (
    QPushButton, QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QLineEdit, QTextEdit, QListWidget, QComboBox, QRadioButton,
    QButtonGroup, QStackedWidget, QFrame, QInputDialog, QDialog
)
from PyQt6.QtCore import QPropertyAnimation, QEasingCurve, pyqtProperty, QRect, Qt, QParallelAnimationGroup, QSequentialAnimationGroup
from PyQt6.QtGui import QColor, QCursor, QFont, QPainter, QLinearGradient
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

class AnimatedLabel(QLabel):
    def __init__(self, text: str = ""):
        super().__init__(text)
        self._opacity = 1.0
        self.opacity_animation = QPropertyAnimation(self, b"opacity")
        self.opacity_animation.setDuration(300)
        self.opacity_animation.setEasingCurve(QEasingCurve.Type.InOutQuad)
        
        self._scale = 1.0
        self.scale_animation = QPropertyAnimation(self, b"scale")
        self.scale_animation.setDuration(200)
        self.scale_animation.setEasingCurve(QEasingCurve.Type.OutBack)

    @pyqtProperty(float)
    def opacity(self):
        return self._opacity
    
    @opacity.setter
    def opacity(self, value):
        self._opacity = value
        self.setStyleSheet(f"color: rgba(0, 0, 0, {value});")
    
    @pyqtProperty(float)
    def scale(self):
        return self._scale
    
    @scale.setter
    def scale(self, value):
        self._scale = value
        self.setStyleSheet(f"font-size: {int(14 * value)}px;")
    
    def fade_in(self):
        self.opacity_animation.setStartValue(0.0)
        self.opacity_animation.setEndValue(1.0)
        self.opacity_animation.start()
    
    def fade_out(self):
        self.opacity_animation.setStartValue(1.0)
        self.opacity_animation.setEndValue(0.0)
        self.opacity_animation.start()
    
    def pulse(self):
        self.scale_animation.setStartValue(1.0)
        self.scale_animation.setEndValue(1.1)
        self.scale_animation.setLoopCount(2)
        self.scale_animation.setDirection(QPropertyAnimation.Direction.Forward)
        self.scale_animation.start()

class AnimatedCard(QFrame):
    def __init__(self):
        super().__init__()
        self.setFrameStyle(QFrame.Shape.StyledPanel)
        self.setLineWidth(2)
        
        self._elevation = 0
        self.elevation_animation = QPropertyAnimation(self, b"elevation")
        self.elevation_animation.setDuration(150)
        self.elevation_animation.setEasingCurve(QEasingCurve.Type.OutQuad)

    @pyqtProperty(int)
    def elevation(self):
        return self._elevation
    
    @elevation.setter
    def elevation(self, value):
        self._elevation = value
        # Qt样式表不支持box-shadow，使用边框和背景色模拟阴影效果
        border_color = "#e0e0e0"
        if value > 0:
            # 根据高度值调整边框颜色来模拟阴影
            shadow_intensity = min(255, 100 + value * 15)
            border_color = f"rgba(0,0,0,{shadow_intensity/255:.2f})"
        
        self.setStyleSheet(f"""
            QFrame {{
                background-color: white;
                border-radius: 8px;
                border: 2px solid {border_color};
                margin: {value}px;
            }}
        """)
    
    def enterEvent(self, event):
        self.elevation_animation.setStartValue(0)
        self.elevation_animation.setEndValue(4)
        self.elevation_animation.start()
        super().enterEvent(event)
    
    def leaveEvent(self, event):
        self.elevation_animation.setStartValue(4)
        self.elevation_animation.setEndValue(0)
        self.elevation_animation.start()
        super().leaveEvent(event)

class UICreator:
    @staticmethod
    def create_main_page(main_window):
        layout = QVBoxLayout(main_window.main_page)
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # 使用动画标题
        title = AnimatedLabel('智能背单词')
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setFont(QFont('Arial', 24, QFont.Weight.Bold))
        layout.addWidget(title)
        
        # 创建卡片容器
        card_container = QWidget()
        card_layout = QVBoxLayout(card_container)
        card_layout.setSpacing(15)
        
        # 创建按钮并设置主题样式
        theme_colors = main_window.theme_manager._themes[main_window.theme_manager.get_current_theme()]
        
        # 创建卡片式按钮
        btn_vocab_card = AnimatedCard()
        btn_vocab_layout = QVBoxLayout(btn_vocab_card)
        btn_vocab = AnimatedButton('单词本管理')
        btn_vocab.setup_theme_style(theme_colors)
        btn_vocab.clicked.connect(lambda: main_window.switch_page(main_window.vocabulary_page))
        btn_vocab_layout.addWidget(btn_vocab)
        
        btn_stats_card = AnimatedCard()
        btn_stats_layout = QVBoxLayout(btn_stats_card)
        btn_stats = AnimatedButton('学习统计')
        btn_stats.setup_theme_style(theme_colors)
        btn_stats.clicked.connect(lambda: main_window.switch_page(main_window.stats_page))
        btn_stats_layout.addWidget(btn_stats)
        
        btn_wrong_words_card = AnimatedCard()
        btn_wrong_words_layout = QVBoxLayout(btn_wrong_words_card)
        btn_wrong_words = AnimatedButton('错题本')
        btn_wrong_words.setup_theme_style(theme_colors)
        btn_wrong_words.clicked.connect(lambda: main_window.switch_page(main_window.wrong_words_page))
        btn_wrong_words_layout.addWidget(btn_wrong_words)
        
        btn_settings_card = AnimatedCard()
        btn_settings_layout = QVBoxLayout(btn_settings_card)
        btn_settings = AnimatedButton('学习设置')
        btn_settings.setup_theme_style(theme_colors)
        btn_settings.clicked.connect(lambda: main_window.switch_page(main_window.settings_page))
        btn_settings_layout.addWidget(btn_settings)
        
        btn_study_card = AnimatedCard()
        btn_study_layout = QVBoxLayout(btn_study_card)
        btn_study = AnimatedButton('开始学习')
        btn_study.setup_theme_style(theme_colors)
        btn_study.clicked.connect(lambda: StudyModes.start_study(main_window))
        btn_study_layout.addWidget(btn_study)
        
        # 添加卡片到卡片容器布局
        card_layout.addWidget(btn_vocab_card)
        card_layout.addWidget(btn_stats_card)
        card_layout.addWidget(btn_wrong_words_card)
        card_layout.addWidget(btn_settings_card)
        card_layout.addWidget(btn_study_card)
        
        # 添加卡片容器到主布局
        layout.addWidget(card_container)
        
        # 添加页面切换动画
        def animate_page_switch():
            title.fade_in()
            from PyQt6.QtCore import QTimer
            QTimer.singleShot(100, lambda: title.pulse())
        
        # 连接页面切换信号
        main_window.stack.currentChanged.connect(animate_page_switch)

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
        
        # 添加搜索框和按钮
        search_layout = QHBoxLayout()
        main_window.search_input = QLineEdit()
        main_window.search_input.setPlaceholderText('搜索单词...')
        btn_search = AnimatedButton('搜索')
        btn_search.setup_theme_style(theme_colors)
        btn_search.clicked.connect(main_window.search_word)
        search_layout.addWidget(main_window.search_input)
        search_layout.addWidget(btn_search)
        right_layout.addLayout(search_layout)
        
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

        # 在单词输入框后添加类型选择
        main_window.word_type_combo = QComboBox()
        main_window.word_type_combo.addItems(['单词', '短语'])
        main_window.word_type_combo.setMinimumWidth(100)
        word_type_layout = QHBoxLayout()
        word_type_layout.addWidget(QLabel('类型：'))
        word_type_layout.addWidget(main_window.word_type_combo)
        layout.addLayout(word_type_layout)
        
        # 创建词性释义输入区域
        pos_meaning_container = QWidget()
        pos_meaning_layout = QVBoxLayout(pos_meaning_container)
        pos_meaning_layout.setSpacing(10)

        pos_title = QLabel('词性与释义：')
        pos_title.setFont(QFont('Arial', 12, QFont.Weight.Bold))
        pos_meaning_layout.addWidget(pos_title)

        # 创建添加词性按钮
        add_pos_button = AnimatedButton('添加词性')
        add_pos_button.setup_theme_style(theme_colors)
        add_pos_button.clicked.connect(lambda: UICreator.add_pos_meaning_pair(main_window))
        pos_meaning_layout.addWidget(add_pos_button)

        # 创建滚动区域用于显示词性释义对
        from PyQt6.QtWidgets import QScrollArea
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setMinimumHeight(200)
        scroll_content = QWidget()
        main_window.pos_meaning_layout = QVBoxLayout(scroll_content)
        scroll_area.setWidget(scroll_content)
        pos_meaning_layout.addWidget(scroll_area)

        layout.addWidget(pos_meaning_container)
        
        # 添加一个默认的词性释义对
        UICreator.add_pos_meaning_pair(main_window)
        
        btn_add = AnimatedButton('添加单词')
        btn_add.setup_theme_style(theme_colors)
        btn_add.clicked.connect(main_window.add_word)
        layout.addWidget(btn_add)

    @staticmethod
    def add_pos_meaning_pair(main_window):
        # 创建词性选择和释义输入的容器
        pair_widget = QWidget()
        pair_layout = QHBoxLayout(pair_widget)
        pair_layout.setSpacing(10)
        
        # 词性选择下拉框
        pos_combo = QComboBox()
        pos_combo.addItems(['n.', 'adj.', 'adv.', 'v.', 'prep.', 'conj.', 'pron.', 'art.', 'num.', 'interj.'])
        pos_combo.setMinimumWidth(80)
        pair_layout.addWidget(QLabel('词性：'))
        pair_layout.addWidget(pos_combo)
        
        # 释义输入框
        meaning_input = QTextEdit()
        meaning_input.setPlaceholderText('输入该词性下的释义')
        meaning_input.setMaximumHeight(60)
        meaning_input.setMinimumWidth(200)
        pair_layout.addWidget(QLabel('释义：'))
        pair_layout.addWidget(meaning_input)
        
        # 删除按钮
        delete_button = AnimatedButton('删除')
        delete_button.setup_theme_style(main_window.theme_manager._themes[main_window.theme_manager.get_current_theme()])
        delete_button.setMaximumWidth(60)
        delete_button.clicked.connect(lambda: main_window.pos_meaning_layout.removeWidget(pair_widget))
        pair_layout.addWidget(delete_button)
        
        # 添加到主布局
        main_window.pos_meaning_layout.addWidget(pair_widget)

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
        
        # 学习类型选择 - 使用真正的多选框
        from PyQt6.QtWidgets import QCheckBox
        vocab_layout.addWidget(QLabel('学习类型：'))
        main_window.settings_checkbox_word = QCheckBox('学习单词')
        main_window.settings_checkbox_phrase = QCheckBox('学习短语')
        main_window.settings_checkbox_word.setChecked(True)
        
        vocab_layout.addWidget(main_window.settings_checkbox_word)
        vocab_layout.addWidget(main_window.settings_checkbox_phrase)
        
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
