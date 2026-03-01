class HTMLFormatter:
    def __init__(self):
        # 네이버 블로그에 최적화된 기본 스타일 설정
        self.table_style = (
            "width: 100%; border-collapse: collapse; border: 1px solid #eeeeee; "
            "font-family: 'Nanum Gothic', sans-serif; line-height: 1.8;"
        )

    def wrap_in_table(self, title, content):
        """본문 내용을 네이버 스마트에디터 호환 표 서식으로 감쌉니다."""
        html = f"""
        <div style="max-width: 800px; margin: 0 auto;">
            <table style="{self.table_style}">
                <thead>
                    <tr>
                        <th style="padding: 20px; background-color: #f9f9f9; text-align: center; border-bottom: 2px solid #333;">
                            <h2 style="margin: 0; color: #333;">{title}</h2>
                        </th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td style="padding: 30px; color: #444; font-size: 16px;">
                            {content.replace('\n', '<br>')}
                        </td>
                    </tr>
                </tbody>
            </table>
        </div>
        """
        return html

    def format_post(self, raw_text):
        """클로드의 결과물(텍스트)을 깔끔한 HTML로 최종 가공합니다."""
        # 텍스트 내의 특정 마커들을 HTML 태그로 치환하거나 정제하는 로직
        # 가이드북에 따라 불렛 포인트(√) 등을 강조할 수 있습니다.
        formatted_text = raw_text.replace("√", "<b>√</b>")
        
        # 실제 앱에서는 클로드가 반환한 HTML 코드 블록만 추출하는 로직이 추가될 수 있습니다.
        return formatted_text