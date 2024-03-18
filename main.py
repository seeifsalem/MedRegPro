import os
import streamlit as st

from utils import (
    doc_loader, summary_prompt_creator, doc_to_final_summary,
)
from my_prompts import file_map, file_combine, youtube_map, youtube_combine
from streamlit_app_utils import check_gpt_4, check_key_validity, create_temp_file, create_chat_model, \
    token_limit, token_minimum

from utils import transcript_loader


def main():
    """
    The main function for the Streamlit app.

    :return: None.
    """
    st.title("Regulations Checker")

    input_method = st.radio("Select input method", ('Upload a document', 'Enter text'))

    if input_method == 'Upload a document':
        uploaded_file = st.file_uploader("Upload a document to be checked, .txt and .pdf are supported", type=['txt', 'pdf'])

    if input_method == 'Enter text':
        youtube_url = st.text_input("Enter a text to be checked")

    api_key = st.text_input("Enter API key here, or contact the author if you don't have one.")
    st.markdown('[Author email](mailto:mohamedseifsalem@gmail.com)')
    use_gpt_4 = st.checkbox("Use GPT-4 for the final prompt (STRONGLY recommended, requires GPT-4 API access - progress bar will appear to get stuck as GPT-4 is slow)", value=True)
#    find_clusters = st.checkbox('Find optimal clusters (experimental, could save on token usage)', value=False)
    st.sidebar.markdown('# Made by: [Seif](https://github.com/seeifsalem)')
    st.sidebar.markdown('# Course: [Lean Startup Academy](https://www.kickbox.academy/)')
    st.sidebar.markdown("""""", unsafe_allow_html=True)

    if st.button('Summarize (click once and wait)'):
        process_summarize_button(uploaded_file, api_key, use_gpt_4)


def process_summarize_button(uploaded_file, api_key, use_gpt_4):
    """
    Processes the summarize button, and displays the summary if input and doc size are valid

    :param uploaded_file: The file uploaded by the user

    :param api_key: The API key entered by the user

    :param use_gpt_4: Whether to use GPT-4 or not

    :return: None
    """
    if not validate_input(uploaded_file, api_key, use_gpt_4):
        return

    with st.spinner("Summarizing... please wait..."):
        temp_file_path = create_temp_file(uploaded_file)
        llm = create_chat_model(api_key, use_gpt_4)
        initial_prompt_list = summary_prompt_creator(map_prompt, 'text', llm)
        final_prompt_list = summary_prompt_creator(combine_prompt, 'text', llm)
        doc = doc_loader(temp_file_path)

        if not validate_doc_size(doc):
            os.unlink(temp_file_path)
            return

        summary = doc_to_final_summary(doc, 10, initial_prompt_list, final_prompt_list, api_key, use_gpt_4)
        st.markdown(summary, unsafe_allow_html=True)
        os.unlink(temp_file_path)


def validate_doc_size(doc):
    """
    Validates the size of the document

    :param doc: doc to validate

    :return: True if the doc is valid, False otherwise
    """
    if not token_limit(doc, 120000):
        st.warning('File too big!')
        return False

    if not token_minimum(doc, 200):
        st.warning('File too small!')
        return False
    return True


def validate_input(uploaded_file, api_key, use_gpt_4):
    """
    Validates the user input, and displays warnings if the input is invalid

    :param uploaded_file: The file uploaded by the user

    :param api_key: The API key entered by the user

    :param use_gpt_4: Whether the user wants to use GPT-4

    :return: True if the input is valid, False otherwise
    """
    if uploaded_file is None:
        st.warning("Please upload a file.")
        return False

    if not check_key_validity(api_key):
        st.warning('Key not valid or API is down.')
        return False

    if use_gpt_4 and not check_gpt_4(api_key):
        st.warning('Key not valid for GPT-4.')
        return False

    return True


if __name__ == '__main__':
    main()