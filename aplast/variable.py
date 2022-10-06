import datetime
import copy


class Variable:
    update_cookie = None
    cookies = {}

    @staticmethod
    def clone(var, key):
        v = copy.deepcopy(var)
        v.key = key
        return v

    def __init__(
        self, key=None, srange=[], help=None, label=None, default=None, orange=None, input_format=None
    ) -> None:
        self.key, self.srange, self.help, self.label, self.default = key, srange, help, label, default
        self.orange, self.input_format = orange, input_format

    def get_format_value(self, var):

        if self.input_format in ["checkbox", "expander"]:
            if type(var) == str and var not in ["false", "False"]:
                return True
            elif type(var) == bool:
                return var
            return False
        elif len(self.srange) == 0:
            return var
        elif self.srange[0] == "t" and type(var) == str and ":" in var:
            dtimes = str(var).split(":")
            return datetime.time(int(dtimes[0]), int(dtimes[1]))
        elif self.srange[0] == "t" and type(var) in [str, int, str]:
            return datetime.time(int(var), 0)
        elif self.srange[0] == "f" and type(var) in [str, int]:
            return float(var)
        elif self.srange[0] == "i" and type(var) in [str, float, int]:
            return int(var)
        elif self.srange[0] == "d" and type(var) in [str, float, int]:
            return int(var)
        elif self.srange[0] == "b" and type(var) in [str, float, int]:
            return bool(var)
        else:
            return var

    def get_key(self):
        return "trianer_" + self.key

    def get_init_value(self):
        var = Variable.cookies[self.get_key()] if self.get_key() in Variable.cookies else self.default
        var = self.get_format_value(var)
        # if type(var) == str:
        #    var = translate(var)

        return var

    def get_input(self, input_cls, **kwargs):
        import streamlit as st

        label = gl(self.key if self.label is None else self.label, u=True)
        srange = [gl(r) for r in self.srange]

        kwargs.update(dict(key=self.key, help=self.help, on_change=lambda: Variable.update_cookie(self.key)))

        # Set default value
        if input_cls in [st.selectbox, st.radio]:
            kwargs.update(dict(index=srange.index(self.get_init_value())))
        elif input_cls in [st.expander]:
            kwargs.update(dict(expanded=self.get_init_value()))
        elif input_cls in [st.multiselect]:
            irange = [gl(r) for r in self.get_init_value()]
            kwargs.update(dict(default=irange))
        else:
            kwargs.update(dict(value=self.get_init_value()))

        if input_cls in [st.radio]:
            kwargs.update(dict(horizontal=True))

        if input_cls in [st.selectbox, st.radio, st.multiselect]:
            kwargs.update(dict(options=srange))

        if input_cls in [st.slider, st.number_input]:
            smin_value, smax_value, sstep = self.get_range_values()
            kwargs.update(dict(min_value=smin_value, max_value=smax_value, step=sstep))

        return input_cls(label, **kwargs)

    def get_range_values(self):
        if type(self.srange) == list or self.srange is None or len(self.srange) == 0:
            return [0, 0, 0]

        stype, smin_value, smax_value, sstep = self.srange.split(":")
        if stype == "t":
            return (
                datetime.time(int(smin_value), 0),
                datetime.time(int(smax_value), 0),
                datetime.timedelta(minutes=int(sstep)),
            )
        elif stype == "d":
            return (
                datetime.date.today(),
                datetime.date.today() + datetime.timedelta(days=30),
                1,
            )
        elif stype == "i":
            return int(smin_value), int(smax_value), int(sstep)
        elif stype == "f":
            return float(smin_value), float(smax_value), float(sstep)
