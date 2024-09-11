from streamlit_lottie import st_lottie
from streamlit_chat import message
import streamlit as st
from utils_agent_tools import *
from utils_prompt import *
from utils_tts import *
from utils_buttons import *
from utils_calendar import *
from streamlit_extras.bottom_container import bottom
import streamlit_antd_components as sac
from langchain_community.chat_message_histories import StreamlitChatMessageHistory
from langchain.agents import AgentExecutor, create_react_agent
from langchain.chains.conversation.memory import ConversationBufferMemory
from langchain_huggingface import HuggingFaceEndpoint
from langchain.chains import LLMChain
import re

# ---------set up page config -------------#
st.set_page_config(page_title="Wacky-GPT",
                   layout="wide", page_icon="👾")

tab = select_tab()

if tab == "chat":
    # ---------set up toggle at the bottom -------------#
    with bottom():
        mode_toggle = st.toggle(label="Creative Mode", value=False)

    # ---- set up creative chat history ----#
    chat_msg = StreamlitChatMessageHistory(key="chat_key")
    chat_history_size = 5

    # ---------set up LLM  -------------#
    llama3p1_70B = "meta-llama/Meta-Llama-3.1-70B-Instruct"

    # initialise LLM for agents and tools
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

    # ---------set up general memory  -------------#
    conversational_memory = ConversationBufferMemory(
        memory_key='chat_history',
        chat_memory=chat_msg,
        k=chat_history_size,
        return_messages=True
    )

    # ---------set up agent with tools  -------------#
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

    # ---------set up for creative mode  -------------#
    # Initialize LLM for creative mode
    llm_creative = HuggingFaceEndpoint(
        repo_id=llama3p1_70B,
        task="text-generation",
        max_new_tokens=1000,
        do_sample=False,
        temperature=0.2,
        repetition_penalty=1.1,
        return_full_text=False,
        top_p=0.2,
        top_k=40,
        huggingfacehub_api_token=st.secrets["huggingfacehub_api_token"]
    )

    # ------ set up the llm chain -----#
    chat_llm_chain = LLMChain(
        llm=llm_creative,
        prompt=chatPrompt,  # located at utils_prompt.py
        verbose=True,
        memory=conversational_memory,
    )

    # ------ initial welcome message -------#

    # set up session state as a gate to display welcome message
    if 'initial_msg' not in st.session_state:
        st.session_state.initial_msg = 0

    # if 0, add welcome message to chat_msg
    if st.session_state.initial_msg == 0:
        part_day = get_time_bucket()  # located at utils_tts.py
        welcome = f"{part_day} from Singapore! I'm Sillius Maximus! How about news headlines to start your day?"
        chat_msg.add_ai_message(welcome)
    # ------ set up message from chat history  -----#

    for index, msg in enumerate(chat_msg.messages):

        # bot's message is in even position as welcome message is added at initial
        if index % 2 == 0:
            message(msg.content.replace('<|eot_id|>', '').replace("assistant", "").replace('Human:', ''),
                    is_user=False,
                    key=f"bot{index}",
                    avatar_style="big-ears",
                    seed="Salem",
                    allow_html=True,
                    is_table=True,)

        # user's message is in odd position
        else:
            message(msg.content.replace('<|eot_id|>', ''),
                    is_user=True, key=f"user{index}",
                    avatar_style="big-ears", seed="Angel")

        # -----clear history -----#
        # add a clear_btn
        clear_btn = sac.buttons([sac.ButtonsItem(icon=sac.BsIcon(name='x-circle', size=20))],
                                align='left',
                                variant='link',
                                index=None,
                                label=" ",
                                key=f"clear_msg{index}"
                                )

        # - clear chat_msg
        # - set initial_msg to 1 to stop welcome message
        if clear_btn is not None:
            chat_msg.messages.pop(-1)
            # chat_msg.clear()

        # set initial_msg to 0 in first loop
        if index == 0:
            st.session_state.initial_msg = 1

    # ---------set up for creative mode  -------------#
    if mode_toggle:
        # initialize response type as creative
        response_type = "creative"
    else:
        # initialize response type as agents
        response_type = "agents"

    # ------ set up user input -----#

    if prompt := st.chat_input("Ask me a question..."):
        # show prompt message
        message(prompt,
                is_user=True,
                key=f"user",
                avatar_style="big-ears",
                seed="Angel")

        # ---- if response_type is agent -----#

        if response_type == "agents":

            with st.spinner("Generating text and voice..."):

                # use {'input': f'{prompt}<|eot_id|>'})
                response = executor.invoke(
                    {'input': f'{prompt}<|eot_id|>'})

                # remove prompt format for better display
                edited_response = str(
                    response['output'].replace('<|eot_id|>', ''))

                # show message
                message(edited_response,
                        is_user=False,
                        key=f"bot_1",
                        avatar_style="big-ears",
                        seed="Salem",
                        allow_html=True,
                        is_table=True)

                # audio conversation if response is NOT video or image related
                if edited_response.find('iframe') == -1 and edited_response.find('img') == -1:
                    col1, col2 = st.columns([1, 3])
                    # with st.spinner("Generating voice..."):
                    txt2speech(edited_response)
                    col1, col2 = st.columns([1, 3])
                    col1.audio("audio.mp3", autoplay=True, format="audio/mpeg")

        # ---- if response_type is creative -----#

        elif response_type == "creative":

            # use {'human_input': f'{prompt}<|eot_id|>'})
            response = chat_llm_chain.invoke(
                {'human_input': f'{prompt}<|eot_id|>'})

            # remove prompt format for better display
            edited_response = response["text"].replace("assistant", "")
            human = re.search(r"Human:.*|human:.*", edited_response)
            if human is not None:
                # exclude "Human:" located at end of string
                edited_response = edited_response[:human.start()]

            # show message
            message(edited_response,
                    is_user=False,
                    key=f"bot_2",
                    avatar_style="big-ears",
                    seed="Salem",
                    allow_html=True,
                    is_table=True,)

            # st_copy_to_clipboard(edited_response)

            # audio conversation
            with st.spinner("Audio..."):
                txt2speech(edited_response)
                col1, col2 = st.columns([1, 3])
                col1.audio("audio.mp3", autoplay=True, format="audio/mpeg")


if tab == "schedule":

    password = st.text_input(label="Your Password",
                             type="password")

    if password == st.secrets["my_password"]:
        schedule_widgets()
        view_schedule()

if tab == "health":

    password = st.text_input(label="Your Password",
                             type="password")

    if password == st.secrets["my_password"]:
        st.write("Beta Testing")
