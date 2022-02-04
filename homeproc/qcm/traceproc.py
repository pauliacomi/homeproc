"""
Module comprising processing of QCM traces and markers.

@author: Dr. Paul Iacomi
@date: Jan 2021
"""

import pathlib

import numpy as np
import pandas as pd
import scipy.signal as sig
import plotly.graph_objects as go
from dateutil import parser
from scipy.signal import find_peaks, peak_widths
from tqdm import tqdm

__all__ = [
    'read_tracefiles',
    'denoise_signal',
    'read_markerfile',
    'calc_tracedata',
    'plot_qcm',
    'FREQ_COL',
    'WIDTH_COL',
]

FREQ_COL = "Resonance frequency [Hz]"
WIDTH_COL = "Peak width [Hz]"


def read_tracefiles(folder='traces', format=2, f0=9950000, f1=10010000, fc=5001):

    trace_dfs = []

    if format == 2:
        for trace in tqdm(pathlib.Path(folder).glob('*.*')):
            df = pd.read_csv(trace, names=[parser.parse(trace.stem)])
            trace_dfs.append(df)

        minpoint = min(df.index.min() for df in trace_dfs)
        maxpoint = max(df.index.max() for df in trace_dfs)
        newind = np.linspace(minpoint, maxpoint, 2000)

        for ind, df in enumerate(trace_dfs):
            df_new = pd.DataFrame(index=newind)
            df_new.index.name = df.index.name
            df_new[df.columns[0]] = np.interp(newind, df.index, df[df.columns[0]])
            trace_dfs[ind] = df_new

        traces = pd.concat(trace_dfs, axis=1)

    elif format == 1:
        traces = pd.DataFrame()
        for trace in tqdm(pathlib.Path(folder).glob('*.*')):
            df = pd.read_csv(trace, names=[trace.name])
            traces[parser.parse(trace.name)] = df[trace.name]
        traces = traces.set_index(np.linspace(f0, f1, fc))

    return traces


def read_markerfile(file):

    if file.endswith(".txt"):
        markers = pd.read_csv(file, names=['day', 'hour', FREQ_COL], delim_whitespace=True)
        markers['time'] = markers['day'] + ' ' + markers['hour']
        markers = markers[['time', FREQ_COL]].set_index(['time'])
        markers.index = pd.to_datetime(markers.index)

    elif file.endswith(".csv"):
        markers = pd.read_csv(file, names=['time', FREQ_COL], index_col='time', parse_dates=True)

    return markers


def calc_tracedata(traces, pwidth=10, pheight=0.1):

    timestamps = []
    maxima = []
    widths = []

    for exp in traces.columns:

        x = traces.index
        y = traces[exp].values

        peaks, properties = find_peaks(y, width=pwidth, height=pheight)
        results_half = peak_widths(y, peaks, rel_height=0.5)

        timestamps.append(exp)
        try:
            maxima.append(x[peaks].values[0])
            widths.append(results_half[0][0])
        except:
            maxima.append(0)
            widths.append(0)

    trace_results = pd.DataFrame(
        data={
            FREQ_COL: maxima,
            WIDTH_COL: widths
        },
        index=timestamps,
    )

    return trace_results


def denoise_signal(signal, window=51, order=2):
    return sig.savgol_filter(signal, window, order)


def plot_qcm(markers, trace_results):

    return go.Figure(
        data=(
            go.Scatter(
                x=markers.index,
                y=markers[FREQ_COL],
                line=dict(color="black"),
                name="marker freq",
            ),
            go.Scatter(
                x=trace_results.index,
                y=trace_results[FREQ_COL],
                line=dict(color="green"),
                name="trace freq",
            ),
            go.Scatter(
                x=trace_results.index,
                y=trace_results[WIDTH_COL],
                line=dict(color="red"),
                name="trace width",
                yaxis='y2'
            ),
        ),
        layout=dict(
            template="simple_white",
            autosize=True,
            width=600,
            margin=dict(l=10, r=10, b=10, t=20, pad=4),
            xaxis=dict(
                title_text="Time (min)",
                domain=[0.1, 0.9],
            ),
            yaxis=dict(
                title=dict(text=FREQ_COL, standoff=0),
                titlefont=dict(color="green", size=12),
                tickfont=dict(color="green", size=12),
            ),
            yaxis2=dict(
                title=dict(text=WIDTH_COL, standoff=0),
                titlefont=dict(color="red", size=12),
                tickfont=dict(color="red", size=12),
                anchor="x",
                overlaying="y",
                side="right"
            ),
            legend=dict(
                orientation="h",
                x=1,
                y=1.02,
                yanchor="bottom",
                xanchor="right",
            )
        )
    )