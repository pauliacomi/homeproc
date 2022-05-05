"""
Module comprising processing of IDE scans.

@author: Dr. Paul Iacomi
@date: Jan 2021
"""

__all__ = [
    "read_novo_file",
    "find_previous_scan",
    "plot_time_column",
    "plot_param_freq",
]

import re
from dateutil import parser

import numpy as np
import pandas as pd
import plotly.graph_objects as go

from matplotlib import cm


def read_novo_file(path: str):
    """Read a Novocontrol output file."""

    with open(path) as f:
        name, date, time = map(str.strip, f.readline().split(","))
        while True:
            if f.readline().strip().startswith("Fixed value"):
                break
        novo = pd.read_table(f)

    novo.columns = map(str.strip, novo.columns)
    novo.columns = [re.sub("\s\s+", " ", s) for s in novo.columns]

    col_time = "Time [s]"
    col_freq = "Freq. [Hz]"

    start = parser.parse(f"{date} {time}", dayfirst=True)
    freqs = novo[col_freq].unique()
    novo[col_time] = pd.to_timedelta(novo[col_time], unit="s") + start

    novo.set_index([col_time, col_freq], inplace=True)
    novo.index.rename(("time", "freq"), inplace=True)

    novoinfo = {
        "sample_name": name,
        "frequencies": freqs,
        "start_time": start,
        "parameters": novo.columns.to_list(),
    }

    return novoinfo, novo


def plot_time_column(
    data,
    column,
    frequencies,
    dvs_data=None,
    dvs_col=None,
    scale='log',
):
    """Plot an interactive graph of variables as a function of time."""

    fig = go.Figure(
        layout=dict(
            title=column,
            template="simple_white",
            width=800,
            margin=dict(l=20, r=10, b=10, t=60, pad=4),
            xaxis=dict(
                title=dict(text="Time (min)", ),
                domain=[0, 0.9],
                tickfont=dict(size=10),
            ),
            yaxis=dict(
                title=dict(
                    text=column,
                    standoff=0,
                ),
                type=scale,
            ),
        )
    )

    for freq in frequencies:
        part = data.loc[pd.IndexSlice[:, freq], :]
        part = part.reset_index(level='freq')

        fig.add_trace(go.Scatter(
            x=part.index,
            y=part[column],
            name=freq,
        ))

    if dvs_data is not None:
        fig.update_layout(yaxis2=dict(
            title=dvs_col,
            anchor="x",
            overlaying="y",
            side="right",
        ), )
        fig.add_trace(
            go.Scatter(
                x=dvs_data.index,
                y=dvs_data[dvs_col],
                line=dict(color="black"),
                name='pressure',
                yaxis="y2"
            ),
        )

    return fig


def find_previous_scan(data, time_before):
    scan = data.query("time < @time_before")\
                        .groupby(level='freq')\
                        .tail(1).droplevel(0)

    return scan


def plot_param_freq(datas, parameter, pressure):
    """Plot a parameter as a function of frequency."""

    pressure = np.asarray(pressure)

    colmap = cm.get_cmap('RdPu', len(pressure))
    colours = [f"rgba({c[0]},{c[1]},{c[2]},{c[3]})" for c in colmap(pressure / max(pressure))]

    fig = go.Figure(
        layout=dict(
            title=parameter,
            template="simple_white",
            xaxis=dict(
                title=dict(text="Frequency [hz]", ),
                type='log',
            ),
            yaxis=dict(
                title=dict(
                    text=parameter,
                    standoff=0,
                ),
                type='log',
            ),
            legend=dict(font=dict(size=10, color="black"))
        )
    )

    for ind, pres, col in zip(range(len(pressure)), pressure, colours):
        fig.add_trace(
            go.Scatter(
                x=datas.columns,
                y=datas.iloc[ind],
                name=f"{pres:.2f}",
                line={"color": col},
            ),
        )

    return fig
