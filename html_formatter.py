class HTMLFormatter:
    def wrap_in_table(self, title, content):
        # 네이버 블로그 UI 가이드를 반영한 메인 컨테이너 [cite: 17, 32]
        html = f"""
        <div style="max-width: 800px; margin: 0 auto; font-family: 'Nanum Gothic', sans-serif; line-height: 1.8; color: #333;">
            <table style="width: 100%; border-collapse: collapse; margin-bottom: 30px; border: 1px solid #eee;">
                <thead>
                    <tr>
                        <th style="padding: 30px; background-color: #fcfcfc; text-align: center; border-bottom: 3px solid #333;">
                            <span style="font-size: 14px; color: #888; letter-spacing: 2px;">MK CINELAB PREVIEW</span>
                            <h1 style="margin: 10px 0; color: #222; font-size: 28px;">{title}</h1>
                        </th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td style="padding: 40px 20px;">
                            {content}
                        </td>
                    </tr>
                </tbody>
            </table>
            
            <div style="background-color: #f9f9f9; padding: 20px; border-radius: 8px; text-align: center; margin-top: 40px;">
                <p style="margin: 0; font-size: 14px; color: #666;">🎬 <b>MK CINELAB</b>의 다른 영화 이야기가 궁금하다면?</p>
                <p style="margin: 10px 0 0 0; font-size: 12px; color: #999;">[이곳에 이전 포스팅 링크를 삽입하세요]</p>
            </div>
        </div>
        """
        return html