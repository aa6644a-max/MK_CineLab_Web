import sqlite3
import os
from datetime import datetime

class DBManager:
    def __init__(self, db_name="mk_cinelab.db"):
        self.db_path = os.path.join(os.path.dirname(__file__), db_name)
        self._create_table()

    def _get_connection(self):
        return sqlite3.connect(self.db_path)

    def _create_table(self):
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS posts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                movie_title TEXT NOT NULL,
                post_type TEXT NOT NULL,
                content TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()
        conn.close()

    def save_post(self, movie_title, post_type, content):
        conn = self._get_connection()
        cursor = conn.cursor()
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute('''
            INSERT INTO posts (movie_title, post_type, content, created_at)
            VALUES (?, ?, ?, ?)
        ''', (movie_title, post_type, content, now))
        conn.commit()
        conn.close()
        print(f"[DB 저장 완료] {movie_title} ({post_type})")

    def get_all_posts(self):
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT id, movie_title, post_type, created_at FROM posts ORDER BY created_at DESC')
        rows = cursor.fetchall()
        conn.close()
        return rows

    # 💡 새로 추가된 기능: 특정 글의 내용(HTML)만 쏙 빼오기
    def get_post_content(self, post_id):
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT content FROM posts WHERE id = ?', (post_id,))
        row = cursor.fetchone()
        conn.close()
        return row[0] if row else None

    # 💡 새로 추가된 기능: 글 삭제하기
    def delete_post(self, post_id):
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM posts WHERE id = ?', (post_id,))
        conn.commit()
        conn.close()