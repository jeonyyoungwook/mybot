import streamlit as st
import urllib.parse

# 1. 페이지 설정
st.set_page_config(page_title="GenSpark Secret Link", page_icon="🕵️‍♂️", layout="centered")

# 2. 언어 설정 (세션 상태 초기화)
if 'lang' not in st.session_state:
    st.session_state.lang = 'ko' # 기본값 한국어

# 3. 언어별 텍스트 데이터 (딕셔너리)
text_data = {
    'ko': {
        'title': "🕵️‍♂️ GenSpark 시크릿 접속기",
        'subtitle': "로그인 없이 검색하려면 아래 방법을 먼저 확인하세요!",
        'guide_title': "💡 시크릿 모드로 여는 방법",
        'tab_pc': "💻 컴퓨터(PC)",
        'tab_mobile': "📱 핸드폰(모바일)",
        'pc_msg': "마우스가 있다면 이 방법을 쓰세요!",
        'pc_desc': """
        1. 아래 **빨간색 버튼** 위로 마우스를 가져가세요.
        2. 버튼 위에서 마우스 **오른쪽 버튼(우클릭)**을 한 번 누르세요.
        3. 메뉴가 뜨면 **[시크릿 창에서 링크 열기]**를 클릭하세요.
        """,
        'pc_short': "🖱️ 우클릭 → 🕶️ 시크릿 창 열기",
        'mo_msg': "스마트폰이라면 이 방법을 쓰세요!",
        'mo_desc': """
        1. 아래 **빨간색 버튼**을 손가락으로 **1초 동안 꾹~ 누르고 계세요.**
        2. 폰 화면에 메뉴창이 뜹니다.
        3. **[시크릿 탭에서 열기]** 또는 **[새 시크릿 탭에서 열기]**를 터치하세요.
        """,
        'mo_short': "👆 꾹 누르기 → 🕶️ 시크릿 탭 열기",
        'input_title': "1️⃣ 질문 입력",
        'input_ph': "무엇을 검색할까요? (예: 오늘 날씨)",
        'btn_title': "2️⃣ 접속 버튼",
        'btn_caption': "👇 아래 버튼을 위 설명대로 누르세요.",
        'btn_search': "🔍 '{query}' 검색 결과 열기",
        'btn_home': "🏠 GenSpark 홈페이지 열기"
    },
    'en': {
        'title': "🕵️‍♂️ GenSpark Secret Link",
        'subtitle': "Check instructions below to search without login!",
        'guide_title': "💡 How to open in Incognito Mode",
        'tab_pc': "💻 PC / Desktop",
        'tab_mobile': "📱 Mobile",
        'pc_msg': "If you are using a mouse:",
        'pc_desc': """
        1. Hover over the **Red Button** below.
        2. **Right-click** on the button.
        3. Select **[Open link in Incognito window]**.
        """,
        'pc_short': "🖱️ Right Click → 🕶️ Incognito Window",
        'mo_msg': "If you are using a smartphone:",
        'mo_desc': """
        1. **Press and hold** the **Red Button** below for 1 second.
        2. A menu will appear.
        3. Select **[Open in Incognito tab]** or **[Open in Private mode]**.
        """,
        'mo_short': "👆 Long Press → 🕶️ Incognito Tab",
        'input_title': "1️⃣ Enter Query",
        'input_ph': "What do you want to search?",
        'btn_title': "2️⃣ Access Button",
        'btn_caption': "👇 Use the button below via Secret Mode.",
        'btn_search': "🔍 Search '{query}'",
        'btn_home': "🏠 Open GenSpark Home"
    },
    'zh': {
        'title': "🕵️‍♂️ GenSpark 秘密连接器",
        'subtitle': "若想免登录搜索，请务必阅读以下说明！",
        'guide_title': "💡 如何使用隐身模式打开",
        'tab_pc': "💻 电脑 (PC)",
        'tab_mobile': "📱 手机 (Mobile)",
        'pc_msg': "电脑用户请使用此方法：",
        'pc_desc': """
        1. 将鼠标移至下方的 **红色按钮** 上。
        2. 点击鼠标 **右键**。
        3. 在菜单中选择 **[在隐身窗口中打开链接]**。
        """,
        'pc_short': "🖱️ 右键点击 → 🕶️ 隐身窗口",
        'mo_msg': "手机用户请使用此方法：",
        'mo_desc': """
        1. 用手指 **长按** 下方的 **红色按钮** 1秒钟。
        2. 会弹出菜单选项。
        3. 选择 **[在隐身标签页中打开]** 或 **[在无痕模式中打开]**。
        """,
        'mo_short': "👆 长按 → 🕶️ 隐身/无痕模式",
        'input_title': "1️⃣ 输入问题",
        'input_ph': "想搜索什么？",
        'btn_title': "2️⃣ 连接按钮",
        'btn_caption': "👇 请按上述说明点击下方按钮。",
        'btn_search': "🔍 搜索 '{query}'",
        'btn_home': "🏠 打开 GenSpark 首页"
    },
    'ja': {
        'title': "🕵️‍♂️ GenSpark シークレット接続",
        'subtitle': "ログインなしで検索するには、以下の手順に従ってください！",
        'guide_title': "💡 シークレットモードでの開き方",
        'tab_pc': "💻 パソコン (PC)",
        'tab_mobile': "📱 スマホ (Mobile)",
        'pc_msg': "マウスをお使いの方はこちら：",
        'pc_desc': """
        1. 下の **赤いボタン** の上にマウスを置きます。
        2. ボタンの上で **右クリック** します。
        3. メニューから **[シークレット ウィンドウでリンクを開く]** を選択します。
        """,
        'pc_short': "🖱️ 右クリック → 🕶️ シークレット窓",
        'mo_msg': "スマホをお使いの方はこちら：",
        'mo_desc': """
        1. 下の **赤いボタン** を指で **1秒間長押し** してください。
        2. メニューが表示されます。
        3. **[シークレット タブで開く]** または **[新しいシークレット タブ]** を選択します。
        """,
        'mo_short': "👆 長押し → 🕶️ シークレットタブ",
        'input_title': "1️⃣ 質問入力",
        'input_ph': "何を検索しますか？",
        'btn_title': "2️⃣ 接続ボタン",
        'btn_caption': "👇 上記の方法で下のボタンを押してください。",
        'btn_search': "🔍 '{query}' 検索結果を開く",
        'btn_home': "🏠 GenSpark ホームを開く"
    }
}

# 4. 언어 선택 버튼 (가로로 배치)
col1, col2, col3, col4 = st.columns(4)

if col1.button("🇰🇷 한국어", use_container_width=True):
    st.session_state.lang = 'ko'
if col2.button("🇺🇸 English", use_container_width=True):
    st.session_state.lang = 'en'
if col3.button("🇨🇳 中文", use_container_width=True):
    st.session_state.lang = 'zh'
if col4.button("🇯🇵 日本語", use_container_width=True):
    st.session_state.lang = 'ja'

# 현재 선택된 언어의 텍스트 가져오기
t = text_data[st.session_state.lang]

# ---------------------------------------------------------
# UI 구성 시작
# ---------------------------------------------------------

st.title(t['title'])
st.write(t['subtitle'])

st.divider() 

# --- [변경] 설명 부분을 위로 올림 ---
st.header(t['guide_title'])

tab1, tab2 = st.tabs([t['tab_pc'], t['tab_mobile']])

with tab1:
    st.info(t['pc_msg'])
    st.markdown(t['pc_desc'])
    st.caption(t['pc_short'])

with tab2:
    st.success(t['mo_msg'])
    st.markdown(t['mo_desc'])
    st.caption(t['mo_short'])

st.divider() 

# --- 질문 입력 ---
st.markdown(f"### {t['input_title']}")
query = st.text_input(
    label="query",
    label_visibility="collapsed", # 레이블 숨김 (깔끔하게)
    placeholder=t['input_ph']
)

# --- 링크 생성 ---
if query:
    encoded_query = urllib.parse.quote(query)
    target_url = f"https://www.genspark.ai/search?query={encoded_query}"
    # query 부분이 {query}로 들어가지 않게 f-string 밖에서 처리하거나 포맷팅
    button_text = t['btn_search'].replace("{query}", query)
else:
    target_url = "https://www.genspark.ai/"
    button_text = t['btn_home']

# --- 접속 버튼 ---
st.markdown(f"### {t['btn_title']}")
st.caption(t['btn_caption'])

st.link_button(
    label=button_text, 
    url=target_url,
    type="primary", 
    use_container_width=True
)
