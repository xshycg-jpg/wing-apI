import streamlit as st
import google.generativeai as genai
import pandas as pd
from datetime import datetime, timedelta
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# API 키 설정
API_KEY = "AQ.Ab8RN6LFSnIh3HNAaP8ggx6qVhn6EJGq6Gu-336G2I-OiAXc4g"
genai.configure(api_key=API_KEY)

# Gemini 모델 설정
model = genai.GenerativeModel('gemini-3.6-flash') # type: ignore

st.set_page_config(
    page_title="부동산 AI 비서 '날개'", 
    page_icon="🏡", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# -------------------------------------------------------------
# 구글 스프레드시트 연결 함수 (인증 내용을 코드 안에 직접 통합)
# -------------------------------------------------------------
def get_google_sheet():
    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive"
    ]
    
    # 💡 여기에 기존 credentials.json 파일 내용을 통째로 넣어두었습니다.
    # (따로 JSON 파일을 둘 필요가 없습니다!)
    credentials_dict = {
        "type": "service_account",
        "project_id": "wing-project-506315",
        "private_key_id": "52ac1079994edbecc943ce7b81de36f42d0503c2",
        "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQC8B6u507epAEB5\n5zPXX+5vA5Ckl3Cn0sRSbLX4dh2KWYeXeSGpsKU1eOomtWDQKwWEnlPIqSzAnbDO\n+N1RVFZopBFrmwEelPtpl7V2kXN+rmPOSwpCfAq0PbvSfMwVGIGpxBAIW8eq7EWh\nP9PAgpzQvU4ma8mqMQrmV2abfjmJbfwG4juPb5a3or+pgVQv/C5mVWFQUlWjb8aE\nJMgcrePw9VHiyXHQ7GjpHDo2XLP9s7nXKGB10ot9lgT9LEp2WXAnoe7oaHb6N/sv\nLUM7iXdfJP6kHf6iTN7kbhlkiz3QUm9vAPxRYe3m+Q+I87eBDvyHQXxftcB4ztxh\nE1p5fxD/AgMBAAECggEABci2n6DDpY88bIOQNK/exct2R5ng/UiegWqWrm3zuq3G\nXgJ75pxoeJyfl1E9CSpJoSq9qQ6LMeGn7rX5GOdfQRjK8GR0RFyQ306rZlpTEzKK\nH25vglwOeDzt6iusm3mFg5Nkat1n5vodqjgsa1+ZM1KfdM8cBQA9NZi6r03St0d9\nVnTJ2OrH8B/9Bt2F0SYDQP8ixLZ/HpuUTfQQIO+ynd8Y/kCKeZxEstXz1FVwGr8U\nfRPKrVTU4oJMsipPNe27GenOq5+l3G3l6d5Z0s8hZlHkHljrZLBbM0EAbG7UQzA8\nSwGYv10reJrCVQ8dYpbeOGd/0AOGtNwiAreonWE2AQKBgQDlG7nsjYMbDAkU/ntw\nnY/+cEpWwL5rGjCR9v9w096ZQTQ3sBlyNmKCVEQSGwpQVpa/KIqnMrfSALqghRbZ\niLrH0ehJjpGYPRskGW6M7ksqZSIbqW209HxMxaq002qyU95dg59TH3mxctn76LC5\nLsuaHCCIWmF5GC5wXMwA270KtwKBgQDSGZ4cgVYGedTy8MtjvZ5sBf5fZ8xRgcsG\npHbatovK/sZTbGW/VJpekXXJVxjv0eIn3lOYnJBIzz8MiXrajHv8so/rxbxE0vwI\n5HEJdL3EKFLUugyC3x3KjPW4MbreiBKcrrJ0P2DD2Ork60CmvWfaYkaDUhyRfLXm\nEUXpOvyD+QKBgD9K5pUkDvkU3RlwqDdXP+VhrhfDTZeW954LZ0wLK+6Ypc1Ql+cG\ngTZSAzAhSjshgKm0kIFaMJASZXxc6BAWhssXAR35Bd3R28KgR/slBZzjrYWIy+b2\nt7QZ02v7D/nN05tv9j7nbh4IhZHjGZc/Bz4+0Pn6Rf1HIeUmrbD7A4GHAoGBALpJ\nhpzlvN3/FmbWRLDKR3amldYIFezLNbZNCymAJFE4N6dufIT6QenJ9fMw6+ZwZaNO\nCTdO0swMHm5CVBEF8UWtGdlGuVkY7eoAi42D2mLcEh2WXVOI+0RGWfUY+wUnB8Gv\nUIGsVGMyqYuSX/+3/yZubvEvVC9XsX0uIZvb9lwZAoGAapYW5SdqW2QwLqBptkd3\nLLM7+ig+DhZ+F9MQAyQUvIGIulymJjwGys5U2eNXVVgtDsZOovU9X+W/uphZP1Ei\ngvbm1k5fUgVkNM998lwNND5BN/98Zw4PjV60A1CKHreWr0BfCqAUBcm66iOCcPj6\ncuLL4G1shkpDhV+j6yH8Vlg=\n-----END PRIVATE KEY-----\n",
        "client_email": "wing-33@wing-project-506315.iam.gserviceaccount.com",
        "client_id": "109482003546462320195",
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/wing-33%40wing-project-506315.iam.gserviceaccount.com",
  "universe_domain": "googleapis.com"
    }
    
    creds = ServiceAccountCredentials.from_json_keyfile_dict(credentials_dict, scope)
    client = gspread.authorize(creds)
    sheet = client.open("wing_memo_db").sheet1
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
        if password_input == "1128":  # 설정하신 비밀번호
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error("비밀번호가 틀렸습니다!")
    st.stop()

# -------------------------------------------------------------
# 메인 프로그램 시작 (로그인 성공 후)
# -------------------------------------------------------------
st.title("🏡 부동산 AI 비서 '날개'")
st.write("올인원 AI 중개 솔루션 (구글 스프레드시트 실시간 영구 연동)")

# 사이드바 메뉴
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
    st.write("계약서 이미지나 PDF를 업로드하면 Gemini AI가 핵심 데이터를 추출합니다.")
    
    uploaded_file = st.file_uploader("계약서 파일을 업로드하세요", type=["png", "jpg", "jpeg", "pdf"])
    
    if uploaded_file is not None:
        st.image(uploaded_file, caption="업로드된 계약서", use_container_width=True)
        if st.button("AI OCR 분석 시작"):
            with st.spinner("AI가 계약서 분석 중..."):
                try:
                    bytes_data = uploaded_file.getvalue()
                    image_part = {
                        "mime_type": uploaded_file.type,
                        "data": bytes_data
                    }
                    
                    prompt = "이 계약서 이미지에서 매도인, 매수인, 계약일, 중도금, 잔금, 거래 금액을 찾아내어 보기 쉽게 요약해 주고, 법정 중개 보수도 대략적으로 계산해 줘."
                    response = model.generate_content([image_part, prompt])
                    
                    st.success("분석 완료!")
                    st.write(response.text)
                except Exception as e:
                    st.error(f"오류가 발생했습니다: {e}")

# -------------------------------------------------------------
# 2. 스마트 메모 및 실시간 고객 소통 (구글 시트 연동)
# -------------------------------------------------------------
elif menu == "2. 스마트 메모 및 실시간 소통":
    st.header("📝 스마트 메모, 통화녹음 및 구글 시트 영구 저장")
    st.write("상담 내용이나 녹음/이미지를 분석하면 **내 구글 스프레드시트에 실시간으로 기록**됩니다.")
    
    memo_input = st.text_area("상담 내용을 직접 입력하세요 (선택 사항)")
    uploaded_memo_file = st.file_uploader("통화 녹음 파일 또는 메모 이미지를 업로드하세요", type=["mp3", "wav", "m4a", "png", "jpg", "jpeg"])
    
    if uploaded_memo_file is not None:
        st.info(f"업로드된 파일: {uploaded_memo_file.name}")

    if st.button("스마트 메모 분석 및 구글 시트 저장"):
        if memo_input or uploaded_memo_file:
            with st.spinner("AI 분석 및 구글 스프레드시트 연동 저장 중..."):
                try:
                    contents = []
                    if uploaded_memo_file is not None:
                        file_bytes = uploaded_memo_file.getvalue()
                        contents.append({
                            "mime_type": uploaded_memo_file.type,
                            "data": file_bytes
                        })
                    
                    prompt_text = f"""
                    다음 상담 자료(텍스트 및 첨부된 녹음/이미지)를 분석하여 아래 형태로 정리해 줘:
                    1. 핵심 키워드 태그 (쉼표로 구분)
                    2. 고객에게 공유할 깔끔한 요약 및 안내 문구
                    
                    [추가 텍스트 메모]: {memo_input}
                    """
                    contents.append(prompt_text)
                    
                    response = model.generate_content(contents)
                    ai_result = response.text
                    
                    st.success("메모 분석 완료!")
                    st.write("**[AI 분석 및 요약]**")
                    st.write(ai_result)
                    st.info("🔗 고객 공유용 링크: https://wing-prop.ai/share/sample-link-1234 (시뮬레이션)")
                    
                    # 구글 스프레드시트에 데이터 행 추가하기
                    sheet = get_google_sheet()
                    now_time = datetime.now().strftime("%Y-%m-%d %H:%M")
                    content_text = memo_input if memo_input else "(파일 첨부 상담)"
                    
                    sheet.append_row([now_time, content_text, ai_result])
                    st.success("☁️ 구글 스프레드시트에 실시간 영구 저장되었습니다!")
                    
                except Exception as e:
                    st.error(f"저장 중 오류가 발생했습니다 (코드 내 인증 정보를 확인해주세요): {e}")
        else:
            st.warning("텍스트 메모를 입력하시거나 파일을 업로드해주세요.")
            
    # 구글 시트에 저장된 내용 불러와서 보여주기
    st.write("---")
    st.subheader("📚 구글 스프레드시트 실시간 연동 목록")
    try:
        sheet = get_google_sheet()
        data = sheet.get_all_records()
        if data:
            df = pd.DataFrame(data)
            st.dataframe(df, use_container_width=True)
        else:
            st.info("구글 시트에 아직 기록된 데이터가 없습니다.")
    except Exception as e:
        st.warning("구글 스프레드시트 연동 대기 중입니다. (인증 정보 설정 필요)")

# -------------------------------------------------------------
# 3. AI 기반 상담 프로파일링
# -------------------------------------------------------------
elif menu == "3. AI 기반 상담 프로파일링":
    st.header("🧠 AI 상담 프로파일링 (속마음 분석)")
    st.write("고객의 숨은 의도와 계약 체결 전략을 파악합니다.")
    
    client_talk = st.text_area("고객의 통화 내용, 말투, 반응 등을 상세히 입력하세요:")
    
    if st.button("고객 속마음 및 대응 전략 분석"):
        if client_talk:
            with st.spinner("고객 심리 분석 중..."):
                prompt = f"""
                당신은 최고급 부동산 수석 협상가이자 심리 분석가입니다. 아래 고객의 발언을 분석해주세요.
                1. 고객의 '암묵적 기대(속마음)' 분석
                2. 계약 체결 확률 및 리스크 요인 파악
                3. 중개사가 취해야 할 구체적인 대응 전략
                
                고객 발언: {client_talk}
                """
                response = model.generate_content(prompt)
                st.success("분석 완료!")
                st.write(response.text)
        else:
            st.warning("고객의 발언을 입력해주세요.")

# -------------------------------------------------------------
# 4. 시각화된 매물 관리 시스템
# -------------------------------------------------------------
elif menu == "4. 시각화된 매물 관리":
    st.header("🏢 시각화된 매물 관리 및 엑셀 연동")
    st.write("사용 중이신 엑셀 매물장 파일을 업로드하여 데이터를 실시간으로 관리하세요.")
    
    uploaded_excel = st.file_uploader("기존 엑셀 매물장 파일 업로드 (.xlsx)", type=["xlsx"])
    
    if uploaded_excel is not None:
        try:
            df = pd.read_excel(uploaded_excel)
            st.success("엑셀 파일 연동 성공!")
            st.dataframe(df)
        except Exception as e:
            st.error(f"엑셀 파일을 읽는 중 오류가 발생했습니다: {e}")
    else:
        st.info("👆 파일을 업로드하면 엑셀 매물장이 화면에 표시됩니다.")

# -------------------------------------------------------------
# 5. 일정 관리 및 자동 특약 생성
# -------------------------------------------------------------
elif menu == "5. 일정 관리 및 자동 특약 생성":
    st.header("📅 지능형 일정 관리 및 특약 자동 생성")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("지능형 캘린더 / 일정 설정")
        contract_date = st.date_input("계약일 선택", datetime.now())
        
        default_balance_date = contract_date + timedelta(days=30)
        balance_date = st.date_input("잔금일 선택", default_balance_date)
        
        st.write("---")
        st.write(f"📌 **계약일:** {contract_date}")
        st.write(f"📌 **잔금일:** {balance_date}")
        
        period_days = (balance_date - contract_date).days
        st.info(f"💡 계약일부터 잔금일까지 총 **{period_days}일** 남았습니다.")
        st.write("⏰ **중요 일정 알림:** 잔금일 기준 주요 신고 기한 및 알림 대기 중")
        
    with col2:
        st.subheader("특약 문구 자동 생성")
        property_info = st.text_input("등기부등본 특이사항 입력 (예: 근저당 설정 있음, 임차인 있음 등)")
        if st.button("안전한 특약 문구 생성"):
            if property_info:
                prompt = f"부동산 계약 시 법적 분쟁을 막고 중개사의 책임을 방어할 수 있는 안전한 특약 조항 문구를 작성해 줘. 조건: {property_info}"
                response = model.generate_content(prompt)
                st.success("특약 문구 생성 완료!")
                st.write(response.text)
            else:
                st.warning("특이사항을 입력해주세요.")
