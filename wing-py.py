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
model = genai.GenerativeModel('gemini-3.6-flash')

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
        "2. 계약서 검토 및 맞춤 특약 추천", 
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
                    
                    render_save_to_keep_buttons(response.text, "ocr_result")
                    
                except Exception as e:
                    st.error(f"오류가 발생했습니다: {e}")

# -------------------------------------------------------------
# 2. 계약서 검토 및 맞춤 특약 추천
# -------------------------------------------------------------
elif menu == "2. 계약서 검토 및 맞춤 특약 추천":
    st.header("📝 계약서 특약 사항 및 리스크 검토")
    st.write("부동산 계약 과정에서 필요한 특약 사항을 추천받고, 계약서상 주의해야 할 위험 요소를 검토하세요.")
    
    col1, col2 = st.columns(2)
    with col1:
        contract_type = st.selectbox("계약 종류 선택", ["매매 계약", "전세 계약", "월세 계약"])
    with col2:
        property_type = st.selectbox("물건 종류 선택", ["아파트/오피스텔", "빌라/다세대", "상가/사무실", "토지"])
        
    special_situation = st.text_area("특수 상황 또는 요청사항 입력 (예: 임대인이 세입자 전세보증금으로 기존 근저당 말소 조건, 누수 책임 한계 등):")
    
    uploaded_contract_file = st.file_uploader("검토할 계약서 파일 업로드 (선택사항, PDF/이미지/텍스트)", type=["pdf", "png", "jpg", "txt"])
    
    if st.button("특약 추천 및 계약서 분석 실행"):
        with st.spinner("최적의 특약 사항과 법적 리스크를 분석 중입니다..."):
            try:
                content_parts = []
                prompt_text = f"""
                당신은 베테랑 공인중개사이자 부동산 전문 변호사입니다.
                다음 조건에 맞는 안전하고 빈틈없는 계약 특약 사항을 제안하고, 주의해야 할 리스크를 분석해 주세요.
                
                - 계약 종류: {contract_type}
                - 물건 종류: {property_type}
                - 특수 상황/요청: {special_situation}
                
                다음 내용을 포함하여 작성해 주세요:
                1. 반드시 들어가야 할 필수 특약 문구 (법적 효력이 명확한 표준 문구 형태)
                2. 중개사와 임대인/임차인 입장에서 주의해야 할 리스크 및 방어 방안
                3. 계약 체결 시 체크리스트
                """
                content_parts.append(prompt_text)
                
                if uploaded_contract_file is not None:
                    bytes_data = uploaded_contract_file.getvalue()
                    content_parts.append({"mime_type": uploaded_contract_file.type, "data": bytes_data})
                
                response = model.generate_content(content_parts)
                st.success("분석이 완료되었습니다!")
                st.write(response.text)
                
                render_save_to_keep_buttons(response.text, "contract_result")
                
            except Exception as e:
                st.error(f"분석 중 오류가 발생했습니다: {e}")

# -------------------------------------------------------------
# 3. AI 기반 상담 프로파일링 (텍스트 & 파일 업로드 지원)
# -------------------------------------------------------------
elif menu == "3. AI 기반 상담 프로파일링":
    st.header("🧠 AI 상담 프로파일링 및 심리 분석")
    st.write("고객과의 대화 내용을 텍스트로 입력하거나, 상담 녹음 파일 및 문서를 업로드하여 심층 분석을 진행하세요.")
    
    client_talk = st.text_area("고객의 발언 또는 상담 내용 직접 입력:")
    uploaded_profile_file = st.file_uploader("상담 녹음 파일 또는 문서 업로드 (오디오, PDF, 텍스트 등)", type=["mp3", "wav", "m4a", "pdf", "txt", "png", "jpg"])
    
    if st.button("고객 속마음 및 대응 전략 분석 시작"):
        if client_talk or uploaded_profile_file:
            with st.spinner("고객의 심리와 최적의 중개 대응 전략을 분석 중..."):
                try:
                    content_parts = []
                    prompt_text = f"""
                    다음은 부동산 고객의 발언 또는 상담 자료입니다. 
                    이를 바탕으로 다음 항목을 전문적으로 분석해 주세요:
                    1. 고객의 숨은 심리 및 니즈 (속마음)
                    2. 거래 성사를 위해 공인중개사가 취해야 할 핵심 대응 전략
                    3. 예상되는 반대 의견 및 방어 화법
                    
                    [직접 입력한 내용]: {client_talk}
                    """
                    content_parts.append(prompt_text)
                    
                    if uploaded_profile_file is not None:
                        bytes_data = uploaded_profile_file.getvalue()
                        content_parts.append({"mime_type": uploaded_profile_file.type, "data": bytes_data})
                    
                    response = model.generate_content(content_parts)
                    st.success("분석 완료!")
                    st.write(response.text)
                    
                    render_save_to_keep_buttons(response.text, "profile_result")
                    
                except Exception as e:
                    st.error(f"분석 중 오류 발생: {e}")
        else:
            st.warning("고객의 발언을 입력하시거나 파일을 업로드해주세요.")

# -------------------------------------------------------------
# 4. 시각화된 매물 관리 시스템
# -------------------------------------------------------------
elif menu == "4. 시각화된 매물 관리":
    st.header("🏢 시각화된 매물 관리")
    uploaded_excel = st.file_uploader("엑셀 파일 업로드 (.xlsx)", type=["xlsx"])
    if uploaded_excel is not None:
        df = pd.read_excel(uploaded_excel)
        st.dataframe(df)
        
        if st.button("AI 매물 데이터 브리핑 생성"):
            with st.spinner("매물 데이터 분석 중..."):
                try:
                    summary_prompt = f"다음 매물 데이터 목록을 분석하여 주요 특징과 주목해야 할 매물을 요약해 줘:\n\n{df.head(10).to_string()}"
                    response = model.generate_content(summary_prompt)
                    st.success("브리핑 생성 완료!")
                    st.write(response.text)
                    
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
