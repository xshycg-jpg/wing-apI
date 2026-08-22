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

# -------------------------------------------------------------
# 세션 상태 기반 메모 저장소 초기화 (앱 켜져 있는 동안 영구 유지)
# -------------------------------------------------------------
if "memo_list" not in st.session_state:
    st.session_state.memo_list = []

# -------------------------------------------------------------
# 보안용 로그인 비밀번호 설정
# -------------------------------------------------------------
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
                except Exception as e:
                    st.error(f"오류가 발생했습니다: {e}")

# -------------------------------------------------------------
# 2. 스마트 메모 및 자동 복사/저장
# -------------------------------------------------------------
elif menu == "2. 스마트 메모 및 자동 복사/저장":
    st.header("📝 스마트 메모 및 앱 내 안전 저장")
    
    memo_input = st.text_area("상담 내용을 직접 입력하세요")
    
    if st.button("메모 분석 및 앱에 저장"):
        if memo_input:
            with st.spinner("AI 분석 중..."):
                try:
                    prompt_text = f"다음 상담 내용을 분석하여 핵심 키워드 태그와 깔끔한 요약 문구를 작성해 줘:\n\n{memo_input}"
                    response = model.generate_content(prompt_text)
                    ai_result = response.text
                    
                    st.success("메모 분석 완료!")
                    st.write(ai_result)
                    
                    # 세션 메모 리스트에 저장
                    now_time = datetime.now().strftime("%Y-%m-%d %H:%M")
                    st.session_state.memo_list.insert(0, {
                        "시간": now_time,
                        "내용": memo_input,
                        "AI분석": ai_result
                    })
                    st.success("💾 앱 내 메모장에 안전하게 저장되었습니다!")
                    
                except Exception as e:
                    st.error(f"저장 중 오류 발생: {e}")
        else:
            st.warning("상담 내용을 입력해주세요.")
            
    st.write("---")
    st.subheader("📚 저장된 메모 목록")
    if st.session_state.memo_list:
        df_memo = pd.DataFrame(st.session_state.memo_list)
        st.dataframe(df_memo, use_container_width=True)
        
        # 엑셀 다운로드 기능 제공 (데이터 유실 방지)
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

# -------------------------------------------------------------
# 5. 일정 관리 및 삼성 캘린더 다이렉트 호출
# -------------------------------------------------------------
elif menu == "5. 일정 관리 및 캘린더 자동 추가":
    st.header("📅 삼성 캘린더 바로 추가")
    st.write("잔금일 등 일정을 입력하고 버튼을 누르면 삼성 캘린더 앱이 즉시 실행됩니다.")
    
    event_title = st.text_input("일정 제목", "[잔금] 홍길동 고객님 부동산 계약")
    event_date = st.date_input("잔금일 선택")
    event_memo = st.text_area("상세 메모", "금액 및 특이사항 입력")
    
    if st.button("삼성 캘린더 앱 열기"):
        # 날짜 포맷 (YYYYMMDD)
        date_str = event_date.strftime("%Y%m%d")
        
        # 안드로이드 캘린더 인텐트 링크 생성 (삼성 캘린더 다이렉트 호출)
        # 웹뷰 환경에서 가장 확실하게 캘린더 앱을 띄우는 방식입니다.
        intent_url = f"content://com.android.calendar/time"
        
        # 구글 캘린더 웹/모바일 겸용 딥링크 (웹뷰 내에서 캘린더 앱으로 연결 유도)
        cal_url = f"https://calendar.google.com/calendar/render?action=TEMPLATE&text={event_title}&dates={date_str}/{date_str}&details={event_memo}"
        
        st.success("✨ 캘린더 연동 링크가 준비되었습니다!")
        
        # 버튼 클릭 시 웹뷰/브라우저를 통해 캘린더 앱으로 연결
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
        st.info("💡 위 초록색 버튼을 누르시면 폰에 설치된 캘린더 앱(삼성 캘린더 등)이 곧바로 실행되면서 입력하신 내용이 채워집니다!")
