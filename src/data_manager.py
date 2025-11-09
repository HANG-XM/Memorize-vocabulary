import sqlite3
from typing import List, Tuple, Optional
import csv
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

        # 创建词性释义表
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS word_pos_meanings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                word TEXT NOT NULL,
                pos TEXT NOT NULL,
                meaning TEXT NOT NULL,
                vocabulary_id INTEGER,
                FOREIGN KEY (vocabulary_id) REFERENCES vocabularies (id)
            )
        ''')

        # 添加学习记录表
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS study_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                vocabulary_id INTEGER,
                word TEXT,
                is_correct BOOLEAN,
                study_mode TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (vocabulary_id) REFERENCES vocabularies (id)
            )
        ''')

        # 创建错题本表
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS wrong_words (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                vocabulary_id INTEGER,
                word TEXT NOT NULL,
                meaning TEXT NOT NULL,
                first_wrong_time DATETIME DEFAULT CURRENT_TIMESTAMP,
                wrong_count INTEGER DEFAULT 1,
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
    def export_vocabulary(self, vocab_id: int, file_path: str) -> Tuple[bool, str]:
        try:
            words = self.get_words(vocab_id)
            with open(file_path, 'w', newline='', encoding='utf-8-sig') as file:  # 使用utf-8-sig编码
                writer = csv.writer(file)
                writer.writerow(['单词', '释义'])  # 写入标题行
                writer.writerows(words)
            return True, "导出成功"
        except Exception as e:
            return False, f"导出失败：{str(e)}"
    def add_word(self, word: str, meaning: str, vocab_id: int) -> Tuple[bool, str]:
        try:
            if not word.strip() or not meaning.strip():
                return False, "单词和释义不能为空"
            
            # 检查单词是否已存在
            self.cursor.execute('SELECT id FROM words WHERE word = ? AND vocabulary_id = ?', 
                            (word.strip(), vocab_id))
            if self.cursor.fetchone():
                return False, "该单词已存在于当前单词本中"
                
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
    def delete_word(self, word: str, vocab_id: int):
        self.cursor.execute('DELETE FROM word_pos_meanings WHERE word = ? AND vocabulary_id = ?', 
                            (word, vocab_id))
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
            words = self.get_words_with_pos_meanings(vocab_id)
            for word, meanings in words:
                words_list.addItem(f"{word}: {meanings}")
    def record_study(self, vocab_id: int, word: str, is_correct: bool, study_mode: str):
        self.cursor.execute('INSERT INTO study_records (vocabulary_id, word, is_correct, study_mode) VALUES (?, ?, ?, ?)',
                            (vocab_id, word, is_correct, study_mode))
        self.conn.commit()

    def get_daily_stats(self, vocab_id: int = None):
        if vocab_id:
            self.cursor.execute('''
                SELECT DATE(timestamp) as date,
                    COUNT(*) as total_words,
                    SUM(is_correct) as correct_words,
                    ROUND(SUM(is_correct) * 100.0 / COUNT(*), 2) as accuracy
                FROM study_records
                WHERE vocabulary_id = ?
                GROUP BY DATE(timestamp)
                ORDER BY DATE(timestamp) DESC
            ''', (vocab_id,))
        else:
            self.cursor.execute('''
                SELECT DATE(timestamp) as date,
                    COUNT(*) as total_words,
                    SUM(is_correct) as correct_words,
                    ROUND(SUM(is_correct) * 100.0 / COUNT(*), 2) as accuracy
                FROM study_records
                GROUP BY DATE(timestamp)
                ORDER BY DATE(timestamp) DESC
            ''')
        return self.cursor.fetchall()
    def add_wrong_word(self, vocab_id: int, word: str, meaning: str):
        self.cursor.execute('''
            INSERT OR REPLACE INTO wrong_words (vocabulary_id, word, meaning, wrong_count)
            VALUES (?, ?, ?, COALESCE((SELECT wrong_count FROM wrong_words 
            WHERE vocabulary_id = ? AND word = ?), 0) + 1)
        ''', (vocab_id, word, meaning, vocab_id, word))
        self.conn.commit()

    def get_wrong_words(self, vocab_id: int = None):
        if vocab_id:
            self.cursor.execute('SELECT word, meaning, wrong_count FROM wrong_words WHERE vocabulary_id = ?', (vocab_id,))
        else:
            self.cursor.execute('SELECT word, meaning, wrong_count FROM wrong_words')
        return self.cursor.fetchall()

    def remove_wrong_word(self, word: str):
        self.cursor.execute('DELETE FROM wrong_words WHERE word = ?', (word,))
        self.conn.commit()
    def get_detailed_stats(self, vocab_id: int = None):
        if vocab_id:
            self.cursor.execute('''
                SELECT 
                    DATE(timestamp) as date,
                    study_mode,
                    COUNT(*) as total_words,
                    SUM(is_correct) as correct_words,
                    ROUND(SUM(is_correct) * 100.0 / COUNT(*), 2) as accuracy
                FROM study_records
                WHERE vocabulary_id = ?
                GROUP BY DATE(timestamp), study_mode
                ORDER BY DATE(timestamp) DESC, study_mode
            ''', (vocab_id,))
        else:
            self.cursor.execute('''
                SELECT 
                    DATE(timestamp) as date,
                    study_mode,
                    COUNT(*) as total_words,
                    SUM(is_correct) as correct_words,
                    ROUND(SUM(is_correct) * 100.0 / COUNT(*), 2) as accuracy
                FROM study_records
                GROUP BY DATE(timestamp), study_mode
                ORDER BY DATE(timestamp) DESC, study_mode
            ''')
        return self.cursor.fetchall()

    def get_weekly_stats(self, vocab_id: int = None):
        if vocab_id:
            self.cursor.execute('''
                SELECT 
                    strftime('%Y-%W', timestamp) as week,
                    COUNT(*) as total_words,
                    SUM(is_correct) as correct_words,
                    ROUND(SUM(is_correct) * 100.0 / COUNT(*), 2) as accuracy
                FROM study_records
                WHERE vocabulary_id = ?
                GROUP BY strftime('%Y-%W', timestamp)
                ORDER BY week DESC
                LIMIT 8
            ''', (vocab_id,))
        else:
            self.cursor.execute('''
                SELECT 
                    strftime('%Y-%W', timestamp) as week,
                    COUNT(*) as total_words,
                    SUM(is_correct) as correct_words,
                    ROUND(SUM(is_correct) * 100.0 / COUNT(*), 2) as accuracy
                FROM study_records
                GROUP BY strftime('%Y-%W', timestamp)
                ORDER BY week DESC
                LIMIT 8
            ''')
        return self.cursor.fetchall()
    def search_words(self, vocab_id: int, search_text: str):
        self.cursor.execute('''
            SELECT word, GROUP_CONCAT(pos || ': ' || meaning, '; ')
            FROM word_pos_meanings 
            WHERE vocabulary_id = ? AND (LOWER(word) LIKE ? OR LOWER(meaning) LIKE ?)
            GROUP BY word
        ''', (vocab_id, f'%{search_text}%', f'%{search_text}%'))
        return self.cursor.fetchall()
    def add_word_with_pos_meanings(self, word: str, pos_meanings: List[Tuple[str, str]], vocab_id: int) -> Tuple[bool, str]:
        try:
            if not word.strip():
                return False, "单词不能为空"
                
            # 检查单词是否已存在
            self.cursor.execute('SELECT id FROM word_pos_meanings WHERE word = ? AND vocabulary_id = ?', 
                            (word.strip(), vocab_id))
            if self.cursor.fetchone():
                return False, "该单词已存在于当前单词本中"
            
            # 添加词性和释义
            for pos, meaning in pos_meanings:
                self.cursor.execute('INSERT INTO word_pos_meanings (word, pos, meaning, vocabulary_id) VALUES (?, ?, ?, ?)',
                                (word.strip(), pos, meaning.strip(), vocab_id))
            
            self.conn.commit()
            return True, "单词添加成功"
        except sqlite3.Error as e:
            self.conn.rollback()
            return False, f"添加失败：{str(e)}"

    def get_words_with_pos_meanings(self, vocab_id):
        self.cursor.execute('''
            SELECT word, GROUP_CONCAT(pos || ': ' || meaning, '; ')
            FROM word_pos_meanings
            WHERE vocabulary_id = ?
            GROUP BY word
        ''', (vocab_id,))
        return self.cursor.fetchall()