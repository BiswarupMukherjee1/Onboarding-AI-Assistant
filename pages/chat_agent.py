import streamlit as st
import boto3
import uuid
import time
from botocore.config import Config


# AWS configuration
agent_id = 'MDY3JVJV6Q'  
agent_alias_id = 'DKHOVNKW92'  
region_name = 'us-east-1'      


# Set a custom timeout and region
config = Config(region_name=region_name, connect_timeout=10, read_timeout=120)
client = boto3.client('bedrock-agent-runtime', config=config)


# Function to ask the agent using persistent session ID and retry logic
def ask_agent(agent_id, agent_alias_id, question, retries=3, delay=5):
    if "session_id" not in st.session_state:
        st.session_state.session_id = str(uuid.uuid4())


    for attempt in range(retries):
        try:
            response = client.invoke_agent(
                agentId=agent_id,
                agentAliasId=agent_alias_id,
                sessionId=st.session_state.session_id,
                inputText=question
            )


            response_text = ""
            for event in response['completion']:
                if 'chunk' in event:
                    response_text += event['chunk']['bytes'].decode('utf-8')
            return response_text


        except client.exceptions.InternalServerException:
            if attempt < retries - 1:
                time.sleep(delay)
            else:
                return "Sorry, the service is temporarily unavailable. Please try again later."


# Initialize session state for chat history
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []


st.title("🧑‍💻 PEP EASY ONBOARD Chat ASSOCIATE")
st.write("Hi🤖 chat with me and let me know how I can help you today?")


# Display chat history
for chat in st.session_state.chat_history:
    with st.chat_message(chat["role"]):
        st.markdown(chat["content"])


# Input box
input_text = st.chat_input("What question do you have in mind?")
if input_text:
    # Append user message
    st.session_state.chat_history.append({"role": "user", "content": input_text})
    with st.chat_message("user"):
        st.markdown(input_text)


    # Get response
    response = ask_agent(agent_id, agent_alias_id, input_text)


    # Append assistant response
    st.session_state.chat_history.append({"role": "assistant", "content": response})
    with st.chat_message("assistant"):
        st.markdown(response)
