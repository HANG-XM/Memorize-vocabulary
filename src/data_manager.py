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
                type TEXT NOT NULL DEFAULT 'word',  -- 添加类型字段，默认为单词
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
        self.cursor.execute('DELETE FROM word_pos_meanings WHERE vocabulary_id = ?', (vocab_id,))
        self.cursor.execute('DELETE FROM vocabularies WHERE id = ?', (vocab_id,))
        self.conn.commit()
    
    def get_vocabularies(self):
        self.cursor.execute('SELECT id, name FROM vocabularies')
        return self.cursor.fetchall()
    def export_vocabulary(self, vocab_id: int, file_path: str) -> Tuple[bool, str]:
        try:
            words = self.get_words_with_pos_meanings(vocab_id)
            with open(file_path, 'w', newline='', encoding='utf-8-sig') as file:
                writer = csv.writer(file)
                writer.writerow(['单词', '释义'])
                writer.writerows(words)
            return True, "导出成功"
        except Exception as e:
            return False, f"导出失败：{str(e)}"
    def delete_word(self, word: str, vocab_id: int):
        try:
            # 先删除该单词的所有词性释义
            self.cursor.execute('DELETE FROM word_pos_meanings WHERE word = ? AND vocabulary_id = ?', 
                            (word, vocab_id))
            # 同时删除学习记录
            self.cursor.execute('DELETE FROM study_records WHERE word = ? AND vocabulary_id = ?', 
                            (word, vocab_id))
            # 同时删除错题记录
            self.cursor.execute('DELETE FROM wrong_words WHERE word = ? AND vocabulary_id = ?', 
                            (word, vocab_id))
            self.conn.commit()
            return True, "单词删除成功"
        except Exception as e:
            self.conn.rollback()
            return False, f"删除失败：{str(e)}"
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
        words = self.cursor.fetchall()
        # 添加序号
        return [(f"{i+1}. {word}", meanings) for i, (word, meanings) in enumerate(words)]
    def add_word_with_pos_meanings(self, word: str, pos_meanings: List[Tuple[str, str]], vocab_id: int) -> Tuple[bool, str]:
        try:
            if not word.strip():
                return False, "单词不能为空"
                
            # 检查单词是否已存在
            self.cursor.execute('SELECT id FROM word_pos_meanings WHERE word = ? AND vocabulary_id = ?', 
                            (word.strip(), vocab_id))
            if self.cursor.fetchone():
                return False, "该单词已存在于当前单词本中"
            
            # 添加词性和释义（使用默认类型'word'）
            for pos, meaning in pos_meanings:
                self.cursor.execute('INSERT INTO word_pos_meanings (word, pos, meaning, vocabulary_id, type) VALUES (?, ?, ?, ?, ?)',
                                (word.strip(), pos, meaning.strip(), vocab_id, 'word'))
            
            self.conn.commit()
            return True, "单词添加成功"
        except sqlite3.Error as e:
            self.conn.rollback()
            return False, f"添加失败：{str(e)}"
    
    def add_word_with_pos_meanings_and_type(self, word: str, pos_meanings: List[Tuple[str, str]], word_type: str, vocab_id: int) -> Tuple[bool, str]:
        try:
            if not word.strip():
                return False, "单词不能为空"
                
            # 检查单词是否已存在
            self.cursor.execute('SELECT id FROM word_pos_meanings WHERE word = ? AND vocabulary_id = ?', 
                            (word.strip(), vocab_id))
            if self.cursor.fetchone():
                return False, "该单词已存在于当前单词本中"
            
            # 添加词性和释义（使用传入的类型）
            for pos, meaning in pos_meanings:
                self.cursor.execute('INSERT INTO word_pos_meanings (word, pos, meaning, vocabulary_id, type) VALUES (?, ?, ?, ?, ?)',
                                (word.strip(), pos, meaning.strip(), vocab_id, word_type))
            
            self.conn.commit()
            return True, "单词添加成功"
        except sqlite3.Error as e:
            self.conn.rollback()
            return False, f"添加失败：{str(e)}"

    def get_words_with_pos_meanings(self, vocab_id, word_type=None):
        if word_type:
            if isinstance(word_type, list):
                # 处理多个类型的情况
                placeholders = ','.join(['?' for _ in word_type])
                self.cursor.execute(f'''
                    SELECT word, GROUP_CONCAT(pos || ': ' || meaning, '; ')
                    FROM word_pos_meanings
                    WHERE vocabulary_id = ? AND type IN ({placeholders})
                    GROUP BY word
                ''', [vocab_id] + word_type)
            else:
                # 处理单个类型的情况
                self.cursor.execute('''
                    SELECT word, GROUP_CONCAT(pos || ': ' || meaning, '; ')
                    FROM word_pos_meanings
                    WHERE vocabulary_id = ? AND type = ?
                    GROUP BY word
                ''', (vocab_id, word_type))
        else:
            self.cursor.execute('''
                SELECT word, GROUP_CONCAT(pos || ': ' || meaning, '; ')
                FROM word_pos_meanings
                WHERE vocabulary_id = ?
                GROUP BY word
            ''', (vocab_id,))
        words = self.cursor.fetchall()
        return [(f"{i+1}. {word}", meanings) for i, (word, meanings) in enumerate(words)]
    def get_word_pos_meanings(self, word: str, vocab_id: int):
        self.cursor.execute('''
            SELECT pos, meaning
            FROM word_pos_meanings
            WHERE vocabulary_id = ? AND word = ?
        ''', (vocab_id, word))
        return self.cursor.fetchall()
    def move_word(self, word: str, from_vocab_id: int, to_vocab_id: int) -> Tuple[bool, str]:
        try:
            # 开始事务 - 使用一致的方式
            self.cursor.execute('BEGIN TRANSACTION')
            
            # 检查目标单词本是否已存在该单词
            self.cursor.execute('SELECT id FROM word_pos_meanings WHERE word = ? AND vocabulary_id = ?', 
                            (word, to_vocab_id))
            if self.cursor.fetchone():
                self.conn.rollback()  # 使用一致的rollback方式
                return False, "目标单词本中已存在该单词"
                
            # 获取原单词的所有词性释义
            self.cursor.execute('''
                SELECT pos, meaning
                FROM word_pos_meanings
                WHERE vocabulary_id = ? AND word = ?
            ''', (from_vocab_id, word))
            pos_meanings = self.cursor.fetchall()
            
            if not pos_meanings:
                self.conn.rollback()
                return False, "在原单词本中未找到该单词"
            
            # 添加到新单词本
            for pos, meaning in pos_meanings:
                self.cursor.execute('''
                    INSERT INTO word_pos_meanings (word, pos, meaning, vocabulary_id) 
                    VALUES (?, ?, ?, ?)
                ''', (word, pos, meaning, to_vocab_id))
                
                # 检查插入是否成功
                if self.cursor.rowcount == 0:
                    self.conn.rollback()
                    return False, "添加到目标单词本失败"
            
            # 从原单词本删除 - 使用参数化查询确保准确性
            self.cursor.execute('''
                DELETE FROM word_pos_meanings 
                WHERE word = ? AND vocabulary_id = ?
            ''', (word, from_vocab_id))
            
            deleted_count = self.cursor.rowcount
            
            # 同时删除相关的学习记录和错题记录
            self.cursor.execute('DELETE FROM study_records WHERE word = ? AND vocabulary_id = ?', 
                            (word, from_vocab_id))
            self.cursor.execute('DELETE FROM wrong_words WHERE word = ? AND vocabulary_id = ?', 
                            (word, from_vocab_id))
            
            # 提交事务
            self.conn.commit()
            
            if deleted_count > 0:
                return True, "单词移动成功"
            else:
                return False, "从原单词本删除失败"
                
        except sqlite3.Error as e:
            self.conn.rollback()
            return False, f"移动失败：{str(e)}"
        except Exception as e:
            self.conn.rollback()
            return False, f"移动过程中发生错误：{str(e)}"