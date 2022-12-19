import numpy as np
import pandas as pd
import scipy as sp
import matplotlib.pyplot as plt
from matplotlib.patches import Circle
from matplotlib.patheffects import withStroke

import os

from . import constants


def get_trajectory(time_descent, time_ascent, max_depth) -> pd.Series:
    x = np.arange(0, time_descent)
    y = -max_depth * np.arange(0, time_descent) / time_descent

    x2 = np.arange(0, time_ascent) + time_descent
    y2 = max_depth * np.arange(0, time_ascent) / time_ascent - max_depth

    x3 = np.append(x, x2)
    y3 = np.append(y, y2)
    return pd.Series(y3, index=x3)


def show_dynamic(diver):

    import plotly.graph_objects as go
    import numpy as np

    x = np.concatenate([np.linspace(0, 90, 90), np.linspace(90, 170, 80)], axis=0)
    y = -125 * np.concatenate([np.linspace(0, 1, 100), np.linspace(1, 0, 80)], axis=0)

    xx = x  # [::2]
    yy = y  # [::2]
    N = len(xx)

    # Create figure
    fig = go.Figure(
        data=[
            go.Scatter(x=x, y=y, mode="lines", line=dict(width=2, color="blue"), name="Diver"),
            go.Scatter(x=x, y=y, mode="lines", line=dict(width=2, color="blue"), name="Trajectory"),
        ],
        layout=go.Layout(
            xaxis=dict(range=[-1, 175], autorange=False, zeroline=False),
            yaxis=dict(range=[-130, 1], autorange=False, zeroline=False),
            hovermode="closest",
            updatemenus=[dict(type="buttons", buttons=[dict(label="Play", method="animate", args=[None])])],
        ),
        frames=[
            go.Frame(data=[go.Scatter(x=[xx[k]], y=[yy[k]], mode="markers", marker=dict(color="red", size=20))])
            for k in range(N)
        ],
    )
    return fig


def show(diver):

    royal_blue = [0, 20 / 256, 82 / 256]

    fig, ax = plt.subplots(figsize=(15, 5))
    ax.tick_params(which="major", width=1.0, length=10, labelsize=14)
    ax.tick_params(which="minor", width=1.0, length=5, labelsize=10, labelcolor="0.25")

    ax.grid(linestyle="--", linewidth=0.5, color=".25", zorder=-10)

    print(diver.time_ascent)
    depth_max = diver.depth_max  # in m
    time_descent = diver.time_descent  # in sec
    time_ascent = diver.time_ascent  # in sec

    track = get_trajectory(time_descent, time_ascent, depth_max)

    ydee = diver.depth_gliding_descent.n
    xdee = track[track + ydee < 0].index[0]

    yaee = diver.depth_gliding_ascent.n
    xaee = track[track + yaee < 0].index[-1]

    track1 = np.ma.masked_where(track.index <= xdee, track)
    track2 = np.ma.masked_where((track.index > xdee) & (track.index < xaee), track)

    ax.plot(track.index, track1, track.index, track2, lw=2.5)

    ax.set_title(f"Position-time estimation", fontsize=20, verticalalignment="bottom")
    ax.set_xlabel("Time in seconds", fontsize=14)
    ax.set_ylabel("Depth in meters", fontsize=14)

    def annotate(x, y, text):
        ax.add_artist(
            Circle(
                (x, y),
                radius=10.15,
                clip_on=False,
                linewidth=2.5,
                edgecolor=royal_blue + [0.6],
                facecolor="none",
                path_effects=[withStroke(linewidth=7, foreground="white")],
            )
        )

        ax.text(
            x,
            y - 0.2,
            text,
            ha="center",
            va="top",
            weight="bold",
            color=royal_blue,
        )

    annotate(xdee, -ydee, "Equilibrium")
    annotate(xaee, -yaee, "Equilibrium")

    filename = constants.get_file("diver.png")

    print(filename)

    if filename:
        newax = fig.add_axes([0.3, 0.33, 0.15, 0.15], anchor="NE")
        newax.imshow(sp.ndimage.rotate(plt.imread(filename), 50))
        newax.axis("off")

        newax = fig.add_axes([0.6, 0.33, 0.15, 0.15], anchor="NE")
        newax.imshow(sp.ndimage.rotate(plt.imread(filename), 130))
        newax.axis("off")

    # plt.show()
