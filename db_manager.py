import gspread
from google.oauth2.service_account import Credentials
import streamlit as st
import json
from datetime import datetime

class DBManager:
    def __init__(self, spreadsheet_name="MK_CINELAB_DB"):
        self.spreadsheet_name = spreadsheet_name
        self.scopes = [
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive"
        ]
        self.client = self._authenticate()

    def _authenticate(self):
        # 스트림릿 Secrets에서 구글 자격증명 JSON을 가져옵니다.
        if "GOOGLE_CREDENTIALS_JSON" not in st.secrets:
            st.error("Secrets에 GOOGLE_CREDENTIALS_JSON 설정이 없습니다.")
            return None
        
        creds_info = json.loads(st.secrets["GOOGLE_CREDENTIALS_JSON"])
        creds = Credentials.from_service_account_info(creds_info, scopes=self.scopes)
        return gspread.authorize(creds)

    def save_post(self, movie_title, post_type, content):
        try:
            # 1. 스프레드시트 열기
            sh = self.client.open(self.spreadsheet_name)
            # 2. 첫 번째 시트 선택
            worksheet = sh.get_worksheet(0)
            
            # 3. 데이터 준비 (날짜, 제목, 타입, 내용)
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            row = [now, movie_title, post_type, content]
            
            # 4. 시트 맨 아래에 추가
            worksheet.append_row(row)
            return True
        except Exception as e:
            st.error(f"구글 시트 저장 에러: {e}")
            return False

    def get_all_posts(self):
        """보물창고 기능을 위해 시트의 모든 데이터를 가져옵니다."""
        try:
            sh = self.client.open(self.spreadsheet_name)
            worksheet = sh.get_worksheet(0)
            # 전체 데이터를 리스트로 가져옴 (헤더 제외)
            all_values = worksheet.get_all_values()
            if len(all_values) <= 1: return []
            
            # [id(인덱스), 제목, 타입, 날짜] 형태로 변환하여 반환
            return [[i, v[1], v[2], v[0]] for i, v in enumerate(all_values[1:], start=2)]
        except:
            return []

    def get_post_content(self, row_index):
        """특정 행의 HTML 내용을 가져옵니다."""
        try:
            sh = self.client.open(self.spreadsheet_name)
            worksheet = sh.get_worksheet(0)
            return worksheet.cell(row_index, 4).value
        except:
            return None

    def delete_post(self, row_index):
        """특정 행을 삭제합니다."""
        try:
            sh = self.client.open(self.spreadsheet_name)
            worksheet = sh.get_worksheet(0)
            worksheet.delete_rows(row_index)
            return True
        except:
            return False