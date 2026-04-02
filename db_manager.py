import sqlite3
import os
from datetime import datetime

class DBManager:
    def __init__(self, db_name="mk_cinelab.db"):
        # DB 파일이 저장될 경로 설정
        self.db_path = os.path.join(os.path.dirname(__file__), db_name)
        self._create_table()

    def _get_connection(self):
        """DB 연결을 생성하고 반환합니다."""
        return sqlite3.connect(self.db_path)

    def _create_table(self):
        """앱이 처음 실행될 때 테이블(저장소)이 없으면 만듭니다."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # 글을 저장할 'posts'라는 이름의 표(테이블) 생성
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS posts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                movie_title TEXT NOT NULL,
                post_type TEXT NOT NULL,  -- 'preview', 'review', 'news'
                content TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()
        conn.close()

    def save_post(self, movie_title, post_type, content):
        """생성된 블로그 글을 DB에 저장합니다."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # 한국 시간 기준으로 현재 시간 가져오기
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        cursor.execute('''
            INSERT INTO posts (movie_title, post_type, content, created_at)
            VALUES (?, ?, ?, ?)
        ''', (movie_title, post_type, content, now))
        
        conn.commit()
        conn.close()
        print(f"[DB 저장 완료] {movie_title} ({post_type})")

    def get_all_posts(self):
        """저장된 모든 글의 목록을 최신순으로 가져옵니다."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT id, movie_title, post_type, created_at FROM posts ORDER BY created_at DESC')
        rows = cursor.fetchall()
        
        conn.close()
        return rows