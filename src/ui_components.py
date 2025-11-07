from PyQt6.QtWidgets import (
    QPushButton, QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QLineEdit, QTextEdit, QListWidget, QComboBox, QRadioButton,
    QButtonGroup, QStackedWidget, QFrame, QInputDialog, QDialog
)
from PyQt6.QtCore import QPropertyAnimation, QEasingCurve, pyqtProperty, QRect, Qt
from PyQt6.QtGui import QColor, QCursor, QFont
from study_modes import StudyModes

class AnimatedButton(QPushButton):
    def __init__(self, text: str):
        super().__init__(text)
        self._color = QColor(100, 150, 200)
        self.animation = QPropertyAnimation(self, b"color")
        self.animation.setDuration(200)
        self.animation.setEasingCurve(QEasingCurve.Type.InOutQuad)
        self.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self._setup_style()

    def _setup_style(self):
        self.setStyleSheet("""
            QPushButton {
                background-color: rgb(100, 150, 200);
                color: white;
                border: none;
                padding: 8px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: rgb(120, 170, 220);
            }
            QPushButton:pressed {
                background-color: rgb(80, 130, 180);
            }
        """)   

    @pyqtProperty(QColor)
    def color(self):
        return self._color
    
    @color.setter
    def color(self, value):
        self._color = value
        self.setStyleSheet(f"background-color: {value.name()}; color: white; border: none; padding: 8px;")
    
    def enterEvent(self, event):
        self.animation.setEndValue(QColor(120, 170, 220))
        self.animation.start()
        super().enterEvent(event)
    
    def leaveEvent(self, event):
        self.animation.setEndValue(QColor(100, 150, 200))
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
        
        btn_vocab = AnimatedButton('单词本管理')
        btn_vocab.clicked.connect(lambda: main_window.switch_page(main_window.vocabulary_page))
        btn_stats = AnimatedButton('学习统计')
        btn_stats.clicked.connect(lambda: main_window.switch_page(main_window.stats_page))
        btn_settings = AnimatedButton('学习设置')
        btn_settings.clicked.connect(lambda: main_window.switch_page(main_window.settings_page))
        btn_study = AnimatedButton('开始学习')
        btn_study.clicked.connect(lambda: StudyModes.start_study(main_window))

        for btn in [btn_vocab, btn_stats, btn_settings, btn_study]:
            btn.setMinimumHeight(50)
            layout.addWidget(btn)

    @staticmethod
    def create_vocabulary_page(main_window):
        layout = QHBoxLayout(main_window.vocabulary_page)
        
        left_layout = QVBoxLayout()
        
        btn_back = AnimatedButton('返回')
        btn_back.clicked.connect(lambda: main_window.switch_page(main_window.main_page))
        left_layout.addWidget(btn_back)
        
        main_window.vocab_list = QListWidget()
        main_window.vocab_list.itemClicked.connect(main_window.on_vocab_selected)
        left_layout.addWidget(main_window.vocab_list)
        
        btn_layout = QHBoxLayout()
        btn_add_vocab = AnimatedButton('新建单词本')
        btn_add_vocab.clicked.connect(main_window.add_vocabulary)
        btn_delete_vocab = AnimatedButton('删除单词本')
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
        btn_add_word.clicked.connect(lambda: main_window.switch_page(main_window.add_word_page))
        btn_edit_word = AnimatedButton('修改单词')
        btn_edit_word.clicked.connect(main_window.edit_word)
        btn_delete_word = AnimatedButton('删除单词')
        btn_delete_word.clicked.connect(main_window.delete_word)
        btn_export = AnimatedButton('导出单词本')
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
        
        btn_back = AnimatedButton('返回')
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
        btn_add.clicked.connect(main_window.add_word)
        layout.addWidget(btn_add)

    @staticmethod
    def create_settings_page(main_window):
        layout = QVBoxLayout(main_window.settings_page)
        
        btn_back = AnimatedButton('返回')
        btn_back.clicked.connect(lambda: main_window.switch_page(main_window.main_page))
        layout.addWidget(btn_back)
        
        # 单词本选择
        main_window.settings_vocab_combo = QComboBox()
        layout.addWidget(QLabel('选择单词本：'))
        layout.addWidget(main_window.settings_vocab_combo)
        
        # 学习模式选择
        mode_group = QButtonGroup()
        main_window.settings_radio_recognize = QRadioButton('认识/不认识')
        main_window.settings_radio_choice = QRadioButton('选择释义')
        main_window.settings_radio_spell = QRadioButton('拼写单词')
        main_window.settings_radio_recognize.setChecked(True)
        mode_group.addButton(main_window.settings_radio_recognize)
        mode_group.addButton(main_window.settings_radio_choice)
        mode_group.addButton(main_window.settings_radio_spell)
        
        layout.addWidget(QLabel('选择学习模式：'))
        layout.addWidget(main_window.settings_radio_recognize)
        layout.addWidget(main_window.settings_radio_choice)
        layout.addWidget(main_window.settings_radio_spell)
        
        # 保存设置按钮
        btn_save = AnimatedButton('保存设置')
        btn_save.clicked.connect(lambda: StudyModes.save_settings(main_window))
        layout.addWidget(btn_save)

    @staticmethod
    def create_stats_page(main_window):
        layout = QVBoxLayout(main_window.stats_page)
        
        btn_back = AnimatedButton('返回')
        btn_back.clicked.connect(lambda: main_window.switch_page(main_window.main_page))
        layout.addWidget(btn_back)
        
        # 添加统计显示区域
        stats_area = QWidget()
        stats_layout = QVBoxLayout(stats_area)
        
        # 显示标题
        title = QLabel('学习统计')
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setFont(QFont('Arial', 18))
        stats_layout.addWidget(title)
        
        # 显示统计数据
        stats_list = QListWidget()
        main_window.stats_list = stats_list  # 确保stats_list被正确赋值给main_window
        stats_layout.addWidget(stats_list)
        
        layout.addWidget(stats_area)

    @staticmethod
    def create_study_page(main_window):
        layout = QVBoxLayout(main_window.study_page)
        
        btn_back = AnimatedButton('返回')
        btn_back.clicked.connect(lambda: main_window.switch_page(main_window.main_page))
        layout.addWidget(btn_back)
        
        main_window.study_area = QWidget()
        main_window.study_layout = QVBoxLayout(main_window.study_area)
        layout.addWidget(main_window.study_area)
