import streamlit as st
import time
import base64
import os
import pandas as pd
import replicate  # 🚨 실제 AI API 통신을 위한 라이브러리

# ==========================================
# 0. 화면 기본 설정
# ==========================================
st.set_page_config(page_title="연애도 결국 호르몬빨? 내 연애 유형 테스트", layout="centered")

# ==========================================
# 1. API 키 설정 (필수!)
# ==========================================
# 발급받으신 Replicate API 키를 아래 따옴표 안에 넣어주세요!
os.environ["REPLICATE_API_TOKEN"] = "r8_YWRmG7YPCMcmjrlwFj0bARuc8khOipx3AA6bN"

# ==========================================
# 2. 배경 이미지 및 CSS 설정 (하얀 박스 완전 투명화)
# ==========================================
def set_background(image_file):
    if os.path.exists(image_file):
        with open(image_file, "rb") as f:
            encoded_string = base64.b64encode(f.read()).decode()
        
        css = f"""
        <style>
        [data-testid="stAppViewContainer"] {{
            background-image: url("data:image/jpeg;base64,{encoded_string}");
            background-size: cover;
            background-position: center;
        }}
        [data-testid="stHeader"] {{
            background-color: transparent;
        }}
        /* 메인 컨테이너 및 스트림릿 내부 모든 블록의 배경을 투명하게 강제 설정 */
        .block-container, div[data-testid="stVerticalBlock"], div[data-testid="stVerticalBlockBorderWrapper"] {{
            background-color: transparent !important;
            box-shadow: none !important;
            border: none !important;
        }}
        /* 컨테이너 상단 여백 조절 */
        .block-container {{
            padding-top: 2rem !important;
        }}
        p, h1, h2, h3, h4, h5, h6, span, label, div {{
            color: #000000 !important;
        }}
        .stRadio > label {{ font-weight: bold; }}
        </style>
        """
        st.markdown(css, unsafe_allow_html=True)

# 배경 사진 파일명
set_background('background.jpg')

# ==========================================
# 3. 질문 데이터셋 구성 
# ==========================================
questions = [
    {"q": "1. 데이트 중 연인이 \"나 요즘 회사(학교) 일 때문에 너무 스트레스 받아...\"라고 할 때 나의 반응은?", "opts": ["\"헐, 무슨 일 있었어? 마음 아프다... 맛있는 거 먹으러 가자.\"", "\"그 사람(일)이 왜 그런대? 일단 이번 주말은 아무 생각 말고 푹 쉬어.\""], "types": ["E", "T"]},
    {"q": "2. 기념일이나 생일 선물을 고를 때, 내가 더 중요하게 생각하는 것은?", "opts": ["연인의 평소 취향, 손편지, 감동적인 서프라이즈", "연인에게 지금 당장 가장 쓸모 있고 필요한 실용적인 아이템"], "types": ["E", "T"]},
    {"q": "3. 연인과 사소한 말다툼이 생겼을 때, 내가 취하는 행동은?", "opts": ["말 안 통하면 눈물부터 나거나 마음이 가라앉을 때까지 대화를 미룸", "\"그래서 뭐가 문제인데?\"라며 그 자리에서 시시비비를 가리고 끝내야 함"], "types": ["E", "T"]},
    {"q": "4. 연인이 나와 어울리지 않는 옷을 입고 와서 \"나 오늘 어때?\"라고 물어본다면?", "opts": ["\"어? 귀엽네! 잘 어울려~\" 일단 기분 좋게 칭찬부터 해준다.", "\"새로운 모습인거 같아. 근데 약간 톤이 안 맞는 듯!\" 솔직하게 피드백한다."], "types": ["E", "T"]},
    {"q": "5. 연인과 사진 찍을 때 내가 더 중요하게 생각하는 건?", "opts": ["분위기, 감성, 표정까지 예쁘게 나오는 무드샷", "각도 오래 잡는 거 귀찮음. 빨리 찍고 자연스러운 게 최고"], "types": ["E", "T"]},
    {"q": "6. 내가 연인에게 사랑받고 있다고 격하게 느끼는 순간은?", "opts": ["\"오늘 고생했어\", \"보고 싶다\" 같은 다정한 말과 따뜻한 포옹을 해줄 때", "내가 가고 싶다던 곳을 기억해서 리드해 주거나, 내 문제를 멋지게 해결해 줄 때"], "types": ["E", "T"]},
    {"q": "7. 연애할 때 내가 자연스럽게 하게 되는 행동은?", "opts": ["상대 반응 하나하나 신경 쓰고 감정 표현 자주 하는 편", "필요한 순간 챙겨주고 행동으로 책임감 보여주는 편"], "types": ["E", "T"]},
    {"q": "8. 내가 꿈꾸는 이상적인 주말 데이트는 어느 쪽?", "opts": ["예쁜 동네 카페에서 도란도란 수다 떨기, 집에서 넷플릭스 보며 맛있는 거 시켜 먹기", "핫플 웨이팅 도전, 페스티벌 가기, 번화가나 액티비티 즐기기"], "types": ["S", "D"]},
    {"q": "9. 첫눈에 반하는 연애 vs 오래 보고 만나는 연애, 나의 현실은?", "opts": ["친구나 아는 사이로 지내다가 스며들듯 좋아지는 편", "찌릿하는 스파크가 튀어야 함. 첫눈에 꽂히면 브레이크 없이 직진"], "types": ["S", "D"]},
    {"q": "10. 연인과 만난 지 1년째 되는 날, 내가 가고 싶은 데이트 장소는?", "opts": ["우리가 처음 만났던 곳이나 자주 가던 단골집에서 추억 회상하기", "한 번도 안 가본 최고급 레스토랑이나 색다른 이색 테마 여행 가기"], "types": ["S", "D"]},
    {"q": "11. 썸 탈 때 밀당(밀고 당기기)에 대한 나의 생각은?", "opts": ["밀당 극혐. 애타는 감정 소모 싫고, 처음부터 확신을 주는 사람이 좋음.", "적당한 밀당은 필수! 답장이 늦게 오면 애가 타면서 오히려 그 사람 생각이 더 남."], "types": ["S", "D"]},
    {"q": "12. 연인과 연락(카톡, 전화)을 주고받을 때 내가 선호하는 방식은?", "opts": ["자주는 안 하더라도 아침, 점심, 저녁 루틴하게 생존 신고하며 안정감을 주는 연락", "티키타카 드립이 잘 맞고, 사진이나 링크를 실시간으로 폭탄 투하하며 텐션 높은 연락"], "types": ["S", "D"]},
    {"q": "13. 연인이 갑자기 “오늘 뭐 하고 싶어?”라고 물어본다면 나는?", "opts": ["“우리 자주 가던 곳 갈까?” 익숙하고 편한 데이트가 좋음", "“새로 생긴 곳 가보자!” 즉흥적으로 새로운 장소 개척하는 게 재밌음"], "types": ["S", "D"]},
    {"q": "14. 연애가 오래 지속됐을 때 내가 더 중요하게 생각하는 건?", "opts": ["서로 편안하고 안정적인 관계 유지, 일상 속 자연스러운 행복", "계속 설레고 새로운 자극이 있는 관계"], "types": ["S", "D"]}
]

# ==========================================
# 4. 프로그램 상태 초기화
# ==========================================
if 'page' not in st.session_state:
    st.session_state.page = 'intro'
if 'idx' not in st.session_state:
    st.session_state.idx = 0
if 'scores' not in st.session_state:
    st.session_state.scores = {"T": 0, "E": 0, "S": 0, "D": 0}
if 'user_photo' not in st.session_state:
    st.session_state.user_photo = None

# ==========================================
# 5. 🚨 진짜 생성형 AI 캐릭터 변환 함수
# ==========================================
def get_maple_character_from_ai(user_image_file, final_type):
    """
    사용자가 올린 사진과 호르몬 결과를 Replicate 서버로 보내서 
    새로운 픽셀 아트 이미지를 생성하여 받아옵니다.
    """
    try:
        api_key = os.environ.get("REPLICATE_API_TOKEN")
        # 실제 입력한 API 키가 아닌 기본 텍스트이거나 키가 없을 경우 차단
        if not api_key or api_key == "여기에_발급받은_API_키를_넣으세요":
            return "API_KEY_MISSING"

        # 사진을 AI가 읽을 수 있도록 변환
        image_bytes = user_image_file.getvalue()
        
        # 호르몬 유형에 맞게 AI에게 내릴 명령어(Prompt) 작성
        if "테스토스테론" in final_type:
            concept = "cool, logical, confident expression"
        else:
            concept = "warm, gentle, emotional expression"
            
        # 메이플스토리 도트 스타일로 그려달라는 핵심 명령어
        prompt_text = f"16-bit pixel art, MapleStory game character style, 2d sprite, white background, {concept}, strictly matching the facial features of the person in the provided image."

        # Replicate의 img2img (사진 기반 재생성) 모델 호출
        output = replicate.run(
            "stability-ai/stable-diffusion-img2img:15a3689ee13b0d2616e98820eca31d4c3abcd36672ff6afce5cb6ef165961dcb",
            input={
                "image": image_bytes,
                "prompt": prompt_text,
                "prompt_strength": 0.7, # 0.7 정도가 원본 사진의 이목구비와 픽셀 아트의 균형이 가장 잘 맞습니다.
                "num_inference_steps": 30,
                "guidance_scale": 7.5
            }
        )
        
        # 완성된 이미지의 URL을 반환
        return output[0]
        
    except Exception as e:
        print(f"API 오류 발생: {e}")
        return None

# ==========================================
# 6. 화면 라우팅 (페이지 이동 로직)
# ==========================================
st.markdown("연애도 결국 호르몬빨? 내 연애 유형 테스트")

# [화면 1] 인트로
if st.session_state.page == 'intro':
    st.markdown("연애 유형 테스트와 나의 캐릭터 보러가기")
    if st.button("검사 시작하기", type="primary", use_container_width=True):
        st.session_state.page = 'quiz'
        st.rerun()

# [화면 2] 퀴즈
elif st.session_state.page == 'quiz':
    q_idx = st.session_state.idx
    q_data = questions[q_idx]
    
    st.markdown(f"### {q_data['q']}")
    selected_option = st.radio("선택지", options=q_data['opts'], index=None, key=f"radio_{q_idx}", label_visibility="collapsed")
    
    if st.button("다음 문항으로 ➔", type="primary"):
        if selected_option is None:
            st.error("⚠️ 답변을 선택해주세요!")
        else:
            sel_idx = q_data['opts'].index(selected_option)
            hormone = q_data['types'][sel_idx]
            st.session_state.scores[hormone] += 1
            
            st.session_state.idx += 1
            if st.session_state.idx >= 14:
                st.session_state.page = 'photo'
            st.rerun()

# [화면 3] 사진 업로드
elif st.session_state.page == 'photo':
    st.markdown("### 📸 수고하셨습니다! 마지막으로 본인의 사진을 올려주세요.")
    st.markdown("올려주신 사진과 검사 결과를 융합하여 **나만의 메이플스토리 AI 캐릭터**를 실시간으로 생성합니다!")
    
    uploaded_file = st.file_uploader("사진을 업로드하세요.", type=["png", "jpg", "jpeg"])
    
    if uploaded_file is not None:
        st.session_state.user_photo = uploaded_file
        st.image(uploaded_file, caption="업로드 완료! 분석을 시작합니다.", width=250)
        
        if st.button("AI 캐릭터 실시간 생성 및 결과 보기", type="primary", use_container_width=True):
            st.session_state.page = 'result'
            st.rerun()

# [화면 4] 최종 결과
elif st.session_state.page == 'result':
    scores = st.session_state.scores
    
    t_v_e = "테스토스테론" if scores["T"] >= scores["E"] else "에스트로겐"
    d_v_s = "도파민" if scores["D"] >= scores["S"] else "세로토닌"
    final_type = f"{t_v_e}형 & {d_v_s}형"
    
    desc = {
        "도파민": "자극 추구, 모험적, 충동적, 열정적", "세로토닌": "안정 추구, 규칙적, 계획적, 전통 중시",
        "테스토스테론": "논리적, 분석적, 경쟁적", "에스트로겐": "공감적, 감성적, 관계 중심적"
    }
    match = "에스트로겐 + 세로토닌형" if t_v_e == "테스토스테론" else "테스토스테론 + 도파민형"
    
    st.markdown(f"##  당신의 유형: {final_type}")
    st.markdown(f"** 왜 이 유형으로 분류되었나요?**\n\n당신은 공감과 이성 사이에서 '{t_v_e}'의 특징이 강하게 나타나며, 연애의 자극과 안정 사이에서 '{d_v_s}'의 성향을 보였습니다.")
    st.markdown(f"** 나의 연애 스타일 특징**\n- **{t_v_e}**: {desc[t_v_e]}\n- **{d_v_s}**: {desc[d_v_s]}")
    st.markdown(f"** 추천 궁합 파트너:** **{match}**\n\n서로의 부족한 점을 보완해 주며 긍정적인 화학 작용을 일으킬 수 있는 최고의 궁합입니다.")
    
    st.divider()
    
    # 두 개의 그래프 분리
    st.markdown("### 내 안의 호르몬 우세 비율")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**1. 이성 vs 공감**")
        st.bar_chart(pd.DataFrame({"점수": [scores["T"], scores["E"]]}, index=["테스토스테론", "에스트로겐"]))
    with col2:
        st.markdown("**2. 자극 vs 안정**")
        st.bar_chart(pd.DataFrame({"점수": [scores["D"], scores["S"]]}, index=["도파민", "세로토닌"]))
    
    st.divider()
    
    # 🚨 AI 캐릭터 실제 생성 호출
    st.markdown("### 🧚 나만의 AI 메이플 캐릭터")
    with st.spinner('생성형 AI가 사진을 분석하여 캐릭터를 그리고 있습니다. (약 10~20초 소요) 🎨'):
        ai_result = get_maple_character_from_ai(st.session_state.user_photo, final_type)
        
        if ai_result == "API_KEY_MISSING":
            st.error("🚨 오류: Replicate API 키가 설정되지 않았습니다. 코드 맨 위 `os.environ[\"REPLICATE_API_TOKEN\"]`에 발급받은 키를 넣어주세요.")
        elif ai_result is not None:
            st.image(ai_result, caption="당신의 특징이 담긴 생성형 AI 메이플 캐릭터!", width=300)
        else:
            st.error("🚨 이미지 생성에 실패했습니다. 올바른 사진 형식인지, API 크레딧이 남아있는지 확인해주세요.")
    
    if st.button("처음부터 다시하기 🔄", use_container_width=True):
        st.session_state.page = 'intro'
        st.session_state.idx = 0
        st.session_state.scores = {"T": 0, "E": 0, "S": 0, "D": 0}
        st.session_state.user_photo = None
        st.rerun()