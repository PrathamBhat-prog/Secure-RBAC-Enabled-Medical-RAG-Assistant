import streamlit as st
from dotenv import load_dotenv
import requests
from requests.auth import HTTPBasicAuth
import os


from pathlib import Path

# Load .env from root directory
env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

API_URL=os.getenv("API_URL")

if not API_URL:
    st.error("Error: API_URL is missing! Please add `API_URL=http://127.0.0.1:8000` to your .env file.")
    st.stop()

st.set_page_config(page_title="Healthcare RBAC RAG Chatbot",layout="centered")

# Session state initalization
if "username" not in st.session_state:
    st.session_state.username=""
    st.session_state.password=""
    st.session_state.role=""
    st.session_state.logged_in=False
    st.session_state.mode="auth"

# Auth header
def get_auth():
    return HTTPBasicAuth(st.session_state.username,st.session_state.password)

# Auth UI

def auth_ui():
    st.title("Healthcare RBAC RAG")
    st.subheader("Login or Signup")

    tab1,tab2=st.tabs(["Login","Signup"])

    # Login
    with tab1:
        username=st.text_input("Username",key="login_user")
        password=st.text_input("Password",type="password",key="login_pass")
        if st.button("Login"):
            res=requests.get(f"{API_URL}/login",auth=HTTPBasicAuth(username,password))
            if res.status_code==200:
                user_data=res.json()
                st.session_state.username=username
                st.session_state.password=password
                st.session_state.role=user_data["role"]
                st.session_state.logged_in=True
                st.session_state.mode="chat"
                st.success(f"Welcome {username}")
                st.rerun()
            else:
                try:
                    st.error(res.json().get("detail", "Login failed"))
                except ValueError:
                    st.error(f"Login failed (Server Error): {res.text}")


    # Signup
    with tab2:
        new_user=st.text_input("New Username",key="signup_user")
        new_pass=st.text_input("New Password",type="password",key="signup_pass")
        new_role=st.selectbox("Choose Role",["admin","doctor","nurse","patient","other"])
        if st.button("Signup"):
            payload={"username":new_user,"password":new_pass,"role":new_role}
            try:
                res=requests.post(f"{API_URL}/signup",json=payload)
                print(f"DEBUG: Status Code: {res.status_code}")
                print(f"DEBUG: Response Text: {res.text}")
                if res.status_code==200:
                    user_data=res.json()
                    st.success("Signup successful! You can login.")
                else:
                    st.error(f"Error {res.status_code}: {res.text}")
            except Exception as e:
                st.error(f"Request failed: {e}")



# Upload PDF (Admin only)
def upload_docs():
    st.subheader("Upload PDF for specific Role")
    uploaded_file=st.file_uploader("Choose a PDF file",type=["pdf"])
    role_for_doc=st.selectbox("Target Role dor docs",["admin", "doctor","nurse","patient","other"])

    if st.button("Upload Document"):
        if uploaded_file:
            files={"file":(uploaded_file.name,uploaded_file.getvalue(),"application/pdf")}
            data={"role":role_for_doc}
            res=requests.post(f"{API_URL}/upload_docs",files=files,data=data,auth=get_auth())
            if res.status_code==200:
                doc_info=res.json()
                st.success(f"Uploaded: {uploaded_file.name}")
                st.info(f"Doc Id : {doc_info['doc_id']},Access:{doc_info['accessible_to']}")
            else:
                try:
                    error_detail = res.json().get("detail", "Upload failed")
                except ValueError:
                    error_detail = f"Server Error ({res.status_code}): {res.text}"
                st.error(error_detail)
        else:
            st.warning("Please upload a file")



# chat interface
def chat_interface():
    st.subheader("Ask a healthcare question")
    msg=st.text_input("Your query")

    if st.button("Send"):
        if not msg.strip():
            st.warning("Please enter a query")
        
        try:
            res=requests.post(f"{API_URL}/chat",data={"message":msg},auth=get_auth())
            
            if res.status_code==200:
                reply=res.json()
                st.markdown('### Answer: ')
                st.success(reply["answer"])
                if reply.get("sources"):
                    for src in reply["sources"]:
                        st.write(f"--{src}")
            else:
                try:
                    error_detail = res.json().get("detail", "Something is wrong.")
                except ValueError:
                    error_detail = f"Server Error ({res.status_code}): {res.text}"
                st.error(error_detail)
        except Exception as e:
            st.error(f"Connection Error: {e}")


# main flow
if not st.session_state.logged_in:
    auth_ui()
else:
    st.title(f"Welcome , {st.session_state.username}")
    st.markdown(f"**Role**: `{st.session_state.role}`")
    if st.button("Logout"):
        st.session_state.logged_in=False
        st.session_state.username=""
        st.session_state.password=""
        st.session_state.role=""
        st.session_state.mode="auth"
        st.rerun()


    if st.session_state.role=="admin":
        upload_docs()
        st.divider()
        chat_interface()
    else:
        chat_interface()
