import streamlit as st
st.set_page_config(page_title="Algo App",layout="wide",initial_sidebar_state="expanded",)
st.markdown("""
  <style>
    .block-container {padding-top: 0.5rem;padding-bottom: 0rem;padding-left: 2rem;padding-right: 5rem;}
  </style>
  """, unsafe_allow_html=True)
import pyotp
from logzero import logger
from py5paisa import FivePaisaClient
cred={
    "APP_NAME":"5PGANESH",
    "APP_SOURCE":"151",
    "USER_ID":"jGpPvkKRRBu",
    "PASSWORD":"CH552StL6Np",
    "USER_KEY":"EWZRvRh5TTs6uaJcfngDwx1u3VMZ3EaQ",
    "ENCRYPTION_KEY":"gdH8fPb3H3oOAh8nYAA8GdmNtCpsMHVFdPfcyaxNiWiKoz1WSkbRSqoffmF6yIje"}
client = FivePaisaClient(cred=cred)
client.get_totp_session('53079505',pyotp.TOTP('GUZTANZZGUYDKXZVKBDUWRKZ').now(),'478963')
