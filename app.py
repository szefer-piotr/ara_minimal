import openai
import pandas as pd
from dotenv import load_dotenv
from pathlib import Path
from typing import List, Dict
from streamlit.runtime.uploaded_file_manager import UploadedFile
import streamlit as st
import os
from PIL import Image
import io
import requests
from openai import OpenAI

from instructions import chat_instructions
###############################################################################
# SETUP
###############################################################################

load_dotenv()
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
client: OpenAI = OpenAI()

###############################################################################
# HELPERS – container, tools, file upload, image
###############################################################################

def create_container(client: OpenAI, file_ids: List[str], name: str = "user-container"):
    container = client.containers.create(name=name, file_ids=file_ids)
    print(f"Created container {container.id} for code interpreter runs.")
    return container

def create_code_interpreter_tool(container):
    return {"type": "code_interpreter", "container": container.id if container else "auto"}

def create_web_search_tool():
    return {"type": "web_search_preview"}

def upload_csv_and_get_file_id(client: OpenAI, uploaded_file: UploadedFile):
    if uploaded_file.type != "text/csv":
        raise ValueError("Uploaded file is not a CSV file.")
    df = pd.read_csv(uploaded_file)
    csv_buffer = io.BytesIO()
    df.to_csv(csv_buffer, index=False)
    csv_buffer.seek(0)
    openai_file = client.files.create(file=csv_buffer, purpose="user_data")
    return openai_file.id

def load_image_from_openai_container(api_key: str, container_id: str, file_id: str) -> Image.Image:
    url = f"https://api.openai.com/v1/containers/{container_id}/files/{file_id}/content"
    headers = {"Authorization": f"Bearer {api_key}"}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return Image.open(io.BytesIO(response.content))
    raise Exception(f"Failed to retrieve file: {response.status_code}, {response.text}")

###############################################################################
# RENDERING
###############################################################################

def render_llm_response(response):
    elements = []
    for item in response.output:
        if item.type == "code_interpreter_call":
            elements.append({"type": "code", "content": item.code})
        elif item.type == "message":
            for block in item.content:
                if block.type == "output_text":
                    elements.append({"type": "text", "content": block.text})
                    if hasattr(block, "annotations"):
                        for ann in block.annotations:
                            if ann.type == "container_file_citation":
                                elements.append({"type": "image", "filename": ann.filename, "content": ann.file_id})
                                container = st.session_state.container
                                image = load_image_from_openai_container(OPENAI_API_KEY, container.id, ann.file_id)
                                img_bytes = io.BytesIO()
                                image.save(img_bytes, format='PNG')
                                st.session_state.images[ann.file_id] = img_bytes.getvalue()
    return elements

def render_chat_elements(elements, role="assistant"):
    with st.chat_message(role):
        for el in elements:
            if el["type"] == "text":
                st.markdown(el["content"])
            elif el["type"] == "code":
                st.code(el["content"], language="python")
            elif el["type"] == "image":
                image_id = el["content"]
                if image_id in st.session_state.images:
                    image = Image.open(io.BytesIO(st.session_state.images[image_id]))
                    st.image(image)
                else:
                    st.warning("Image not found.")

###############################################################################
# LLM INTERFACE
###############################################################################

def get_llm_response(client: OpenAI, model: str, prompt: str, instructions: str, tools: List[Dict[str, str]], context: str = "", stream: bool = False, temperature: float = 0):
    try:
        response = client.responses.create(
            model=model,
            tools=tools,
            instructions=instructions,
            input=[{"role": "system", "content": context}, {"role": "user", "content": prompt}],
            temperature=temperature,
            stream=stream,
        )
        return render_llm_response(response)
    except openai.BadRequestError as e:
        if "Container is expired" in str(e):
            print("Container expired! Re-create or refresh the container before retrying.")
        else:
            print(f"BadRequestError: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")

###############################################################################
# STREAMLIT APP
###############################################################################

st.set_page_config(page_title="Chat with your Data – powered by OpenAI", layout="wide")

if "messages" not in st.session_state:
    st.session_state.messages = []
if "uploaded_file" not in st.session_state:
    st.session_state.uploaded_file = None
if "container" not in st.session_state:
    st.session_state.container = None
if "tools" not in st.session_state:
    st.session_state.tools = []
if "file_ids" not in st.session_state:
    st.session_state.file_ids = []
if "images" not in st.session_state:
    st.session_state.images = {}

with st.sidebar:
    st.header("Settings")
    model = st.text_input("Model", value="gpt-4o-mini")
    temperature = st.slider("Temperature", 0.0, 1.0, 0.0, 0.05)
    st.divider()
    uploaded_file = st.file_uploader("Upload a CSV file")
    if uploaded_file:
        st.session_state.uploaded_file = uploaded_file
        st.success(f"{uploaded_file.name} uploaded successfully.")

st.title("💬 Chat with an LLM over your data")

for msg in st.session_state.messages:
    render_chat_elements(msg["content"], role=msg["role"])

user_prompt = st.chat_input("Ask me anything…")

if user_prompt:
    if not st.session_state.uploaded_file:
        st.error("Please upload a CSV file first.")
        st.stop()

    if not st.session_state.container:
        file_id = upload_csv_and_get_file_id(client, st.session_state.uploaded_file)
        st.session_state.container = create_container(client, [file_id])
        st.session_state.tools = [
            create_web_search_tool(),
            create_code_interpreter_tool(st.session_state.container)
        ]

    message = {"role": "user", "content": [{"type": "text", "content": user_prompt}]}
    if not st.session_state.messages or st.session_state.messages[-1] != message:
        st.session_state.messages.append(message)

    with st.chat_message("user"):
        st.markdown(user_prompt)

    history = "\n\n".join(
        el["content"]
        for group in [msg["content"] for msg in st.session_state.messages]
        for el in group if el["type"] == "text"
    )

    with st.spinner("Thinking …"):
        assistant_reply = get_llm_response(
            client=client,
            model=model,
            prompt=user_prompt,
            instructions=chat_instructions,
            tools=st.session_state.tools,
            context=history,
            stream=False,
            temperature=temperature
        )

    render_chat_elements(assistant_reply, role="assistant")
    st.session_state.messages.append({"role": "assistant", "content": assistant_reply})

st.caption("Built with 🧡 using Streamlit & OpenAI")
