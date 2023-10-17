import openai
import streamlit as st
import re
import deepl
import os
from dotenv import load_dotenv

# .env 파일 불러오기
load_dotenv()

# OpenAI API 키 설정
openai.api_key = os.getenv("OPENAI_API_KEY")

#DeepL API 키 설정
translator = deepl.Translator(os.getenv("DeepL_API_KEY"))

# 사용 가능한 철학자와 대화 프롬프트 목록
philosophers = {
    "니체": "In the manner and with the ideas of Nietzsche, ",
    "칸트": "In the manner and with the ideas of Kant, ",
    "맹자": "In the manner and with the ideas of Mencius, ",
    "노자": "In the manner and with the ideas of Lao Tzu, "
}

# 답변 길이 목록
len_select = {"짧은 답변 📑": 100, "긴 답변 📜": 300}

#모델 성능 선택 목록
model_list = {'GPT-3.5-TURBO':'gpt-3.5-turbo', 'Davinci': 'davinci'}


# Streamlit 앱 설정
st.title('🧔📚 철학자와 대화하기')

# 사용자 선택에 따라 프롬프트 설정
selected_philosopher = st.radio("👨‍🏫 철학자 선택:", list(philosophers.keys()))
selected_prompt = philosophers[selected_philosopher]

# 답변 길이 설정 버튼
# 답변 길이에 따라 max_tokens 설정
selected_len = st.radio("🗣️ 답변 길이:", list(len_select.keys()))
max_tokens = len_select[selected_len]

available_models = {
    "GPT-3.5-Turbo": "gpt-3.5-turbo",
    "Davinci": "davinci"
}
selected_model = st.radio("🤖 사용할 모델:", list(available_models.keys()))
selected_model_final = available_models[selected_model]

# session_state에 messages 리스트 초기화
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", 
         "content": "You are %s. Do not act like a chatbot and just be %s himself" % (selected_prompt.split(' ')[8], selected_prompt.split(' ')[8])}
    ]

if 'messages' not in st.session_state:
    st.session_state.messages = []
    
# 폼 생성
with st.form(key='message_form'):
    # 사용자의 메시지 입력 받기
    st.write("안녕하세요! 철학자와 대화를 시작해 보세요!")
    user_message = st.text_input("철학자에게 고민을 말해보세요: ")
    # 폼 제출 버튼 추가
    submit_button = st.form_submit_button(label='전송')

if submit_button and user_message:
    user_input = selected_prompt + 'Answer about ' + user_message + ' in ' + str(max_tokens) +' words, just like ' + selected_prompt.split(' ')[8].replace(',','') + ' counsel'
    st.session_state.messages.append({"role": "user", 
                                      "content": user_input})

    if selected_model_final == "gpt-3.5-turbo":
        response = openai.ChatCompletion.create(
            model=selected_model_final,
            messages=st.session_state.messages
        )
        message_content = response.choices[0].message["content"]
    else:  # Davinci 선택 시
        #st.write(f"{prompt_text}")
        #st.write(f"{selected_model_final}")
        response = openai.Completion.create(
            engine=selected_model_final,
            prompt=user_input,
            max_tokens=max_tokens
        )
        message_content = response.choices[0].text.strip()
    st.session_state.messages.append({"role": "assistant", "content": message_content})

# 대화 로그 및 상태 초기화 버튼들
if st.button("대화 다시 시작하기"):
    st.session_state.messages = [
        {"role": "system", 
         "content": "You are %s. Do not act like a chatbot and just be %s himself" % (selected_prompt.split(' ')[8].replace(',','') , selected_prompt.split(' ')[8].replace(',',''))}
    ]

# 대화 로그 표시
st.subheader("📝 대화 로그")
for message in st.session_state.messages:
    if message["role"] == "user":
        role_1 = "🙋‍♂️나: "
        question = message['content']
        pattern_1 = "Answer about (.*?) in"
        match_1 = re.search(pattern_1, question)
        if match_1:
            result_1 = match_1.group(1)
        pattern_2= 'like (.*?) counsel'
        match_2= re.search(pattern_2, question)
        if match_2:
            result_2 = match_2.group(1)
        result_2=translator.translate_text(result_2, target_lang="KO").text
        if result_2=='Lao':
            role_2="🧔노자:"
        else:
            role_2 = "🧔%s:"%result_2
        st.write(f"{role_1}")
        st.write(f"{result_1}")
        st.write(f"{role_2}")
    elif message['role'] == 'assistant':
        answer= message['content']
        answer = translator.translate_text(answer, target_lang="KO").text
        st.write(f"{answer}")
