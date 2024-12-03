import streamlit as st
from utils.embedding import Embedding
from utils.llm import LLM
from utils.resume_processor import ResumeProcessor
from typing import Optional
import tempfile
import os


class ChatInterface:
    def __init__(self):
        self.initialise_session_state()
        self.embedding = Embedding()
        self.llm = LLM()
        self.resume_processor = ResumeProcessor()

    def initialise_session_state(self):
        """Initialise streamlit session state variables"""
        if "messages" not in st.session_state:
            st.session_state.messages = [{
                "role": "assistant",
                "content": "Hey there! I'm you personal career coach. What position are you looking for? Please upload you resume & type the role you're interested in the chat input window and hit enter to start!"
            }]

        if "resume_uploaded" not in st.session_state:
            st.session_state.resume_uploaded = False

    def handle_file_upload(self) -> Optional[str]:
        """Handle resume pdf upload"""
        uploaded_file = st.file_uploader("Please upload your resume (PDF format)", type=["pdf"])

        if uploaded_file and not st.session_state.resume_uploaded:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
                tmp_file.write(uploaded_file.getvalue())
                tmp_path = tmp_file.name

            try:
                resume_text = self.resume_processor.process_resume(tmp_path)
                st.session_state.resume_uploaded = True
                return resume_text
            except Exception as e:
                st.error(f"Error processing resume: {str(e)}")
            finally:
                os.unlink(tmp_path)
        return None
    
    def render(self):
        """Render the chat interface"""
        st.title("Jobs AI")

        # Display chat messages
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
        
        # Resume upload button
        resume_text = self.handle_file_upload()
        if resume_text:
            st.success("Resume uploaded")

        # Chat input
        if prompt := st.chat_input("Type your message here ..."):
            st.session_state.messages.append({"role": "user", "content": prompt})

            try:
                # Process user input and generate response
                if st.session_state.resume_uploaded:
                    response = self.llm.generate_response(
                        prompt,
                        resume_text,
                        self.embedding.get_relevant_jobs(resume_text)
                    )
                else:
                    response = "Please upload your resume first to get personalised recommendations."

                # Add assistant response
                st.session_state.messages.append({"role": "assistant", "content": response})
                st.rerun()
            except Exception as e:
                st.error(f"Error processing request: {str(e)}")