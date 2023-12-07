import openai
import streamlit as st
import re
import deepl
import os
from dotenv import load_dotenv

# .env 파일 불러오기
load_dotenv()

# OpenAI API 키 설정
os.environ["OPEN_API_KEY"] = st.secrets["OPENAI_API_KEY"]
openai.api_key = os.environ["OPEN_API_KEY"]

#DeepL API 키 설정
translator = deepl.Translator(os.getenv("DeepL_API_KEY"))

# 사용 가능한 철학자와 대화 프롬프트 목록
philosophers =["니체" '칸트', '맹자', '노자']
#칸트": "In the manner of and with the ideas of Kant, ",
    #"맹자": "In the manner of and with the ideas of Mencius, ",
    #"노자": "In the manner of and with the ideas of Lao Tzu, "

# 답변 길이 목록
len_select = {"짧은 답변 📑": 50, "긴 답변 📜": 200}

#사용가능 모델 목록
available_models = {
    "GPT-3.5-Turbo": "gpt-3.5-turbo",
    "GPT-4": "gpt-4"
}

# Streamlit 앱 설정
st.title('🧔📚 철학자와 대화하기')

# 컬럼 생성하여 나란히 배열
col1, col2, col3 = st.columns(3)

# 첫 번째 컬럼에 철학자 선택
# 사용자 선택에 따라 프롬프트 설정
with col1:
    selected_philosopher = st.radio("👨‍🏫 철학자 선택:", philosophers)
chosen_philosopher=selected_philosopher

# 두 번째 컬럼에 답변 길이 선택
# 답변 길이 설정 버튼
# 답변 길이에 따라 max_tokens 설정
with col2:
    selected_len = st.radio("🗣️ 답변 길이:", list(len_select.keys()))
max_tokens = len_select[selected_len]

# 세 번째 컬럼에 모델 선택
#사용할 모델 선택
with col3:
    selected_model = st.radio("🤖 사용할 모델:", list(available_models.keys()))
selected_model_final = available_models[selected_model]


# session_state에 messages 리스트 초기화
if "messages" not in st.session_state:
    system_message="너는 %s야. AI챗봇처럼 대답하지말고, %s가 말하는 것처럼 대답해줘"%(chosen_philosopher, chosen_philosopher)
    system_message_eng=translator.translate_text(system_message, target_lang="EN-US").text
    st.session_state.messages = [
        {"role": "system", 
         "content": system_message_eng}
    ]
    
# 폼 생성
with st.form(key='message_form'):
    # 사용자의 메시지 입력 받기
    st.write("안녕하세요! 환영합니다. 철학자와 대화를 시작해 보세요!")
    user_message = st.text_input("철학자에게 고민을 말해보세요: ")
    
    # 폼 제출 버튼 추가
    submit_button = st.form_submit_button(label='전송')

if submit_button and user_message:
    #user_message_en=translator.translate_text(user_message, target_lang="EN-US").text
    user_prompt="""
        상담내용: %s
        위 상담 내용에 대해서 %s의 사상을 바탕으로 %d자 이내로, %s가 상담해주듯이 %s의 말투를 사용해서 대답해줘.
        """%(user_message, chosen_philosopher, max_tokens, chosen_philosopher, chosen_philosopher)
    user_prompt_eng=translator.translate_text(user_prompt, target_lang="KO").text
    st.session_state.messages.append({"role": "user", 
                                      "content": user_prompt_eng})

    # OpenAI GPT-3.5-turbo를 사용해 응답 생성
    response = openai.chat.completions.create(
            model=selected_model_final,
            messages=st.session_state.messages, 
        )
    answer = translator.translate_text(response.choices[0].message.content, target_lang='KO').text
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    st.session_state.messages.append({"role": "assistant", "content": answer +'@@@'+user_message +'@@@'+chosen_philosopher})

# 대화 로그 및 상태 초기화 버튼들
if st.button("대화 다시 시작하기"):
    st.session_state.messages = []
    #st.session_state.messages = [
        #{"role": "system", 
         #"content": "You are %s. Do not act like a chatbot and just be %s himself" % (selected_prompt.split(' ')[9].replace(',','') , selected_prompt.split(' ')[9].replace(',',''))}
    #]

st.subheader("📝 대화 로그")
for message in st.session_state.messages:
    if message["role"] == "assistant":
        input_message = message['content'].split('@@@')[1]
        st.write("🙋‍♂나:")
        st.write(input_message)
        st.write("_________________________________________________________________________________________________________")
        st.write("🧔%s:"%(message['content'].split('@@@')[2]))
        answer_message= message['content'].split('@@@')[0]
        st.write(f"{answer}")
