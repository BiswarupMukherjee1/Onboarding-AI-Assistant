import streamlit as st
import os
import boto3
import time
import uuid
import requests
import base64
from audio_recorder_streamlit import audio_recorder
from streamlit_float import float_init
from botocore.config import Config


# AWS Agent configuration
agent_id = 'MDY3JVJV6Q'
agent_alias_id = 'DKHOVNKW92'
S3_BUCKET = "storevoice"


# Set a custom timeout
config = Config(connect_timeout=10, read_timeout=180)
client = boto3.client('bedrock-agent-runtime', config=config)


# Initialize float feature
float_init()


# Initialize session state
def initialize_session_state():
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant", "content": "Hi! How may I assist you today?"}
        ]
    if "session_id" not in st.session_state:
        st.session_state.session_id = str(uuid.uuid4())


initialize_session_state()


st.title("🧑‍💻 PEP EASY ONBOARD VOICE ASSOCIATE")
st.markdown("Hi🤖 just click on the voice recorder and let me know how I can help you today?")


# Footer container for microphone
footer_container = st.container()
with footer_container:
    audio_bytes = audio_recorder()


# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])


# Upload audio to S3 and transcribe
def speech_to_text(file_path):
    transcribe = boto3.client('transcribe')
    s3 = boto3.client('s3')


    job_name = f"transcription-{uuid.uuid4()}"
    s3.upload_file(file_path, S3_BUCKET, file_path)
    job_uri = f"s3://{S3_BUCKET}/{file_path}"


    transcribe.start_transcription_job(
        TranscriptionJobName=job_name,
        Media={'MediaFileUri': job_uri},
        MediaFormat='mp3',
        LanguageCode='en-US'
    )


    while True:
        status = transcribe.get_transcription_job(TranscriptionJobName=job_name)
        if status['TranscriptionJob']['TranscriptionJobStatus'] in ['COMPLETED', 'FAILED']:
            break
        time.sleep(5)


    if status['TranscriptionJob']['TranscriptionJobStatus'] == 'COMPLETED':
        transcript_url = status['TranscriptionJob']['Transcript']['TranscriptFileUri']
        transcript_json = requests.get(transcript_url).json()
        return transcript_json['results']['transcripts'][0]['transcript']
    return None


# Convert text to speech
def text_to_speech(output_path, text):
    polly = boto3.client('polly')
    response = polly.synthesize_speech(
        Text=text,
        OutputFormat='mp3',
        VoiceId='Joanna'
    )
    with open(output_path, 'wb') as f:
        f.write(response['AudioStream'].read())
    return output_path


# Autoplay audio
def autoplay_audio(file_path: str):
    with open(file_path, "rb") as f:
        audio_bytes = f.read()
        b64 = base64.b64encode(audio_bytes).decode()
        md = f"""
        <audio autoplay="true" controls>
        <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
        </audio>
        """
        st.markdown(md, unsafe_allow_html=True)


# Ask the agent with retry logic
def ask_agent(question, retries=3, delay=5):
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


# Handle audio input
if audio_bytes:
    with st.spinner("Listening..."):
        webm_file_path = "temp_audio.mp3"
        with open(webm_file_path, "wb") as f:
            f.write(audio_bytes)


        transcript = speech_to_text(webm_file_path)
        if transcript:
            st.session_state.messages.append({"role": "user", "content": transcript})
            with st.chat_message("user"):
                st.write(transcript)
            os.remove(webm_file_path)


# Generate assistant response
if st.session_state.messages[-1]["role"] != "assistant":
    with st.chat_message("assistant"):
        with st.spinner("Processing..."):
            final_response = ask_agent(st.session_state.messages[-1]["content"].lower().strip())
            st.write(final_response)
        with st.spinner("Generating audio response..."):
            speech_file_path = 'audio_response.mp3'
            text_to_speech(speech_file_path, final_response)
            autoplay_audio(speech_file_path)
        st.session_state.messages.append({"role": "assistant", "content": final_response})
        os.remove(speech_file_path)


# Float the footer container
footer_container.float("bottom: 0rem;")