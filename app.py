import streamlit as st
import requests

st.title("🔎 진짜 서버 IP 확인")
try:
    ip = requests.get('https://api.ipify.org').text
    st.code(ip, language="text")
except:
    st.error("확인 실패")
