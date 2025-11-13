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
                padding: 10px 20px;
                border-radius: 6px;
                font-weight: 500;
                font-size: 14px;
                min-width: 100px;
            }}
            QPushButton:hover {{
                background-color: {theme_colors['button_hover']};
                border: 2px solid {theme_colors['accent']};
                padding: 9px 19px;
            }}
            QPushButton:pressed {{
                background-color: {theme_colors['accent']};
                color: {theme_colors['text']};
                border: 2px solid {theme_colors['accent']};
            }}
            QPushButton:disabled {{
                background-color: {theme_colors['border_light']};
                color: {theme_colors['text_secondary']};
                border: 1px solid {theme_colors['border']};
            }}
        """)

    @pyqtProperty(QColor)
    def color(self):
        return self._color
    
    @color.setter
    def color(self, value):
        self._color = value
        # 获取当前主题颜色以保持边框样式
        parent = self.parent()
        if parent and hasattr(parent, 'theme_manager'):
            theme_manager = parent.theme_manager
            theme_colors = theme_manager._themes[theme_manager.get_current_theme()]
            # 根据背景色亮度自动选择文字颜色，同时保持主题边框
            brightness = value.red() * 0.299 + value.green() * 0.587 + value.blue() * 0.114
            text_color = "white" if brightness < 128 else "black"
            border_color = theme_colors['accent'] if brightness < 128 else theme_colors['border']
            self.setStyleSheet(f"""
                background-color: {value.name()}; 
                color: {text_color}; 
                border: 2px solid {border_color};
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: 500;
                font-size: 14px;
            """)
        else:
            # 根据背景色亮度自动选择文字颜色
            brightness = value.red() * 0.299 + value.green() * 0.587 + value.blue() * 0.114
            text_color = "white" if brightness < 128 else "black"
            self.setStyleSheet(f"background-color: {value.name()}; color: {text_color}; border: none; padding: 8px;")
    
    def enterEvent(self, event):
        # 缓存主题管理器引用，避免重复属性查找
        parent = self.parent()
        if parent and hasattr(parent, 'theme_manager'):
            theme_manager = parent.theme_manager
            theme_colors = theme_manager._themes[theme_manager.get_current_theme()]
            # 使用主题的主色调而不是固定的白色
            self.animation.setEndValue(QColor(theme_colors['accent']))
            self.animation.start()
        super().enterEvent(event)
    
    def leaveEvent(self, event):
        parent = self.parent()
        if parent and hasattr(parent, 'theme_manager'):
            theme_manager = parent.theme_manager
            theme_colors = theme_manager._themes[theme_manager.get_current_theme()]
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
        
        # 获取当前主题颜色
        parent = self.parent()
        if parent and hasattr(parent, 'theme_manager'):
            theme_manager = parent.theme_manager
            theme_colors = theme_manager._themes[theme_manager.get_current_theme()]
            bg_color = theme_colors['background_secondary']
        else:
            bg_color = 'white'
        
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {bg_color};
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
    def _get_theme_colors(main_window):
        """获取当前主题颜色"""
        return main_window.theme_manager._themes[main_window.theme_manager.get_current_theme()]
    
    @staticmethod
    def _create_back_button(main_window, layout, theme_colors):
        """创建返回按钮"""
        btn_back = AnimatedButton('返回')
        btn_back.setup_theme_style(theme_colors)
        # 使用partial避免lambda函数创建开销
        from functools import partial
        btn_back.clicked.connect(partial(main_window.switch_page, main_window.main_page))
        layout.addWidget(btn_back)
        return btn_back
    
    @staticmethod
    def _create_card_button(main_window, text, target_page, theme_colors):
        """创建卡片式按钮"""
        card = AnimatedCard()
        card_layout = QVBoxLayout(card)
        btn = AnimatedButton(text)
        btn.setup_theme_style(theme_colors)
        
        # 使用partial优化连接性能
        from functools import partial
        if target_page == 'study':
            btn.clicked.connect(partial(StudyModes.start_study, main_window))
        else:
            target_page_obj = getattr(main_window, f'{target_page}_page')
            btn.clicked.connect(partial(main_window.switch_page, target_page_obj))
        
        card_layout.addWidget(btn)
        return card
    
    @staticmethod
    def create_main_page(main_window):
        """创建主页面"""
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
        
        # 获取主题颜色
        theme_colors = UICreator._get_theme_colors(main_window)
        
        # 创建卡片式按钮
        button_configs = [
            ('单词本管理', 'vocabulary'),
            ('学习统计', 'stats'),
            ('错题本', 'wrong_words'),
            ('学习设置', 'settings'),
            ('开始学习', 'study')
        ]
        
        for text, target in button_configs:
            card = UICreator._create_card_button(main_window, text, target, theme_colors)
            card_layout.addWidget(card)
        
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
    def _create_button(main_window, text, callback, theme_colors):
        """创建通用按钮"""
        btn = AnimatedButton(text)
        btn.setup_theme_style(theme_colors)
        btn.clicked.connect(callback)
        return btn
    
    @staticmethod
    def create_vocabulary_page(main_window):
        """创建单词本管理页面"""
        layout = QHBoxLayout(main_window.vocabulary_page)
        theme_colors = UICreator._get_theme_colors(main_window)
        
        # 左侧布局
        left_layout = QVBoxLayout()
        UICreator._create_back_button(main_window, left_layout, theme_colors)
        
        main_window.vocab_list = QListWidget()
        main_window.vocab_list.itemClicked.connect(main_window.on_vocab_selected)
        left_layout.addWidget(main_window.vocab_list)
        
        # 单词本操作按钮
        btn_layout = QHBoxLayout()
        btn_add_vocab = UICreator._create_button(main_window, '新建单词本', main_window.add_vocabulary, theme_colors)
        btn_delete_vocab = UICreator._create_button(main_window, '删除单词本', main_window.delete_vocabulary, theme_colors)
        btn_layout.addWidget(btn_add_vocab)
        btn_layout.addWidget(btn_delete_vocab)
        left_layout.addLayout(btn_layout)
        
        # 右侧布局
        right_layout = QVBoxLayout()
        
        main_window.words_title = QLabel('请选择一个单词本')
        main_window.words_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_window.words_title.setFont(QFont('Arial', 16))
        right_layout.addWidget(main_window.words_title)
        
        # 搜索功能
        search_layout = QHBoxLayout()
        main_window.search_input = QLineEdit()
        main_window.search_input.setPlaceholderText('搜索单词...')
        btn_search = UICreator._create_button(main_window, '搜索', main_window.search_word, theme_colors)
        search_layout.addWidget(main_window.search_input)
        search_layout.addWidget(btn_search)
        right_layout.addLayout(search_layout)
        
        main_window.words_list = QListWidget()
        right_layout.addWidget(main_window.words_list)
        
        # 单词操作按钮
        word_btn_layout = QHBoxLayout()
        button_configs = [
            ('添加单词', lambda: main_window.switch_page(main_window.add_word_page)),
            ('修改单词', main_window.edit_word),
            ('删除单词', main_window.delete_word),
            ('导出单词本', lambda: main_window.export_vocabulary())
        ]
        
        for text, callback in button_configs:
            btn = UICreator._create_button(main_window, text, callback, theme_colors)
            word_btn_layout.addWidget(btn)
        
        right_layout.addLayout(word_btn_layout)
        
        layout.addLayout(left_layout, stretch=1)
        layout.addLayout(right_layout, stretch=2)

    @staticmethod
    def create_add_word_page(main_window):
        """创建添加单词页面"""
        layout = QVBoxLayout(main_window.add_word_page)
        theme_colors = UICreator._get_theme_colors(main_window)
        
        # 返回按钮
        UICreator._create_back_button(main_window, layout, theme_colors)
        
        # 单词本选择
        main_window.vocab_combo = QComboBox()
        layout.addWidget(QLabel('选择单词本：'))
        layout.addWidget(main_window.vocab_combo)
        
        # 单词输入
        main_window.word_input = QLineEdit()
        main_window.word_input.setPlaceholderText('输入单词')
        layout.addWidget(QLabel('单词：'))
        layout.addWidget(main_window.word_input)

        # 类型选择
        main_window.word_type_combo = QComboBox()
        main_window.word_type_combo.addItems(['单词', '短语'])
        main_window.word_type_combo.setMinimumWidth(100)
        word_type_layout = QHBoxLayout()
        word_type_layout.addWidget(QLabel('类型：'))
        word_type_layout.addWidget(main_window.word_type_combo)
        layout.addLayout(word_type_layout)
        
        # 词性释义输入区域
        UICreator._create_pos_meaning_section(main_window, layout, theme_colors)
        
        # 添加单词按钮
        btn_add = UICreator._create_button(main_window, '添加单词', main_window.add_word, theme_colors)
        layout.addWidget(btn_add)

    @staticmethod
    def _create_pos_meaning_section(main_window, layout, theme_colors):
        """创建词性释义输入区域"""
        pos_meaning_container = QWidget()
        pos_meaning_layout = QVBoxLayout(pos_meaning_container)
        pos_meaning_layout.setSpacing(10)

        pos_title = QLabel('词性与释义：')
        pos_title.setFont(QFont('Arial', 12, QFont.Weight.Bold))
        pos_meaning_layout.addWidget(pos_title)

        # 创建添加词性按钮
        add_pos_button = UICreator._create_button(main_window, '添加词性', 
                                                 lambda: UICreator.add_pos_meaning_pair(main_window), 
                                                 theme_colors)
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
    
    @staticmethod
    def add_pos_meaning_pair(main_window):
        """添加词性释义对"""
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
        delete_button = UICreator._create_button(main_window, '删除', 
                                                lambda: main_window.pos_meaning_layout.removeWidget(pair_widget), 
                                                UICreator._get_theme_colors(main_window))
        delete_button.setMaximumWidth(60)
        pair_layout.addWidget(delete_button)
        
        # 添加到主布局
        main_window.pos_meaning_layout.addWidget(pair_widget)

    @staticmethod
    def _create_section_container(title, font_size=14):
        """创建带标题的容器"""
        container = QWidget()
        container_layout = QVBoxLayout(container)
        container_layout.setSpacing(10)
        
        title_label = QLabel(title)
        title_label.setFont(QFont('Arial', font_size, QFont.Weight.Bold))
        container_layout.addWidget(title_label)
        
        return container, container_layout
    
    @staticmethod
    def create_settings_page(main_window):
        """创建设置页面"""
        layout = QVBoxLayout(main_window.settings_page)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        theme_colors = UICreator._get_theme_colors(main_window)
        
        # 返回按钮
        UICreator._create_back_button(main_window, layout, theme_colors)
        
        # 主题选择部分
        theme_container, theme_layout = UICreator._create_section_container('界面主题')
        
        theme_group = QButtonGroup()
        theme_buttons = {
            'light': QRadioButton('浅色主题'),
            'dark': QRadioButton('深色主题'),
            'blue': QRadioButton('蓝色主题'),
            'green': QRadioButton('绿色主题')
        }
        
        # 设置默认选中
        current_theme = main_window.theme_manager.get_current_theme()
        for theme_name, radio_button in theme_buttons.items():
            if current_theme == getattr(Theme, theme_name.upper()):
                radio_button.setChecked(True)
            theme_group.addButton(radio_button)
            theme_layout.addWidget(radio_button)
            setattr(main_window, f'theme_radio_{theme_name}', radio_button)
        
        layout.addWidget(theme_container)
        
        # 分隔线
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setFrameShadow(QFrame.Shadow.Sunken)
        layout.addWidget(line)
        
        # 学习设置部分
        vocab_container, vocab_layout = UICreator._create_section_container('学习设置')
        
        main_window.settings_vocab_combo = QComboBox()
        vocab_layout.addWidget(QLabel('选择单词本：'))
        vocab_layout.addWidget(main_window.settings_vocab_combo)
        
        # 学习模式选择
        mode_group = QButtonGroup()
        mode_buttons = {
            'recognize': QRadioButton('认识/不认识'),
            'choice': QRadioButton('选择释义'),
            'spell': QRadioButton('拼写单词')
        }
        
        vocab_layout.addWidget(QLabel('学习模式：'))
        for mode_name, radio_button in mode_buttons.items():
            if mode_name == 'recognize':
                radio_button.setChecked(True)
            mode_group.addButton(radio_button)
            vocab_layout.addWidget(radio_button)
            setattr(main_window, f'settings_radio_{mode_name}', radio_button)
        
        # 学习类型选择
        from PyQt6.QtWidgets import QCheckBox
        vocab_layout.addWidget(QLabel('学习类型：'))
        
        type_checkboxes = {
            'word': QCheckBox('学习单词'),
            'phrase': QCheckBox('学习短语')
        }
        
        for type_name, checkbox in type_checkboxes.items():
            if type_name == 'word':
                checkbox.setChecked(True)
            # 不设置具体样式，使用全局QCheckBox样式
            vocab_layout.addWidget(checkbox)
            setattr(main_window, f'settings_checkbox_{type_name}', checkbox)
        
        layout.addWidget(vocab_container)
        
        # 保存设置按钮
        btn_save = UICreator._create_button(main_window, '保存设置', 
                                           lambda: StudyModes.save_settings(main_window), 
                                           theme_colors)
        layout.addWidget(btn_save)
        
        # 添加弹性空间
        layout.addStretch()

    @staticmethod
    def _create_simple_page(main_window, page_name, title_text, button_configs=None):
        """创建简单页面（统计、错题本等）"""
        layout = QVBoxLayout(getattr(main_window, f'{page_name}_page'))
        theme_colors = UICreator._get_theme_colors(main_window)
        
        # 返回按钮
        UICreator._create_back_button(main_window, layout, theme_colors)
        
        # 标题
        title = QLabel(title_text)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setFont(QFont('Arial', 18))
        layout.addWidget(title)
        
        # 列表控件
        list_widget = QListWidget()
        setattr(main_window, f'{page_name}_list', list_widget)
        layout.addWidget(list_widget)
        
        # 按钮区域
        if button_configs:
            button_layout = QHBoxLayout()
            for text, callback in button_configs:
                btn = UICreator._create_button(main_window, text, callback, theme_colors)
                button_layout.addWidget(btn)
            layout.addLayout(button_layout)
        
        return layout
    
    @staticmethod
    def create_stats_page(main_window):
        """创建统计页面"""
        layout = UICreator._create_simple_page(main_window, 'stats', '学习统计')
        
        # 添加统计类型选择
        main_window.stats_type_combo = QComboBox()
        main_window.stats_type_combo.addItems(['每日统计', '每周统计', '详细统计'])
        main_window.stats_type_combo.currentTextChanged.connect(main_window.update_stats_display)
        layout.insertWidget(2, main_window.stats_type_combo)  # 插入到标题和列表之间

    @staticmethod
    def create_wrong_words_page(main_window):
        """创建错题本页面"""
        button_configs = [
            ('清除错题', main_window.clear_wrong_word),
            ('清空错题本', main_window.clear_all_wrong_words)
        ]
        UICreator._create_simple_page(main_window, 'wrong_words', '错题本', button_configs)

    @staticmethod
    def create_study_page(main_window):
        """创建学习页面"""
        layout = QVBoxLayout(main_window.study_page)
        theme_colors = UICreator._get_theme_colors(main_window)
        
        # 返回按钮
        UICreator._create_back_button(main_window, layout, theme_colors)
        
        # 学习区域
        main_window.study_area = QWidget()
        main_window.study_layout = QVBoxLayout(main_window.study_area)
        layout.addWidget(main_window.study_area)
