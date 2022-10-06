import streamlit as st
import hydralit_components as hc
import extra_streamlit_components as stx

from ..core.labels import gl


class Menu:
    def __init__(self, use_nav_bar=False, beta_mode=False):

        # specify the primary menu definition
        menu_data = [
            {"id": "athlete", "icon": "💗"},
            {"id": "race", "icon": "🌍"},
            {"id": "perf", "icon": "🏊🚴🏃"},
            {"id": "simulation", "icon": "🏆"},
        ]
        self.beta_mode = beta_mode
        if beta_mode:
            menu_data.append({"id": "training", "icon": "💦"})

        self.menu_steps = [self.get_label(m["id"]) for m in menu_data]

        for m in menu_data:
            m["label"] = self.get_label(m["id"])

        if use_nav_bar:
            self.menu_id = hc.nav_bar(
                menu_definition=menu_data,
                override_theme={"txc_inactive": "#FFFFFF"},
                hide_streamlit_markers=False,
                sticky_nav=True,
                sticky_mode="pinned",
            )
        else:
            self.menu_id = stx.stepper_bar(steps=self.menu_steps)

    def get_label(self, code):
        return gl(code)[:4] + "." if self.beta_mode else gl(code)

    def is_menu(self, code):
        def is_menu_str(c):
            l = self.get_label(c)
            if l not in self.menu_steps:
                return False

            return l not in self.menu_steps or self.menu_id == l or self.menu_id == self.menu_steps.index(l)

        if type(code) is list:
            for c in code:
                if is_menu_str(c):
                    return True
            return False
        else:
            return is_menu_str(code)
