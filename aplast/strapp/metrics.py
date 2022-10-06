import streamlit as st

from trianer.core.labels import gl, Labels


def get_metric(triathlon, discipline, label):
    r = triathlon.race.get_dinfo(discipline)
    if r[0] == 0:
        return
    a = triathlon.get_dinfo(discipline)
    if label == "header":
        st.subheader(gl(discipline))
    elif label == "distance":
        st.metric("Distance&D+", f"{r[0]:.2f}km", f"{r[1]:.0f}m", delta_color="off")
    elif label == "speed":
        txt = Labels.add_label(en="Speed&pace", fr="Vitesse&Allure")
        st.metric(
            txt,
            f"{a[0]:.2f}km/h",
            f"{a[1]:.0f}s/" + ("km" if discipline.lower() != "swimming" else "100m"),
            delta_color="off",
        )
    elif label == "duration":
        txt = Labels.add_label(en="Duration", fr="Durée")
        st.metric(txt, f"{a[2]:.0f}h{60 * (a[2] % 1):02.0f}min", f"{60*a[2]:.0f}min", delta_color="off")


def show_metrics(triathlon):

    disciplines = (
        triathlon.race.disciplines + ["Total"] if len(triathlon.race.disciplines) > 1 else triathlon.race.disciplines
    )

    metrics = ["header", "distance", "speed", "duration"]
    for discipline in disciplines:
        cols = st.columns(len(metrics))
        for c, metric in enumerate(metrics):
            with cols[c]:
                get_metric(triathlon, discipline, metric)
