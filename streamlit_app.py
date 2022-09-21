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


import datetime


st.set_option("deprecation.showPyplotGlobalUse", False)


@st.cache(allow_output_mutation=True, suppress_st_warning=True)
def get_manager():
    return stx.CookieManager()


cookie_manager = get_manager()
all_cookies = cookie_manager.get_all()


def update_cookie(key):
    val = st.session_state[key]
    fval = str(val) if type(val) == datetime.time else val
    cookie_manager.set(key, fval, expires_at=datetime.datetime(year=2023, month=2, day=2))


aplast.set_var_on_change_function(update_cookie)
aplast.set_var_cookies(all_cookies)


def main():

    with st.expander("Diving performance", expanded=True):
        col1, col2, col3 = st.columns(3)
        with col1:
            time_descent = aplast.get_var_slider("time_descent")

        with col2:
            depth_max = aplast.get_var_number("depth_max")

        with col3:
            time_ascent = aplast.get_var_slider("time_ascent")

    with st.expander("Gliding charecteristics", expanded=True):
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            depth_gliding_descent = aplast.get_var_number("depth_gliding_descent")

        with col2:
            depth_gliding_descent_error = aplast.get_var_number("depth_gliding_descent_error")

        with col3:
            depth_gliding_ascent = aplast.get_var_number("depth_gliding_ascent")

        with col4:
            depth_gliding_ascent_error = aplast.get_var_number("depth_gliding_ascent_error")

    with st.expander("Body specification"):
        col1, col2 = st.columns(2)
        with col1:
            volume_lungs = aplast.get_var_number("volume_lungs")
        with col2:
            mass_body = aplast.get_var_number("mass_body")

    with st.expander("Gear", expanded=True):
        col3, col4 = st.columns(2)
        with col3:
            mass_ballast = aplast.get_var_number("mass_ballast")
        with col4:
            thickness_suit = aplast.get_var_number("thickness_suit")

    d = aplast.Diver(
        data=dict(
            surname="John Doe",
            depth_max=depth_max,
            mass_body=mass_body,
            mass_ballast=mass_ballast,
            thickness_suit=thickness_suit,
            volume_lungs=volume_lungs,
            time_descent=time_descent,
            time_ascent=time_ascent,
            depth_gliding_descent=depth_gliding_descent,
            depth_gliding_descent_error=depth_gliding_descent_error,
            depth_gliding_ascent=depth_gliding_ascent,
            depth_gliding_ascent_error=depth_gliding_ascent_error,
        )
    )

    solution = d.minimize()
    time_total = d.time_descent + d.time_ascent

    with st.expander("Recommendations", expanded=True):
        col3, col4, col5, col6 = st.columns(4)
        with col3:
            st.metric(
                "mass_ballast_best",
                "%s kg" % solution["mass_ballast_best"],
                "%s kg" % (solution["mass_ballast_best"] - mass_ballast),
            )
        with col4:
            st.metric(
                "thickness_suit_best",
                "%s mm" % solution["thickness_suit_best"],
                "%s mm" % (solution["thickness_suit_best"] - thickness_suit),
            )
        with col5:
            st.metric(
                "Economy of power",
                "%.0f W" % (solution["work_best"] / time_total),
                "%.4f %% " % (100 * (solution["work_best"] - solution["work"]) / solution["work"]),
                delta_color="inverse",
            )

        with col6:
            st.metric(
                "Energy spent",
                "%.0f kJ" % (solution["work_best"] / 1000),
                "%.4f %%" % (100 * (solution["work_best"] - solution["work"]) / solution["work"]),
                delta_color="inverse",
            )
    # st.write("solution", solution)

    with st.expander("Trajectory", expanded=True):
        diver = d.data
        diver.update(
            {"mass_ballast": solution["mass_ballast_best"], "thickness_suit": solution["thickness_suit_best"]}
        )
        d_best = aplast.Diver(data=diver)

        # st.plotly_chart(aplast.trajectory.show_dynamic(d))
        st.pyplot(aplast.trajectory.show(d))
        st.pyplot(aplast.trajectory.show(d_best))

    with st.expander("Cookies management", expanded=True):
        st.write(all_cookies)
        cookie = st.text_input("Cookie", key="2")
        if st.button("Delete"):
            cookie_manager.delete(cookie)


if __name__ == "__main__":
    main()
