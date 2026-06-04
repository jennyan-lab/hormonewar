import streamlit as st
import time
import base64
import os
import pandas as pd
import replicate

# ==========================================
# 0. 화면 기본 설정
# ==========================================
# ⭐️ 브라우저 탭 제목에 요청하신 줄바꿈(\n)을 확실하게 반영했습니다.
st.set_page_config(page_title="연애도 결국 호르몬빨? 내 연애 유형\n테스트", layout="centered")

# ==========================================
# 1. API 키 설정 (필수!)
# ==========================================
os.environ["REPLICATE_API_TOKEN"] = "r8_YWRmG7YPCMcmjrlwFj0bARuc8khOipx3AA6bN"

# ==========================================
# 2. 프로그램 상태 초기화
# ==========================================
if 'page' not in st.session_state:
    st.session_state.page = 'intro'
if 'idx' not in st.session_state:
    st.session_state.idx = 0
if 'scores' not in st.session_state:
    st.session_state.scores = {"T": 0, "E": 0, "S": 0, "D": 0}
if 'history' not in st.session_state:
    st.session_state.history = [] 
if 'user_photo' not in st.session_state:
    st.session_state.user_photo = None

# ==========================================
# 3. 배경, 폰트 및 메신저 레이아웃 강제 맞춤
# ==========================================
def set_background_and_font(image_filename, font_filename):
    current_dir = os.path.dirname(os.path.abspath(__file__))
    image_path = os.path.join(current_dir, image_filename)
    font_path = os.path.join(current_dir, font_filename)
    
    if os.path.exists(image_path):
        with open(image_path, "rb") as f:
            img_encoded = base64.b64encode(f.read()).decode()
    else:
        st.error(f"⚠️ 이미지를 찾을 수 없습니다: {image_filename}")
        return

    if os.path.exists(font_path):
        with open(font_path, "rb") as f:
            font_encoded = base64.b64encode(f.read()).decode()
    else:
        st.error(f"⚠️ 폰트 파일을 찾을 수 없습니다: {font_filename}")
        return
        
    css = f"""
    <style>
    @font-face {{
        font-family: 'MyCustomFont';
        src: url(data:font/ttf;charset=utf-8;base64,{font_encoded}) format('truetype');
    }}
    
    html, body, [class*="css"], .block-container * {{
        font-family: 'MyCustomFont', sans-serif !important;
        text-align: center !important; 
    }}

    .block-container {{
        padding-top: 18vh !important; 
        padding-bottom: 18vh !important; 
    }}

    div.block-container > div:first-child > div[data-testid="stVerticalBlock"] {{
        background-color: rgba(255, 235, 240, 0.9) !important; 
        padding: 30px !important;
        border-radius: 20px !important;
    }}

    .stRadio > div[role="radiogroup"] {{
        display: flex;
        flex-direction: column;
        align-items: center; 
        gap: 15px; 
    }}
    .stRadio > div[role="radiogroup"] > label {{
        width: 100%;
        background-color: rgba(255, 255, 255, 0.6); 
        padding: 15px 20px !important; 
        border-radius: 15px;
        margin-bottom: 5px !important;
        justify-content: flex-start !important; 
    }}
    .stRadio > div[role="radiogroup"] > label div {{
        text-align: left !important; 
    }}
    .stRadio > label {{ display: none; }} 

    [data-testid="stAppViewContainer"] {{
        background-image: url("data:image/jpeg;base64,{img_encoded}");
        background-size: 100% 100%; 
        background-position: center top;
        background-attachment: fixed; 
    }}
    
    [data-testid="stHeader"] {{ background-color: transparent; }}
    div[data-testid="stVerticalBlock"], div[data-testid="stVerticalBlockBorderWrapper"] {{
        background-color: transparent !important;
        box-shadow: none !important;
        border: none !important;
    }}
    p, h1, h2, h3, h4, h5, h6, span, label, div {{
        color: #000000 !important;
    }}

    div.stButton {{
        position: fixed !important;
        bottom: 7.5vh !important; 
        left: 18vw !important; 
        width: 78vw !important; 
        z-index: 9999 !important; 
    }}
    
    div[data-testid="column"]:nth-child(1) div.stButton,
    div[data-testid="stColumn"]:nth-child(1) div.stButton {{
        left: 18vw !important;
        width: 38vw !important;
    }}
    div[data-testid="column"]:nth-child(2) div.stButton,
    div[data-testid="stColumn"]:nth-child(2) div.stButton {{
        left: 58vw !important;
        width: 38vw !important;
    }}

    div.stButton > button {{
        width: 100% !important;
        height: 8vh !important; 
        background-color: transparent !important;
        border: none !important;
        box-shadow: none !important;
        color: #000000 !important;
        font-weight: bold !important;
        font-size: 20px !important;
        padding: 10px 0 !important;
        display: flex;
        justify-content: center;
        align-items: center;
    }}
    div.stButton > button:hover {{ color: #777777 !important; }}
    div.stButton > button:active, div.stButton > button:focus {{ color: #000000 !important; }}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

# 페이지별 배경 이미지 동적 적용
if st.session_state.page in ['photo', 'result']:
    current_bg = 'background.png'
else:
    current_bg = 'background3.jpg'

set_background_and_font(current_bg, 'x12y12pxMaruMinyaHangul.ttf')

# ==========================================
# 4. 질문 데이터셋 구성 
# ==========================================
questions = [
    {"q": "1. 데이트 중 연인이 \"나 요즘 회사(학교) 일 때문에 너무 스트레스 받아...\"라고 할 때 나의 반응은?", "opts": ["\"헐, 무슨 일 있었어? 마음 아프다... 맛있는 거 먹으러 가자.\"", "\"그 사람(일)이 왜 그런대? 일단 이번 주말은 아무 생각 말고 푹 쉬어.\""], "types": ["E", "T"]},
    {"q": "2. 기념일이나 생일 선물을 고를 때, 내가 더 중요하게 생각하는 것은?", "opts": ["연인의 평소 취향, 손편지, 감동적인 서프라이즈", "연인에게 지금 당장 가장 쓸모 있고 필요한 실용적인 아이템"], "types": ["E", "T"]},
    {"q": "3. 연인과 사소한 말다툼이 생겼을 때, 내가 취하는 행동은?", "opts": ["말 안 통하면 눈물부터 나거나 마음이 가라앉을 때까지 대화를 미룸", "\"그래서 뭐가 문제인데?\"라며 그 자리에서 시시비비를 가리고 끝내야 함"], "types": ["E", "T"]},
    {"q": "4. 연인이 나와 어울리지 않는 옷을 입고 와서 \"나 오늘 어때?\"라고 물어본다면?", "opts": ["\"어? 귀엽네! 잘 어울려~\" 일단 기분 좋게 칭찬부터 해준다.", "\"새로운 모습인거 같아. 근데 약간 톤이 안 맞는 듯!\" 솔직하게 피드백한다."], "types": ["E", "T"]},
    {"q": "5. 연인과 사진 찍을 때 내가 더 중요하게 생각하는 건?", "opts": ["분위기, 감성, 표정까지 예쁘게 나오는 무드샷", "각도 오래 잡는 거 귀찮음. 빨리 찍고 자연스러운 게 최고"], "types": ["E", "T"]},
    {"q": "6. 내가 연인에게 사랑받고 있다고 격하게 느끼는 순간은?", "opts": ["\"오늘 고생했어\", \"보고 싶다\" 같은 다정한 말 and 따뜻한 포옹을 해줄 때", "내가 가고 싶다던 곳을 기억해서 리드해 주거나, 내 문제를 멋지게 해결해 줄 때"], "types": ["E", "T"]},
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
# 5. 생성형 AI 캐릭터 변환 함수
# ==========================================
def get_maple_character_from_ai(user_image_file, final_type):
    try:
        api_key = os.environ.get("REPLICATE_API_TOKEN")
        if not api_key or api_key == "여기에_발급받은_API_키를_넣으세요":
            return "API_KEY_MISSING"

        image_bytes = user_image_file.getvalue()
        
        if "테토" in final_type:
            concept = "cool, logical, confident expression"
        else:
            concept = "warm, gentle, emotional expression"
            
        prompt_text = f"16-bit pixel art, MapleStory game character style, 2d sprite, white background, {concept}, strictly matching the facial features of the person in the provided image."

        output = replicate.run(
            "stability-ai/stable-diffusion-img2img:15a3689ee13b0d2616e98820eca31d4c3abcd36672ff6afce5cb6ef165961dcb",
            input={
                "image": image_bytes,
                "prompt": prompt_text,
                "prompt_strength": 0.7, 
                "num_inference_steps": 30,
                "guidance_scale": 7.5
            }
        )
        return output[0]
        
    except Exception as e:
        print(f"API 오류 발생: {e}")
        return None

# ==========================================
# 6. 화면 라우팅
# ==========================================
# [화면 1] 인트로
if st.session_state.page == 'intro':
    # ⭐️ 실제 화면상의 메인 제목 글씨도 완벽하게 엔터(<br>) 처리가 되도록 반영했습니다.
    st.markdown("""
    <div style="font-size: 30px; font-weight: bold; margin-bottom: 10px;">연애도 결국 호르몬빨?</div>
    <div style="font-size: 40px; font-weight: bold; margin-bottom: 30px;">내 연애<br>유형 테스트</div>
    <div style="font-size: 18px; color: #333333;">나의 연애 유형 테스트 보러가기</div>
    """, unsafe_allow_html=True)
    
    st.write("") 
    if st.button("검사 시작하기", type="primary", use_container_width=True):
        st.session_state.page = 'quiz'
        st.rerun()

# [화면 2] 퀴즈
elif st.session_state.page == 'quiz':
    q_idx = st.session_state.idx
    q_data = questions[q_idx]
    
    st.markdown(f"### {q_data['q']}")
    st.write("") 
    
    selected_option = st.radio("선택지", options=q_data['opts'], index=None, key=f"radio_{q_idx}", label_visibility="collapsed")
    
    col1, col2 = st.columns(2)
    with col1:
        prev_clicked = st.button("◀ 이전 문항", use_container_width=True)
    with col2:
        next_clicked = st.button("다음 문항 ▶", use_container_width=True)
        
    if prev_clicked:
        if st.session_state.idx > 0:
            last_hormone = st.session_state.history.pop() 
            st.session_state.scores[last_hormone] -= 1
            st.session_state.idx -= 1
        else:
            st.session_state.page = 'intro'
        st.rerun()
        
    if next_clicked:
        if selected_option is None:
            st.error("⚠️ 답변을 선택해주세요!")
        else:
            sel_idx = q_data['opts'].index(selected_option)
            hormone = q_data['types'][sel_idx]
            st.session_state.history.append(hormone) 
            st.session_state.scores[hormone] += 1
            
            st.session_state.idx += 1
            if st.session_state.idx >= 14:
                st.session_state.page = 'photo'
            st.rerun()

# [화면 3] 사진 업로드
elif st.session_state.page == 'photo':
    st.markdown("### 📸 수고하셨습니다!")
    st.markdown("마지막으로 본인의 사진을 올려주세요.\n\n올려주신 사진과 결과를 융합하여 **나만의 메이플 AI 캐릭터**를 생성합니다!")
    
    uploaded_file = st.file_uploader("사진을 업로드하세요.", type=["png", "jpg", "jpeg"])
    if uploaded_file is not None:
        st.image(uploaded_file, caption="업로드 완료! 분석을 준비합니다.", width=250)
        
    col1, col2 = st.columns(2)
    with col1:
        skip_clicked = st.button("사진 넣지 않기", use_container_width=True)
    with col2:
        result_clicked = st.button("결과 보기 ▶", use_container_width=True)
        
    if skip_clicked:
        st.session_state.user_photo = None 
        st.session_state.page = 'result'
        st.rerun()
        
    if result_clicked:
        if uploaded_file is None:
            st.error("⚠️ 사진을 업로드하거나 '사진 넣지 않기' 버튼을 눌러주세요.")
        else:
            st.session_state.user_photo = uploaded_file
            st.session_state.page = 'result'
            st.rerun()

# [화면 4] 최종 결과
elif st.session_state.page == 'result':
    scores = st.session_state.scores
    
    t_v_e = "테스토스테론" if scores["T"] >= scores["E"] else "에스트로겐"
    d_v_s = "도파민" if scores["D"] >= scores["S"] else "세로토닌"
    
    if t_v_e == "에스트로겐" and d_v_s == "도파민":
        large_title = "감성로맨티스트형"
        small_desc = "에겐 & 도파민"
        style_text = """당신은 사랑에 빠지면 누구보다 진심이 되는 사람입니다. 상대방과의 대화, 추억, 감정 하나하나를 소중하게 여기며 연애 속에서 행복과 설렘을 찾는 타입이에요. 

공감 능력이 뛰어나 상대방의 감정을 잘 읽고 배려하지만, 동시에 연애에서의 설렘과 두근거림도 중요하게 생각합니다. 그래서 권태로운 관계보다는 서로에게 계속 새로운 자극을 줄 수 있는 관계를 선호해요.

다만 상대에게 너무 많은 감정을 쏟다 보면 혼자 기대가 커지거나 상처를 받는 경우도 있습니다. 가끔은 상대를 있는 그대로 바라보는 여유도 필요해요."""
        match = "테토 + 세로토닌형 (인생동반자형)"
        
    elif t_v_e == "테스토스테론" and d_v_s == "도파민":
        large_title = "심쿵 직진로맨서형"
        small_desc = "테토 & 도파민"
        style_text = """당신은 연애에서도 목표가 생기면 망설이지 않고 행동하는 사람입니다.
 
좋아하는 사람이 생기면 계산하기보다 먼저 다가가고, 애매한 관계를 오래 끌지 않는 편이에요. 상대방의 마음을 확인하기 위해 시간을 낭비하기보다는 직접 표현하는 것을 선호합니다.

새로운 경험을 좋아하는 도파민 성향과 자신감 있는 테스토스테론 성향이 만나 강한 추진력을 만들어냅니다. 그래서 연애 초반에는 굉장히 매력적으로 보이는 경우가 많아요.

다만 감정보다 행동이 앞설 때가 있어 상대방이 부담을 느끼기도 합니다. 때로는 속도를 조절하며 상대의 감정을 살펴보는 것도 중요합니다."""
        match = "에겐 + 세로토닌형 (다정한 집착형)"
        
    elif t_v_e == "에스트로겐" and d_v_s == "세로토닌":
        large_title = "인간 전기장판형"
        small_desc = "에겐 & 세로토닌"
        style_text = """당신은 누군가를 좋아하게 되면 단순한 호감 이상의 의미를 찾는 사람이에요. 함께 있으면 편안한지, 진심으로 마음을 나눌 수 있는지, 오래 곁에 있을 수 있는지를 중요하게 생각합니다.

좋아하는 사람에게 쉽게 마음을 열지는 않지만, 한번 관계를 시작하면 깊고 오래 사랑하는 편이에요. 상대방의 마음을 세심하게 살피고 배려하는 능력이 뛰어나며, 다툼이 생겨도 대화를 통해 해결하려고 합니다.

연애를 단순한 감정 놀이가 아니라 함께 성장하는 관계로 바라보는 경우가 많습니다. 그래서 가벼운 만남보다는 진지한 관계를 선호하는 편이에요.

다만 상대방을 너무 이해하려고 하다가 자신의 감정을 뒤로 미루는 경우가 있습니다. 때로는 자신의 마음도 솔직하게 표현할 필요가 있습니다."""
        match = "테토 + 도파민형 (심쿵 직진로맨서형)"
        
    else: # 테스토스테론 & 세로토닌
        large_title = "인생동반자형"
        small_desc = "테토 & 세로토닌"
        style_text = """당신에게 연애는 단순히 설레는 감정을 나누는 것이 아니라 함께 미래를 만들어 가는 과정에 가깝습니다. 누군가를 좋아하게 되더라도 신중하게 관계를 시작하며, 한번 시작한 관계는 책임감 있게 이어가려고 노력해요.

누군가를 좋아하게 되더라도 신중하게 판단하며, 관계가 시작되면 책임감 있게 상대를 대합니다. 순간의 감정보다 서로의 가치관과 미래를 중요하게 생각하는 편이에요.

주변 사람들에게는 다소 무뚝뚝해 보일 수 있지만, 실제로는 자신이 아끼는 사람을 오래 챙기는 유형입니다. 연애 상대에게 안정감과 신뢰를 주며, 어려운 상황에서도 쉽게 포기하지 않습니다.

다만 감정을 표현하는 데 서툴러 상대방이 사랑받고 있다는 확신을 얻지 못할 수도 있습니다. 가끔은 마음을 말로 표현하는 연습도 필요합니다."""
        match = "에겐 + 도파민형 (플러팅 천재형)"

    st.markdown("## 당신의 연애 유형")
    st.markdown(f"# {large_title}") 
    st.markdown(f"#### ({small_desc}형)") 
    st.write("")
    
    st.markdown(style_text)
    st.write("")
    st.markdown(f"**추천 궁합 파트너:** **{match}**")
    
    st.divider()
    
    st.markdown("### 📊 내 안의 호르몬 우세 비율")
    
    te_total = scores["T"] + scores["E"]
    if te_total == 0: te_total = 1 
    t_pct = int((scores["T"] / te_total) * 100)
    e_pct = 100 - t_pct

    ds_total = scores["D"] + scores["S"]
    if ds_total == 0: ds_total = 1
    d_pct = int((scores["D"] / ds_total) * 100)
    s_pct = 100 - d_pct

    st.markdown("**1. 이성(테토) vs 공감(에겐)**")
    st.markdown(f"""
    <div style="display: flex; height: 35px; width: 100%; border-radius: 10px; overflow: hidden; margin-bottom: 25px; box-shadow: 1px 1px 5px rgba(0,0,0,0.2);">
        <div style="width: {t_pct}%; background-color: #4A90E2; display: flex; align-items: center; justify-content: center; color: white; font-weight: bold; font-size: 14px;">테스토스테론 {t_pct}%</div>
        <div style="width: {e_pct}%; background-color: #F5A623; display: flex; align-items: center; justify-content: center; color: white; font-weight: bold; font-size: 14px;">에스트로겐 {e_pct}%</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("**2. 자극(도파민) vs 안정(세로토닌)**")
    st.markdown(f"""
    <div style="display: flex; height: 35px; width: 100%; border-radius: 10px; overflow: hidden; margin-bottom: 25px; box-shadow: 1px 1px 5px rgba(0,0,0,0.2);">
        <div style="width: {d_pct}%; background-color: #50E3C2; display: flex; align-items: center; justify-content: center; color: #333; font-weight: bold; font-size: 14px;">도파민 {d_pct}%</div>
        <div style="width: {s_pct}%; background-color: #D0021B; display: flex; align-items: center; justify-content: center; color: white; font-weight: bold; font-size: 14px;">세로토닌 {s_pct}%</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.divider()
    
    st.markdown("### 🧚 나만의 AI 메이플 캐릭터")
    if st.session_state.user_photo is not None:
        with st.spinner('생성형 AI가 사진을 분석하여 캐릭터를 그리고 있습니다. (약 10~20초 소요) 🎨'):
            ai_result = get_maple_character_from_ai(st.session_state.user_photo, small_desc)
            
            if ai_result == "API_KEY_MISSING":
                st.error("🚨 오류: Replicate API 키가 설정되지 않았습니다.")
            elif ai_result is not None:
                st.image(ai_result, caption="당신의 특징이 담긴 생성형 AI 메이플 캐릭터!", width=300)
            else:
                st.error("🚨 이미지 생성에 실패했습니다.")
    else:
        st.info("💡 사진을 넣지 않아 AI 캐릭터 생성이 생략되었습니다.")
    
    if st.button("처음부터 다시하기 🔄", use_container_width=True):
        st.session_state.page = 'intro'
        st.session_state.idx = 0
        st.session_state.scores = {"T": 0, "E": 0, "S": 0, "D": 0}
        st.session_state.history = []
        st.session_state.user_photo = None
        st.rerun()