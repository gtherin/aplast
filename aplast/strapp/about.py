import streamlit as st

# from ..core.labels import gl, gc, Labels
# from . import inputs


def gl(name):
    return name


def get_expander():
    from ..__version__ import __version__ as version

    return st.expander(f"ℹ️ - {gl('about_app')} (pyversion={version})", expanded=False)


def get_content(all_cookies, cookie_manager):

    from ..__version__ import __version__ as version

    st.success(f"Version {version}")
    rd = open("./README.md", "r").read()
    st.markdown(rd)

    """
![alt text](./data/relative_intensity_vs_running_time.png "Title")

<img src="./data/relative_intensity_vs_running_time.png" alt="isolated" width="200"/>
<img src="../data/relative_intensity_vs_running_time.png" alt="isolated" width="200"/>
<img src="data/relative_intensity_vs_running_time.png" alt="isolated" width="200"/>
"""

    cl = open("./CHANGELOG.md", "r").read().split("[")
    st.markdown("[".join(cl[:3]))
    if st.checkbox("More changes history"):
        st.markdown("#### [" + "[".join(cl[3:]))

    if st.checkbox("Cookies management"):
        st.write(all_cookies)
        cookie = st.text_input("Cookie", key="Cookie list")
        if st.button("Delete a cookie"):
            cookie_manager.delete(cookie)

    # if inputs.get_var_input("beta_mode"):
    #    st.success(Labels.add_label(en="Beta mode is activated !", fr="Le mode beta est activé !"))


def get_section(all_cookies, cookie_manager):
    with get_expander():
        get_content(all_cookies, cookie_manager)
