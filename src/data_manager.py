import sqlite3
from typing import List, Tuple, Optional

class DatabaseManager:
    def __init__(self, db_name='vocabulary.db'):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self.init_db()
    
    def init_db(self):
        # 创建单词本表
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS vocabularies (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL
            )
        ''')
        
        # 创建单词表
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS words (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                word TEXT NOT NULL,
                meaning TEXT NOT NULL,
                vocabulary_id INTEGER,
                FOREIGN KEY (vocabulary_id) REFERENCES vocabularies (id)
            )
        ''')
        self.conn.commit()
    
    def add_vocabulary(self, name: str) -> Tuple[bool, str]:
        try:
            if not name.strip():
                return False, "单词本名称不能为空"
            self.cursor.execute('INSERT INTO vocabularies (name) VALUES (?)', (name.strip(),))
            self.conn.commit()
            return True, "单词本创建成功"
        except sqlite3.IntegrityError:
            return False, "该单词本已存在"
        except Exception as e:
            return False, f"创建失败：{str(e)}"
    
    def delete_vocabulary(self, vocab_id):
        self.cursor.execute('DELETE FROM words WHERE vocabulary_id = ?', (vocab_id,))
        self.cursor.execute('DELETE FROM vocabularies WHERE id = ?', (vocab_id,))
        self.conn.commit()
    
    def get_vocabularies(self):
        self.cursor.execute('SELECT id, name FROM vocabularies')
        return self.cursor.fetchall()
    
    def add_word(self, word: str, meaning: str, vocab_id: int) -> Tuple[bool, str]:
        try:
            if not word.strip() or not meaning.strip():
                return False, "单词和释义不能为空"
            self.cursor.execute('INSERT INTO words (word, meaning, vocabulary_id) VALUES (?, ?, ?)',
                            (word.strip(), meaning.strip(), vocab_id))
            self.conn.commit()
            return True, "单词添加成功"
        except sqlite3.Error as e:
            return False, f"添加失败：{str(e)}"
    
    def get_words(self, vocab_id):
        self.cursor.execute('SELECT word, meaning FROM words WHERE vocabulary_id = ?', (vocab_id,))
        return self.cursor.fetchall()
    def update_word(self, old_word, new_word, new_meaning, vocab_id):
        self.cursor.execute('UPDATE words SET word = ?, meaning = ? WHERE word = ? AND vocabulary_id = ?',
                        (new_word, new_meaning, old_word, vocab_id))
        self.conn.commit()    
    def delete_word(self, word):
        self.cursor.execute('DELETE FROM words WHERE word = ?', (word,))
        self.conn.commit()
    def update_vocab_list(self, vocab_list):
        vocab_list.clear()
        vocabularies = self.get_vocabularies()
        for vocab_id, name in vocabularies:
            vocab_list.addItem(f"{name} (ID: {vocab_id})")

    def update_vocab_combo(self, combo):
        combo.clear()
        vocabularies = self.get_vocabularies()
        for vocab_id, name in vocabularies:
            combo.addItem(name, vocab_id)

    def update_words_list(self, words_list, vocab_id):
        words_list.clear()
        if vocab_id:
            words = self.get_words(vocab_id)
            for word, meaning in words:
                words_list.addItem(f"{word}: {meaning}")