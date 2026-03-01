import customtkinter as ctk
import pyperclip
from tkinter import messagebox
from tmdb_client import TMDBClient
from gemini_client import GeminiClient
from prompt_builder import PromptBuilder
from html_formatter import HTMLFormatter

# GUI 테마 설정
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class MKCineLabApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("MK CINELAB: 제미나이 블로그 자동화 앱")
        self.geometry("900x750")

        # 엔진 초기화
        self.tmdb = TMDBClient()
        self.gemini = GeminiClient() 
        self.builder = PromptBuilder()
        self.formatter = HTMLFormatter()

        # 하단 상태 표시줄
        self.status_label = ctk.CTkLabel(self, text="준비 완료", text_color="gray")
        self.status_label.pack(side="bottom", pady=10)

        # 3가지 탭 생성 (리뷰, 프리뷰, 뉴스)
        self.tabview = ctk.CTkTabview(self, width=860, height=650)
        self.tabview.pack(padx=20, pady=20)

        self.tab_review = self.tabview.add("영화 리뷰")
        self.tab_preview = self.tabview.add("영화 프리뷰")
        self.tab_news = self.tabview.add("영화 소식")

        self.setup_review_tab()
        self.setup_preview_tab()
        self.setup_news_tab()

    def setup_review_tab(self):
        ctk.CTkLabel(self.tab_review, text="영화 제목:").pack(pady=(10, 0))
        self.review_title = ctk.CTkEntry(self.tab_review, width=400)
        self.review_title.pack(pady=5)

        ctk.CTkLabel(self.tab_review, text="나의 주관적 감상평:").pack(pady=(10, 0))
        self.review_comment = ctk.CTkTextbox(self.tab_review, width=600, height=200)
        self.review_comment.pack(pady=5)

        ctk.CTkButton(self.tab_review, text="리뷰 생성 시작", command=self.generate_review).pack(pady=20)

    def setup_preview_tab(self):
        ctk.CTkLabel(self.tab_preview, text="개봉 예정작 제목:").pack(pady=(10, 0))
        self.preview_title = ctk.CTkEntry(self.tab_preview, width=400)
        self.preview_title.pack(pady=5)

        ctk.CTkLabel(self.tab_preview, text="포스팅 방향성 (예: 배우 중심):").pack(pady=(10, 0))
        self.preview_point = ctk.CTkEntry(self.tab_preview, width=400)
        self.preview_point.pack(pady=5)

        ctk.CTkButton(self.tab_preview, text="프리뷰 생성 시작", command=self.generate_preview).pack(pady=20)

    def setup_news_tab(self):
        ctk.CTkLabel(self.tab_news, text="뉴스 기사 내용:").pack(pady=(10, 0))
        self.news_content = ctk.CTkTextbox(self.tab_news, width=600, height=300)
        self.news_content.pack(pady=5)

        ctk.CTkButton(self.tab_news, text="소식 포스팅 생성", command=self.generate_news).pack(pady=20)

    # --- 실행 로직 ---

    def process_generation(self, prompt, title):
        try:
            self.status_label.configure(text="제미나이가 글을 쓰는 중입니다...", text_color="cyan")
            self.update()

            result = self.gemini.generate_post(prompt)
            final_html = self.formatter.wrap_in_table(title, result)
            pyperclip.copy(final_html)

            self.status_label.configure(text="생성 완료! 클립보드에 복사되었습니다.", text_color="green")
            messagebox.showinfo("성공", "포스팅이 클립보드에 복사되었습니다.\n블로그에 Ctrl+V 하세요!")
        except Exception as e:
            messagebox.showerror("에러", str(e))

    def generate_review(self):
        title = self.review_title.get().strip()
        comment = self.review_comment.get("1.0", "end").strip()
        
        if not title:
            messagebox.showwarning("입력 확인", "영화 제목을 입력해 주세요.")
            return

        self.status_label.configure(text=f"'{title}' 검색 중...", text_color="yellow")
        self.update()

        movie_info = self.tmdb.search_movie(title)
        
        if movie_info:
            details = self.tmdb.get_movie_details(movie_info['id'])
            prompt = self.builder.build_review_prompt(details, comment)
            self.process_generation(prompt, f"{details['title']} 리뷰")
        else:
            self.status_label.configure(text="검색 결과가 없습니다.", text_color="red")
            messagebox.showerror("검색 실패", "해당하는 영화 정보가 없습니다.\n제목을 다시 확인해 주세요.")

    def generate_preview(self):
        title = self.preview_title.get().strip()
        point = self.preview_point.get().strip()
        
        if not title:
            messagebox.showwarning("입력 확인", "영화 제목을 입력해 주세요.")
            return

        self.status_label.configure(text=f"'{title}' 정보 수집 중...", text_color="yellow")
        self.update()

        movie_info = self.tmdb.search_movie(title)
        
        if movie_info:
            details = self.tmdb.get_movie_details(movie_info['id'])
            prompt = self.builder.build_preview_prompt(details, point)
            self.process_generation(prompt, f"{details['title']} 프리뷰")
        else:
            self.status_label.configure(text="검색 결과가 없습니다.", text_color="red")
            messagebox.showerror("검색 실패", "해당하는 영화 정보가 없습니다.\n정확한 제목을 입력해 주세요.")

    def generate_news(self):
        content = self.news_content.get("1.0", "end").strip()
        if not content:
            messagebox.showwarning("입력 확인", "뉴스 내용을 입력해 주세요.")
            return
        prompt = self.builder.build_news_prompt(content)
        self.process_generation(prompt, "최신 영화 뉴스")

if __name__ == "__main__":
    app = MKCineLabApp()
    app.mainloop()