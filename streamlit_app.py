from streamlit_chat import message
from langchain.chains.conversation.memory import ConversationBufferMemory
from langchain.agents import AgentExecutor, create_react_agent
from langchain_community.chat_message_histories import StreamlitChatMessageHistory
from langchain_huggingface import HuggingFaceEndpoint
import streamlit as st
from langchain.chains.conversation.memory import ConversationBufferMemory
from langchain.agents import AgentExecutor, create_react_agent
from langchain_community.chat_message_histories import StreamlitChatMessageHistory
from langchain_huggingface import HuggingFaceEndpoint
from utils_agent_tools import *
from utils_prompt import *
from utils_tts import *
from news_btn_options_utils import *


# ---------set up page config -------------#
st.set_page_config(page_title="Wacky-GPT",
                   layout="wide", page_icon="👾")

st.markdown("<p style='text-align: center; font-size:1.2rem; color:#6b6a67'>Mary Sillius Maximus</p>",
            unsafe_allow_html=True)

# ---- set up creative chat history ----#
chat_msg = StreamlitChatMessageHistory(key="chat_key")
chat_history_size = 5

# Set up LLM for factual mode
llama3p1_70B = "meta-llama/Meta-Llama-3.1-70B-Instruct"

llm_factual = HuggingFaceEndpoint(
    repo_id=llama3p1_70B,
    max_new_tokens=1500,
    do_sample=False,
    temperature=0.1,
    repetition_penalty=1.1,
    return_full_text=False,
    top_p=0.2,
    top_k=40,
    huggingfacehub_api_token=st.secrets["huggingfacehub_api_token"]
)

conversational_memory = ConversationBufferMemory(
    memory_key='chat_history',
    chat_memory=chat_msg,
    k=chat_history_size,
    return_messages=True)

react_agent = create_react_agent(llm_factual, toolkit, prompt)

executor = AgentExecutor(
    agent=react_agent,
    tools=toolkit,
    memory=conversational_memory,
    max_iterations=10,
    handle_parsing_errors=True,
    verbose=True,
    agent_kwargs=agent_kwargs,
)

if prompt := st.chat_input("Ask me a question..."):
    response = executor.invoke(
        {'input': f'{prompt}<|eot_id|>'})
    response = str(
        response['output'].replace('<|eot_id|>', ''))

    with st.container(height=380):
        for index, msg in enumerate(chat_msg.messages):
            if index % 2 == 0:
                message(msg.content.replace('<|eot_id|>', ''),
                        is_user=True, key=f"user{index}",
                        avatar_style="big-ears", seed="Angel")
            else:
                message(msg.content.replace('<|eot_id|>', ''),
                        is_user=False,
                        key=f"bot{index}",
                        avatar_style="big-ears",
                        seed="Salem",
                        allow_html=True,
                        is_table=True,)

        if response.find('iframe') == -1 and response.find('img') == -1:

            col1, col2 = st.columns([1, 3])

            with st.spinner("Audio..."):
                txt2speech(response)
                col1, col2 = st.columns([1, 3])
                col1.audio("audio.mp3", autoplay=True, format="audio/mpeg")

