import streamlit as st

from ..variables import variables


def get_var_input(key, **kwargs):
    v = variables[key]
    input_format = getattr(st, v.input_format) if v.input_format else st.number_input
    return v.get_input(input_format, **kwargs)


def get_value(key):
    return variables[key].get_init_value()


def get_inputs(vars, options=[]):
    for p, col in enumerate(st.columns(len(vars))):
        with col:
            kwargs = options[p] if len(options) > p else {}
            get_var_input(vars[p], **kwargs)


def get_temperature_menu(race_choice):
    col1, col2, col3 = st.columns(3)
    with col1:
        atemp = get_var_input(f"temperature_menu_{race_choice}")
        is_manual_temp = gc(atemp) == "temp_manual"
        is_date_temp = gc(atemp) == "temp_from_date"
    with col2:
        temperature = get_var_input(f"temperature_{race_choice}", disabled=not is_manual_temp)
    with col3:
        get_var_input(f"dtemperature_{race_choice}", disabled=not is_date_temp)
    return temperature


def get_temperature(race_choice):
    return (
        None
        if get_value(f"temperature_menu_{race_choice}") == "temp_auto"
        else get_value(f"temperature_{race_choice}")
    )
