import pandas as pd
import streamlit as st
from pandasai import SmartDataframe
from pandasai.responses.response_parser import ResponseParser
from pandasai.llm.base import LLM
import requests
import json

class StreamlitResponse(ResponseParser):
    def __init__(self, context) -> None:
        super().__init__(context)

    def format_dataframe(self, result):
        st.dataframe(result["value"])
        return

    def format_plot(self, result):
        st.image(result["value"])
        return

    def format_other(self, result):
        st.write(result["value"])
        return

# Custom DeepSeek LLM class
class DeepSeekLLM(LLM):
    def __init__(self, api_key: str, model: str = "deepseek-chat"):
        super().__init__()
        self.api_key = api_key
        self.model = model
        self._api_url = "https://api.deepseek.com/v1/chat/completions"

    def call(self, prompt: str, **kwargs) -> str:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        data = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            **kwargs
        }
        response = requests.post(self._api_url, headers=headers, json=data)
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]

    @property
    def type(self) -> str:
        return "deepseek-llm"

# Streamlit UI configuration
st.set_page_config(layout='wide')
st.title("ChatBot : Prompt Based Data Analysis and Visualization")
st.markdown('---')

# File uploader
upload_csv_file = st.file_uploader("Upload Your CSV file for data analysis and visualization", type=["csv"])

data = None
if upload_csv_file is not None:
    data = pd.read_csv(upload_csv_file)
    data.columns = data.columns.str.upper()
    st.table(data.head(5))
    st.write('Data Uploaded Successfully!')

st.markdown('---')
st.write('### Enter Your Analysis or Visualization Request')
query = st.text_area("Enter your prompt")




llm = DeepSeekLLM(api_key='')  

if st.button("Submit"):
    if query:
        with st.spinner("Processing..."):
            st.write('### OUTPUT:')
            st.markdown('---')
            if data is not None:
                query_engine = SmartDataframe(
                    data,
                    config={
                        'llm': llm,
                        "response_parser": StreamlitResponse
                    }
                )
                query_engine.chat(query)
            else:
                st.error("Please upload a CSV file first!")
    else:
        st.warning("Please enter a prompt")