import openai
import streamlit as st
import re
import deepl

# OpenAI API 키 설정
API_KEY = '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'
openai.api_key = API_KEY

#DeepL API 키 설정
auth_key = "c24af978-e422-0d8b-4420-4c2daa1a067e:fx"
translator = deepl.Translator(auth_key)

# 사용 가능한 철학자와 대화 프롬프트 목록
philosophers = {
    "니체": "In the manner and with the ideas of Nietzsche, ",
    "칸트": "In the manner and with the ideas of Kant, ",
    "맹자": "In the manner and with the ideas of Mencius, ",
    "노자": "In the manner and with the ideas of Lao Tzu, "
}

# 답변 길이 목록
len_select = {"짧은 답변 📑": 100, "긴 답변 📜": 300}


# Streamlit 앱 설정
st.title('🧔📚 철학자와 대화하기')

# 사용자 선택에 따라 프롬프트 설정
selected_philosopher = st.radio("👨‍🏫 철학자 선택:", list(philosophers.keys()))
selected_prompt = philosophers[selected_philosopher]

# 답변 길이 설정 버튼
# 답변 길이에 따라 max_tokens 설정
selected_len = st.radio("🗣️ 답변 길이:", list(len_select.keys()))
max_tokens = len_select[selected_len]

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
    user_message = st.text_input("철학자와 대화를 시작해보세요: ")
    # 폼 제출 버튼 추가
    submit_button = st.form_submit_button(label='전송')

if submit_button and user_message:
    #user_message_en=translator.translate_text(user_message, target_lang="EN-US").text
    st.session_state.messages.append({"role": "user", 
                                      "content": selected_prompt + 'Answer about ' + user_message + ' in ' + str(max_tokens) +' words, just like ' + selected_prompt.split(' ')[8].replace(',','') + ' counsel'})

    # OpenAI GPT-3.5-turbo를 사용해 응답 생성
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=st.session_state.messages  # 전체 메시지 리스트를 API에 전송
    )

    message_content = response.choices[0].message["content"]
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


# In[ ]:





# In[ ]:




