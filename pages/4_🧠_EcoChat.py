""" Simple Chatbot
@Original author: Nigel Gebodh
Adapted and Modified: Desmond Lartey
"""
import numpy as np
import streamlit as st
from openai import OpenAI
import os
import sys
from dotenv import load_dotenv, dotenv_values
load_dotenv()

# #===========================================
# updates = '''
# Updates
# + 04/20/2025
# - Changed the inference from HF b/c 
#     API calls are not very limted.
# - Added API call limiting to allow for demoing
# - Added support for adding your own API token.     

# + 04/16/2025  
# - Changed the inference points on HF b/c
#     older points no longer supported.
    
# '''
# #-------------------------------------------


# EcoChat.py — Streamlit Chatbot Using Local Embedding Search
# import streamlit as st
# from ecosystem_search import search_ess_knowledge

# # --- Page config ---
# st.set_page_config(page_title="EcoChat", page_icon="🧠", layout="wide")
# st.title("🧠 EcoChat: Ask About Ecosystem Services")

# # --- Chat Input ---
# user_question = st.chat_input("Ask EcoChat about ecosystem services...")

# if user_question:
#     # Step 1: Search in-memory vector store using cosine similarity
#     results_df, top_chunks = search_ess_knowledge(user_question)

#     # Step 2: Show natural-language snippets
#     st.markdown("### 🔍 Relevant Knowledge Snippets")
#     for i, chunk in enumerate(top_chunks):
#         st.markdown(f"**{i+1}.** {chunk}")

#     # Step 3: Optional table for source rows
#     with st.expander("📄 Matching ESS database rows"):
#         st.dataframe(results_df, use_container_width=True)

#     # Step 4 (Optional): Placeholder for future LLM integration
#     # Example:
#     # llm_response = my_llm(prompt=f"Context:\n{top_chunks}\n\nQuestion: {user_question}")
#     # st.markdown("### 🤖 EcoChat's Response")
#     # st.write(llm_response)

#     st.success("✅ Response generated using local embedding search on ESS data.")








API_CALL_LIMIT = 10 # Define the limit

if 'api_call_count' not in st.session_state:
    st.session_state.api_call_count = 0
    st.session_state.remaining_calls = API_CALL_LIMIT



model_links_hf ={
      "Gemma-3-27B-it":{
                      "inf_point":"https://router.huggingface.co/nebius/v1",
                      "link":"google/gemma-3-27b-it-fast",
                      },
      "Meta-Llama-3.1-8B":{
                      "inf_point":"https://router.huggingface.co/nebius/v1",
                      "link":"meta-llama/Meta-Llama-3.1-8B-Instruct-fast",
                      },
      "Mistral-7B":{
                      "inf_point":"https://router.huggingface.co/together/v1",
                      "link":"mistralai/Mistral-7B-Instruct-v0.3",
                      },
      "Gemma-2-27B-it":{
                      "inf_point":"https://router.huggingface.co/nebius/v1",
                      "link":"google/gemma-2-27b-it-fast",
                      },
      "Gemma-2-2B-it":{
                      "inf_point":"https://router.huggingface.co/nebius/v1",
                      "link":"google/gemma-2-2b-it-fast",
                      },
      "Zephyr-7B-β":{
                      "inf_point":"https://router.huggingface.co/hf-inference/models/HuggingFaceH4/zephyr-7b-beta/v1",
                      "link":"HuggingFaceH4/zephyr-7b-beta",
                      },
  }


model_links_groq ={
      "Gemma-2-9B-it":{
                      "inf_point":"https://api.groq.com/openai/v1",
                      "link":"gemma2-9b-it",
                      },
      "Meta-Llama-3.1-8B":{
                      "inf_point":"https://api.groq.com/openai/v1",
                      "link":"llama-3.1-8b-instant",
                      },
      "Meta-Llama-4-Scout-17B": {
      "inf_point": "https://api.groq.com/openai/v1",
      "link": "meta-llama/llama-4-scout-17b-16e-instruct",
},

  }

#Pull info about the model to display
model_info ={
    "Mistral-7B":
        {'description':"""The Mistral model is a **Large Language Model (LLM)** that's able to have question and answer interactions.\n \
            \nIt was created by the [**Mistral AI**](https://mistral.ai/news/announcing-mistral-7b/) team as has over  **7 billion parameters.** \n""",
        'logo':'https://cdn-avatars.huggingface.co/v1/production/uploads/62dac1c7a8ead43d20e3e17a/wrLf5yaGC6ng4XME70w6Z.png'},
    "Gemma-2-27B-it":        
        {'description':"""The Gemma model is a **Large Language Model (LLM)** that's able to have question and answer interactions.\n \
            \nIt was created by the [**Google's AI Team**](https://blog.google/technology/developers/gemma-open-models/) team as has over  **27 billion parameters.** \n""",
        'logo':'https://pbs.twimg.com/media/GG3sJg7X0AEaNIq.jpg'},
    "Gemma-3-27B-it":        
        {'description':"""The Gemma model is a **Large Language Model (LLM)** that's able to have question and answer interactions.\n \
            \nIt was created by the [**Google's AI Team**](https://blog.google/technology/developers/gemma-open-models/) team as has over  **27 billion parameters.** \n""",
        'logo':'https://pbs.twimg.com/media/GG3sJg7X0AEaNIq.jpg'},
    "Gemma-2-2B-it":        
        {'description':"""The Gemma model is a **Large Language Model (LLM)** that's able to have question and answer interactions.\n \
            \nIt was created by the [**Google's AI Team**](https://blog.google/technology/developers/gemma-open-models/) team as has over  **2 billion parameters.** \n""",
        'logo':'https://pbs.twimg.com/media/GG3sJg7X0AEaNIq.jpg'},
    "Gemma-2-9B-it":        
        {'description':"""The Gemma model is a **Large Language Model (LLM)** that's able to have question and answer interactions.\n \
            \nIt was created by the [**Google's AI Team**](https://blog.google/technology/developers/gemma-open-models/) team as has over  **9 billion parameters.** \n""",
        'logo':'https://pbs.twimg.com/media/GG3sJg7X0AEaNIq.jpg'},
    "Zephyr-7B":        
        {'description':"""The Zephyr model is a **Large Language Model (LLM)** that's able to have question and answer interactions.\n \
            \nFrom Huggingface: \n\
            Zephyr is a series of language models that are trained to act as helpful assistants. \
            [Zephyr 7B Gemma](https://huggingface.co/HuggingFaceH4/zephyr-7b-gemma-v0.1)\
            is the third model in the series, and is a fine-tuned version of google/gemma-7b \
            that was trained on on a mix of publicly available, synthetic datasets using Direct Preference Optimization (DPO)\n""",
        'logo':'https://huggingface.co/HuggingFaceH4/zephyr-7b-gemma-v0.1/resolve/main/thumbnail.png'},
    "Zephyr-7B-β":        
        {'description':"""The Zephyr model is a **Large Language Model (LLM)** that's able to have question and answer interactions.\n \
            \nFrom Huggingface: \n\
            Zephyr is a series of language models that are trained to act as helpful assistants. \
            [Zephyr-7B-β](https://huggingface.co/HuggingFaceH4/zephyr-7b-beta)\
            is the second model in the series, and is a fine-tuned version of mistralai/Mistral-7B-v0.1 \
            that was trained on on a mix of publicly available, synthetic datasets using Direct Preference Optimization (DPO)\n""",
        'logo':'https://huggingface.co/HuggingFaceH4/zephyr-7b-alpha/resolve/main/thumbnail.png'},
    "Meta-Llama-3-8B":
        {'description':"""The Llama (3) model is a **Large Language Model (LLM)** that's able to have question and answer interactions.\n \
            \nIt was created by the [**Meta's AI**](https://llama.meta.com/) team and has over  **8 billion parameters.** \n""",
        'logo':'Llama_logo.png'},
    "Meta-Llama-3.1-8B":
        {'description':"""The Llama (3.1) model is a **Large Language Model (LLM)** that's able to have question and answer interactions.\n \
            \nIt was created by the [**Meta's AI**](https://llama.meta.com/) team and has over  **8 billion parameters.** \n""",
        'logo':'https://huggingface.co/spaces/ngebodh/SimpleChatbot/resolve/main/Llama3_1_logo.png'},
    "Meta-Llama-4-Scout-17B": {
    'description': """The Llama 4 Scout model is a **Large Language Model (LLM)** designed for fast and accurate interactions.\
    \nIt is part of Meta's Llama 4 series and optimized for instruction-following and chat-based applications.\n \
    \nCreated by [**Meta AI**](https://llama.meta.com/) with **17 billion parameters**.""",
    'logo': 'https://upload.wikimedia.org/wikipedia/commons/0/0b/Meta_Platforms_Inc._logo.svg'},

}



#Random dog images for error message
random_dog = ["0f476473-2d8b-415e-b944-483768418a95.jpg",
              "1bd75c81-f1d7-4e55-9310-a27595fa8762.jpg",
              "526590d2-8817-4ff0-8c62-fdcba5306d02.jpg",
              "1326984c-39b0-492c-a773-f120d747a7e2.jpg",
              "42a98d03-5ed7-4b3b-af89-7c4876cb14c3.jpg",
              "8b3317ed-2083-42ac-a575-7ae45f9fdc0d.jpg",
              "ee17f54a-83ac-44a3-8a35-e89ff7153fb4.jpg",
              "027eef85-ccc1-4a66-8967-5d74f34c8bb4.jpg",
              "08f5398d-7f89-47da-a5cd-1ed74967dc1f.jpg",
              "0fd781ff-ec46-4bdc-a4e8-24f18bf07def.jpg",
              "0fb4aeee-f949-4c7b-a6d8-05bf0736bdd1.jpg",
              "6edac66e-c0de-4e69-a9d6-b2e6f6f9001b.jpg",
              "bfb9e165-c643-4993-9b3a-7e73571672a6.jpg"]



def reset_conversation():
    '''
    Resets Conversation
    '''
    st.session_state.conversation = []
    st.session_state.messages = []
    return None
    


# --- Sidebar Setup ---
st.sidebar.title("Chatbot Settings")

# Define model clients
client_names = ["Provided API Call", "HF-Token"]
client_select = st.sidebar.selectbox("Select Model Client", client_names)

# Handle Hugging Face Token
if "HF-Token" in client_select:
    try:
        if "API_token" not in st.session_state:
            st.session_state.API_token = None

        st.session_state.API_token = st.sidebar.text_input("Enter your Hugging Face Access Token", type="password")
        model_links = model_links_hf

    except Exception as e:
        st.sidebar.error(f"Credentials Error:\n\n {e}")

# Handle GROQ Token from secrets
elif "Provided API Call" in client_select:
    try:
        if "API_token" not in st.session_state:
            st.session_state.API_token = None

        # ✅ Use secrets safely here
        st.session_state.API_token = st.secrets["GROQ_API_TOKEN"]
        model_links = model_links_groq

        if not st.session_state.API_token:
            st.error("Missing GROQ API Token. Please add it to your Streamlit secrets.")
            st.stop()

    except Exception as e:
        st.sidebar.error("Credentials Error. Check your secrets configuration.")
        st.stop()






# Define the available models
models =[key for key in model_links.keys()]

# Create the sidebar with the dropdown for model selection
selected_model = st.sidebar.selectbox("Select Model", models)

#Create a temperature slider
temp_values = st.sidebar.slider('Select a temperature value', 0.0, 1.0, (0.5))



#Add reset button to clear conversation
st.sidebar.button('Reset Chat', on_click=reset_conversation, type="primary") #Reset button

st.sidebar.divider() # Add a visual separator

# Create model description
st.sidebar.subheader(f"About {selected_model}")
st.sidebar.write(f"You're now chatting with **{selected_model}**")
st.sidebar.markdown(model_info[selected_model]['description'])
st.sidebar.image(model_info[selected_model]['logo'])
st.sidebar.markdown("*Generated content may be inaccurate or false.*")
# st.sidebar.markdown("\nLearn how to build this chatbot [here](https://ngebodh.github.io/projects/2024-03-05/).")
st.sidebar.markdown("\nRun into issues? \nTry coming back in a bit, GPU access might be limited or something is down.")




if "prev_option" not in st.session_state:
    st.session_state.prev_option = selected_model

if st.session_state.prev_option != selected_model:
    st.session_state.messages = []
    st.session_state.prev_option = selected_model
    reset_conversation()



#Pull in the model we want to use
repo_id = model_links[selected_model]

# initialize the client
client = OpenAI(
  base_url=model_links[selected_model]["inf_point"],#"https://api-inference.huggingface.co/v1",
  api_key=st.session_state.API_token#os.environ.get('HUGGINGFACE_API_TOKEN')#"hf_xxx" # Replace with your token
) 


st.subheader(f'AI - {selected_model}')

# Set a default model
if selected_model not in st.session_state:
    st.session_state[selected_model] = model_links[selected_model] 

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []


# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])





if prompt := st.chat_input(f"Hi I'm {selected_model}, ask me a question about ecosystem services "):

    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})



    if st.session_state.api_call_count >= API_CALL_LIMIT:
        
        # Add the warning to the displayed messages, but not to the history sent to the model
        response = f"LIMIT REACHED: Sorry, you have reached the API call limit for this session."
        # st.write(response)
        st.warning(f"Sorry, you have reached the API call limit for this session.")
        st.session_state.messages.append({"role": "assistant", "content": response })


    else:
        # Display assistant response in chat message container
        with st.chat_message("assistant"):
            try:
                st.session_state.api_call_count += 1
                # Add a spinner for better UX while waiting
                with st.spinner(f"Asking {selected_model}..."):

                    stream = client.chat.completions.create(
                        model=model_links[selected_model]["link"],
                        messages=[
                            {"role": m["role"], "content": m["content"]}
                            for m in st.session_state.messages
                        ],
                        temperature=temp_values,#0.5,
                        stream=True,
                        max_tokens=3000,
                    )

                    response = st.write_stream(stream)

                    remaining_calls = (API_CALL_LIMIT) - st.session_state.api_call_count
                    st.markdown(f"\n\n <span style='float: right; font-size: 0.8em; color: gray;'>API calls:({remaining_calls}/{API_CALL_LIMIT})</span>", unsafe_allow_html=True)

            except Exception as e:
                response = "😵‍💫 Looks like someone unplugged something!\
                        \n Either the model space is being updated or something is down.\
                        \n\
                        \n Try again later. \
                        \n\
                        \n Here's a random pic of a 🐶:"
                st.write(response)
                random_dog_pick = 'https://random.dog/'+ random_dog[np.random.randint(len(random_dog))]
                st.image(random_dog_pick)
                st.write("This was the error message:")
                st.write(e)



        
        st.session_state.messages.append({"role": "assistant", "content": response})