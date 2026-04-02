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
        # 1. Secrets에서 데이터 가져오기
        raw_json = st.secrets.get("GOOGLE_CREDENTIALS_JSON")
        
        if not raw_json:
            st.error("Secrets에 GOOGLE_CREDENTIALS_JSON 설정이 없습니다.")
            return None
        
        try:
            # 💡 안전장치 1: JSON 파싱 시 제어문자(실제 줄바꿈 등) 오류를 무시하도록 strict=False 추가
            creds_info = json.loads(raw_json.strip(), strict=False)
            
            # 💡 안전장치 2: 혹시 꼬여있을 줄바꿈 문자열(\n)을 확실하게 찐 줄바꿈으로 복원 (인증 핵심)
            if "private_key" in creds_info:
                creds_info["private_key"] = creds_info["private_key"].replace("\\n", "\n")
                
            creds = Credentials.from_service_account_info(creds_info, scopes=self.scopes)
            return gspread.authorize(creds)
        except Exception as e:
            st.error(f"구글 인증 에러: {e}")
            return None

    def save_post(self, movie_title, post_type, content):
        try:
            sh = self.client.open(self.spreadsheet_name)
            worksheet = sh.get_worksheet(0) # 첫 번째 시트
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            worksheet.append_row([now, movie_title, post_type, content])
            return True
        except Exception as e:
            st.error(f"저장 중 에러 발생: {e}")
            return False

    def get_all_posts(self):
        try:
            sh = self.client.open(self.spreadsheet_name)
            worksheet = sh.get_worksheet(0)
            values = worksheet.get_all_values()
            if len(values) <= 1: return []
            return [[i, v[1], v[2], v[0]] for i, v in enumerate(values[1:], start=2)]
        except:
            return []

    def get_post_content(self, row_index):
        try:
            sh = self.client.open(self.spreadsheet_name)
            worksheet = sh.get_worksheet(0)
            return worksheet.cell(row_index, 4).value
        except:
            return None

    def delete_post(self, row_index):
        try:
            sh = self.client.open(self.spreadsheet_name)
            worksheet = sh.get_worksheet(0)
            worksheet.delete_rows(row_index)
            return True
        except:
            return False