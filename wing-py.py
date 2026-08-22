import streamlit as st
from google import genai
import pandas as pd
from datetime import datetime, timedelta
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# 1. Streamlit Secrets에서 API 키 안전하게 불러오기
# 1. Streamlit Secrets에서 API 키 안전하게 불러오기
if "GEMINI_API_KEY" in st.secrets:
    API_KEY = st.secrets["GEMINI_API_KEY"]
else:
    st.error("🚨 Streamlit Cloud Secrets에 'GEMINI_API_KEY'가 설정되어 있지 않습니다!")
    st.stop()
  
# 2. 최신 Gemini 클라이언트 초기화
client = genai.Client(api_key=API_KEY)

st.set_page_config(
    page_title="부동산 AI 비서 '날개'", 
    page_icon="🏡", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# -------------------------------------------------------------
# 구글 스프레드시트 연결 함수 (코드 내 직접 통합형)
# -------------------------------------------------------------
def get_google_sheet():
    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive"
    ]
    
    # 본인의 credentials.json 내용을 여기에 넣어두셨거나 파일로 쓰시는 부분입니다.
    # 만약 기존 방식(파일 읽기)을 쓰신다면 ServiceAccountCredentials.from_json_keyfile_name 유지 가능
    try:
        creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
    except:
        # 파일이 없다면 Secrets에 넣어둔 딕셔너리로 대체할 수도 있습니다.
        # 일단 기존처럼 파일을 같은 폴더에 두거나 인증 설정을 유지해주세요.
        pass
    
    # 임시 인증 처리 (만약 credentials.json 파일을 폴더에 두셨다면 아래 코드가 정상 작동합니다)
    creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
    gspread_client = gspread.authorize(creds)
    sheet = gspread_client.open("wing_memo_db").sheet1
    return sheet

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
st.write("올인원 AI 중개 솔루션 (구글 스프레드시트 실시간 영구 연동)")

menu = st.sidebar.selectbox(
    "기능 선택", 
    [
        "1. 계약서 OCR 및 데이터 자동화", 
        "2. 스마트 메모 및 실시간 소통", 
        "3. AI 기반 상담 프로파일링", 
        "4. 시각화된 매물 관리", 
        "5. 일정 관리 및 자동 특약 생성"
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
                    prompt = "이 계약서 이미지에서 매도인, 매수인, 계약일, 중도금, 잔금, 거래 금액을 찾아내어 보기 쉽게 요약해 주고, 법정 중개 보수도 대략적으로 계산해 줘."
                    
                    # 최신 클라이언트 호출 방식
                    response = client.models.generate_content(
                        model='gemini-1.5-flash',
                        contents=[
                            {"mime_type": uploaded_file.type, "data": bytes_data},
                            prompt
                        ]
                    )
                    st.success("분석 완료!")
                    st.write(response.text)
                except Exception as e:
                    st.error(f"오류가 발생했습니다: {e}")

# -------------------------------------------------------------
# 2. 스마트 메모 및 실시간 고객 소통 (구글 시트 연동)
# -------------------------------------------------------------
elif menu == "2. 스마트 메모 및 실시간 소통":
    st.header("📝 스마트 메모 및 구글 시트 영구 저장")
    
    memo_input = st.text_area("상담 내용을 직접 입력하세요")
    
    if st.button("스마트 메모 분석 및 구글 시트 저장"):
        if memo_input:
            with st.spinner("AI 분석 및 구글 스프레드시트 연동 저장 중..."):
                try:
                    prompt_text = f"다음 상담 내용을 분석하여 핵심 키워드 태그와 깔끔한 요약 문구를 작성해 줘:\n\n{memo_input}"
                    
                    # 최신 클라이언트 호출 방식
                    response = client.models.generate_content(
                        model='gemini-1.5-flash',
                        contents=prompt_text
                    )
                    ai_result = response.text
                    
                    st.success("메모 분석 완료!")
                    st.write(ai_result)
                    
                    # 구글 스프레드시트에 저장
                    sheet = get_google_sheet()
                    now_time = datetime.now().strftime("%Y-%m-%d %H:%M")
                    sheet.append_row([now_time, memo_input, ai_result])
                    st.success("☁️ 구글 스프레드시트에 실시간 영구 저장되었습니다!")
                    
                except Exception as e:
                    st.error(f"저장 중 오류가 발생했습니다: {e}")
        else:
            st.warning("상담 내용을 입력해주세요.")
            
    st.write("---")
    st.subheader("📚 구글 스프레드시트 연동 목록")
    try:
        sheet = get_google_sheet()
        data = sheet.get_all_records()
        if data:
            df = pd.DataFrame(data)
            st.dataframe(df, use_container_width=True)
        else:
            st.info("구글 시트에 아직 기록된 데이터가 없습니다.")
    except Exception as e:
        st.warning("구글 스프레드시트 연동 대기 중입니다.")

# -------------------------------------------------------------
# 3. AI 기반 상담 프로파일링
# -------------------------------------------------------------
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
                    
                    # 최신 클라이언트 호출 방식 적용
                    response = client.models.generate_content(
                        model='gemini-1.5-flash',
                        contents=prompt
                    )
                    
                    st.success("분석 완료!")
                    st.write(response.text)
                except Exception as e:
                    st.error(f"분석 중 오류가 발생했습니다: {e}")
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
# 5. 일정 관리 및 자동 특약 생성
# -------------------------------------------------------------
elif menu == "5. 일정 관리 및 자동 특약 생성":
    st.header("📅 일정 및 특약 생성")
    property_info = st.text_input("특이사항 입력")
    if st.button("특약 생성"):
        if property_info:
            response = client.models.generate_content(
                model='gemini-1.5-flash',
                contents=f"안전한 부동산 특약 조항 작성해 줘: {property_info}"
            )
            st.write(response.text)
