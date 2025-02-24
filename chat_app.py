import streamlit as st
import os
from azure.ai.inference import ChatCompletionsClient
import time
from azure.core.credentials import AzureKeyCredential

# Page configuration
st.set_page_config(page_title="Deepseek Chatbot", page_icon="🤖")

# Initialize Azure client
def init_azure_client():
    api_key = ('x1f9HKK4UHFsEQHDzux1QLA0GNd8qTUT')
    if not api_key:
        st.error("Azure API key not found. Please set the AZURE_INFERENCE_CREDENTIAL environment variable.")
        return None
    
    return ChatCompletionsClient(
        endpoint='https://DeepSeek-R1-jr.eastus2.models.ai.azure.com',
        credential=AzureKeyCredential(api_key)
    )

# Initialize session state for chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

def get_bot_response(client, messages):
    payload = {
        "messages": messages,
        "max_tokens": 2048,
        "temperature": 0.6,
        "top_p": 1,
        "stream": True
    }
    
    try:
        # Create placeholder for streaming output
        message_placeholder = st.empty()
        full_response = ""
        
        # Get streaming response
        stream_response = client.complete(**payload)
        
        # Process the stream
        for chunk in stream_response:
            if chunk.choices and hasattr(chunk.choices[0], 'delta'):
                if chunk.choices[0].delta.content:
                    content = chunk.choices[0].delta.content
                    # Stream character by character
                    for char in content:
                        full_response += char
                        # Update display with cursor effect
                        message_placeholder.markdown(full_response + "▌")
                        time.sleep(0.1)  # Add small delay for visibility
        
        # Final update without cursor
        message_placeholder.markdown(full_response)
        return full_response
    except Exception as e:
        return f"Error: {str(e)}"

def main():
    st.title("🤖 Deepseek Chatbot")
    
    # Initialize Azure client
    client = init_azure_client()
    if not client:
        return

    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Chat input
    if prompt := st.chat_input("What would you like to know?"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Get bot response with streaming
        with st.chat_message("assistant"):
            response = get_bot_response(client, st.session_state.messages)
            
        # Add to chat history after complete response
        st.session_state.messages.append({"role": "assistant", "content": response})


if __name__ == "__main__":
    main()