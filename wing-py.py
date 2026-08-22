import streamlit as st
import os
import google.generativeai as genai
import pandas as pd
from datetime import datetime, timedelta

# 1. Streamlit Secrets에서 API 키 안전하게 불러오기
if "GEMINI_API_KEY" in st.secrets:
    API_KEY = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=API_KEY)
else:
    st.error("🚨 Streamlit Cloud Secrets에 'GEMINI_API_KEY'가 설정되어 있지 않습니다!")
    st.stop()

# 안정적인 제미나이 모델 설정
model = genai.GenerativeModel('gemini-1.5-flash')

st.set_page_config(
    page_title="부동산 AI 비서 '날개'", 
    page_icon="🏡", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# 세션 상태 초기화
if "memo_list" not in st.session_state:
    st.session_state.memo_list = []

# 보안용 로그인 비밀번호 설정
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.title("🔒 부동산 AI 비서 '날개' - 보안 로그인")
    st.write("승인된 사용자(중개사무소)만 접속할 수 있습니다.")
    
    password_input = st.text_input("비밀번호를 입력하세요", type="password")
    
    if st.button("로그인"):
        if password_input == "1128":
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error("비밀번호가 틀렸습니다!")
    st.stop()

# -------------------------------------------------------------
# 공통 함수: AI 결과를 구글 킵 또는 노트에 원클릭으로 보낼 수 있게 해주는 UI 컴포넌트
# -------------------------------------------------------------
def render_save_to_keep_buttons(text_to_save, unique_key):
    st.markdown("---")
    st.markdown("### 📌 구글 킵(Keep) 및 노트에 원클릭 저장")
    
    # 1. 텍스트 자동 복사 HTML/JS 버튼 (웹뷰/브라우저 클립보드 직행)
    # 파이썬 자바스크립트 컴포넌트를 이용해 원클릭 복사 구현
    safe_text = text_to_save.replace('"', '\\"').replace('\n', '\\n')
    
    copy_html = f"""
    <div style="margin: 10px 0;">
        <button onclick="navigator.clipboard.writeText(`{safe_text}`); alert('클립보드에 복사되었습니다! 구글 킵이나 메모장에 붙여넣으세요.');" 
                style="background-color: #4285F4; color: white; border: none; padding: 12px 20px; border-radius: 6px; font-size: 14px; font-weight: bold; cursor: pointer; width: 100%;">
            📋 AI 요약 내용 원클릭 복사하기 (구글 킵에 붙여넣기)
        </button>
    </div>
    """
    st.markdown(copy_html, unsafe_allow_html=True)
    
    # 2. 구글 킵 웹/앱 다이렉트 실행 링크
    st.markdown(
        f"""
        <div style="text-align: center; margin-top: 5px;">
            <a href="https://keep.google.com/" target="_blank" style="background-color: #FBBC05; color: black; padding: 10px 20px; text-decoration: none; border-radius: 6px; font-size: 14px; font-weight: bold; display: block; text-align: center;">
                🟡 구글 킵(Google Keep) 앱/웹 열기
            </a>
        </div>
        """, 
        unsafe_allow_html=True
    )

# -------------------------------------------------------------
# 메인 프로그램 시작
# -------------------------------------------------------------
st.title("🏡 부동산 AI 비서 '날개'")
st.write("올인원 AI 중개 솔루션 (모바일 최적화 버전)")

menu = st.sidebar.selectbox(
    "기능 선택", 
    [
        "1. 계약서 OCR 및 데이터 자동화", 
        "2. 스마트 메모 및 자동 복사/저장", 
        "3. AI 기반 상담 프로파일링", 
        "4. 시각화된 매물 관리", 
        "5. 일정 관리 및 캘린더 자동 추가"
    ]
)

# -------------------------------------------------------------
# 1. 계약서 OCR 및 데이터 자동화
# -------------------------------------------------------------
if menu == "1. 계약서 OCR 및 데이터 자동화":
    st.header("📄 계약서 OCR 및 데이터 자동 파싱")
    uploaded_file = st.file_uploader("계약서 파일을 업로드하세요", type=["png", "jpg", "jpeg", "pdf"])
    
    if uploaded_file is not None:
        st.image(uploaded_file, caption="업로드된 계약서", use_container_width=True)
        if st.button("AI OCR 분석 시작"):
            with st.spinner("AI가 계약서 분석 중..."):
                try:
                    bytes_data = uploaded_file.getvalue()
                    prompt = "이 계약서 이미지에서 매도인, 매수인, 계약일, 중도금, 잔금 날짜 및 금액을 찾아내어 보기 쉽게 요약해 주고, 법정 중개 보수도 계산해 줘."
                    
                    response = model.generate_content([
                        {"mime_type": uploaded_file.type, "data": bytes_data},
                        prompt
                    ])
                    st.success("분석 완료!")
                    st.write(response.text)
                    
                    # 원클릭 노트 저장 버튼 추가
                    render_save_to_keep_buttons(response.text, "ocr_result")
                    
                except Exception as e:
                    st.error(f"오류가 발생했습니다: {e}")

# -------------------------------------------------------------
# 2. 스마트 메모 및 파일 업로드 통합 분석 & 저장
# -------------------------------------------------------------
elif menu == "2. 스마트 메모 및 파일 업로드 분석":
    st.header("📝 스마트 메모 및 파일 업로드 분석")
    st.write("상담 내용을 텍스트로 직접 입력하거나, 관련 파일(문서, 이미지, 오디오 등)을 업로드하여 AI 분석을 진행하세요.")
    
    memo_input = st.text_area("상담 내용을 직접 입력하세요")
    uploaded_memo_file = st.file_uploader("상담 관련 파일 업로드 (이미지, PDF, 문서, 오디오 등)", type=["png", "jpg", "jpeg", "pdf", "txt", "mp3", "wav"])
    
    if st.button("메모/파일 AI 분석 및 저장"):
        if memo_input or uploaded_memo_file:
            with st.spinner("AI가 내용을 분석 중입니다..."):
                try:
                    content_parts = []
                    prompt_text = f"""
                    다음은 부동산 상담 내용 또는 자료입니다. 이를 분석하여 다음 형식으로 깔끔하게 정리해 주세요:
                    1. 핵심 키워드 태그 (예: #매매, #아파트 등)
                    2. 상담 내용 요약
                    3. 고객 요구사항 및 특이사항
                    
                    [직접 입력한 메모]: {memo_input}
                    """
                    content_parts.append(prompt_text)
                    
                    if uploaded_memo_file is not None:
                        bytes_data = uploaded_memo_file.getvalue()
                        content_parts.append({"mime_type": uploaded_memo_file.type, "data": bytes_data})
                    
                    response = model.generate_content(content_parts)
                    ai_result = response.text
                    
                    st.success("분석 완료!")
                    st.write(ai_result)
                    
                    # 세션 메모 리스트에 자동 저장
                    now_time = datetime.now().strftime("%Y-%m-%d %H:%M")
                    file_info = uploaded_memo_file.name if uploaded_memo_file else "텍스트 입력"
                    
                    st.session_state.memo_list.insert(0, {
                        "시간": now_time,
                        "출처": file_info,
                        "내용": memo_input if memo_input else "(파일 업로드 분석)",
                        "AI분석": ai_result
                    })
                    st.success("💾 앱 내 메모장에 안전하게 저장되었습니다!")
                    
                    # 원클릭 노트 저장 버튼 추가
                    render_save_to_keep_buttons(ai_result, "memo_result")
                    
                except Exception as e:
                    st.error(f"분석 및 저장 중 오류 발생: {e}")
        else:
            st.warning("상담 내용을 입력하시거나 파일을 업로드해주세요.")
            
    st.write("---")
    st.subheader("📚 저장된 메모 목록")
    if st.session_state.memo_list:
        df_memo = pd.DataFrame(st.session_state.memo_list)
        st.dataframe(df_memo, use_container_width=True)
        
        csv = df_memo.to_csv(index=False).encode('utf-8-sig')
        st.download_button(
            label="📥 메모 전체 엑셀(CSV)로 백업하기",
            data=csv,
            file_name=f"memo_backup_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv",
        )
    else:
        st.info("아직 저장된 메모가 없습니다.")

# -------------------------------------------------------------
# 3. AI 기반 상담 프로파일링
# -------------------------------------------------------------
elif menu == "3. AI 기반 상담 프로파일링":
    st.header("🧠 AI 상담 프로파일링")
    client_talk = st.text_area("고객의 발언 입력:")
    
    if st.button("속마음 분석 시작"):
        if client_talk:
            with st.spinner("고객의 심리와 대응 전략 분석 중..."):
                try:
                    prompt = f"다음 고객의 발언을 분석하여 숨겨진 속마음과 효과적인 중개 대응 전략을 요약해 줘:\n\n{client_talk}"
                    response = model.generate_content(prompt)
                    st.success("분석 완료!")
                    st.write(response.text)
                    
                    # 원클릭 노트 저장 버튼 추가
                    render_save_to_keep_buttons(response.text, "profiling_result")
                    
                except Exception as e:
                    st.error(f"분석 중 오류 발생: {e}")
        else:
            st.warning("고객의 발언을 입력해주세요.")

# -------------------------------------------------------------
# 4. 시각화된 매물 관리 시스템
# -------------------------------------------------------------
elif menu == "4. 시각화된 매물 관리":
    st.header("🏢 시각화된 매물 관리")
    uploaded_excel = st.file_uploader("엑셀 파일 업로드 (.xlsx)", type=["xlsx"])
    if uploaded_excel is not None:
        df = pd.read_excel(uploaded_excel)
        st.dataframe(df)
        
        # 매물 요약 분석 기능 추가
        if st.button("AI 매물 데이터 브리핑 생성"):
            with st.spinner("매물 데이터 분석 중..."):
                try:
                    summary_prompt = f"다음 매물 데이터 목록을 분석하여 주요 특징과 주목해야 할 매물을 요약해 줘:\n\n{df.head(10).to_string()}"
                    response = model.generate_content(summary_prompt)
                    st.success("브리핑 생성 완료!")
                    st.write(response.text)
                    
                    # 원클릭 노트 저장 버튼 추가
                    render_save_to_keep_buttons(response.text, "property_result")
                except Exception as e:
                    st.error(f"분석 오류: {e}")

# -------------------------------------------------------------
# 5. 일정 관리 및 캘린더 자동 추가
# -------------------------------------------------------------
elif menu == "5. 일정 관리 및 캘린더 자동 추가":
    st.header("📅 잔금일 및 일정 캘린더 자동 등록")
    
    event_title = st.text_input("일정 제목 (예: [잔금] 홍길동 고객님 아파트 계약)", "부동산 잔금일")
    event_date = st.date_input("날짜 선택 (잔금일 등)")
    event_memo = st.text_area("상세 메모", "금액 및 특이사항 입력")
    
    if st.button("캘린더 연동 링크 생성"):
        date_str = event_date.strftime("%Y%m%d")
        cal_url = f"https://calendar.google.com/calendar/render?action=TEMPLATE&text={event_title}&dates={date_str}/{date_str}&details={event_memo}"
        
        st.success("✨ 캘린더 연동 링크가 준비되었습니다!")
        st.markdown(
            f"""
            <div style="text-align: center; margin-top: 20px;">
                <a href="{cal_url}" target="_blank" style="background-color: #4CAF50; color: white; padding: 15px 25px; text-decoration: none; border-radius: 8px; font-size: 16px; font-weight: bold; display: inline-block;">
                    📱 삼성 / 구글 캘린더에 일정 바로 등록하기
                </a>
            </div>
            """, 
            unsafe_allow_html=True
        )
        st.info("💡 위 버튼을 누르면 웹뷰 앱 안에서 외부 캘린더 앱으로 매끄럽게 연결됩니다.")
