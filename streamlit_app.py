import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
import datetime
import aplast
import time
import extra_streamlit_components as stx

from streamlit_folium import folium_static
import os
import streamlit as st
from persist import persist, load_widget_state

from google.cloud import firestore


import datetime


default_params = {
    "weight_kg": 80,
    "swimming_sX100m": datetime.time(2, 0),
    "transition_swi2cyc_s": datetime.time(2, 0),
    "cycling_kmXh": 30,
    "transition_cyc2run_s": datetime.time(2, 0),
    "running_sXkm": datetime.time(5, 30),
}


@st.cache(allow_output_mutation=True)
def get_manager():
    return stx.CookieManager()


cookie_manager = get_manager()
athlete_config = cookie_manager.get_all()


st.set_option("deprecation.showPyplotGlobalUse", False)


if os.path.exists("/home/guydegnol/projects/trianer/trianer_db_credentials.json"):
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/home/guydegnol/projects/trianer/trianer_db_credentials.json"


info_box = st.empty()


def main():
    c1, c2, c3 = st.columns(3)

    with c1:
        st.subheader("Get Cookie:")
        cookie = st.text_input("Cookie", key="0")
        clicked = st.button("Get")
        if clicked:
            value = cookie_manager.get(cookie=cookie)
            st.write(value)
    with c2:
        st.subheader("Set Cookie:")
        cookie = st.text_input("Cookie", key="1")
        val = st.text_input("Value")
        if st.button("Add"):
            cookie_manager.set(cookie, val, expires_at=datetime.datetime(year=2023, month=2, day=2))
    with c3:
        st.subheader("Delete Cookie:")
        cookie = st.text_input("Cookie", key="2")
        if st.button("Delete"):
            cookie_manager.delete(cookie)


if __name__ == "__main__":
    main()
