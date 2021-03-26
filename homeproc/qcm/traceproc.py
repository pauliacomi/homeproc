import pandas as pd
import numpy as np
import pathlib
from dateutil import parser
from scipy.signal import find_peaks, peak_widths
import matplotlib.pyplot as plt
from tqdm import tqdm


def read_tracefiles(
    folder='traces', format=2, f0=9950000, f1=10010000, fc=5001
):

    traces = pd.DataFrame()

    if format == 2:
        for trace in tqdm(pathlib.Path(folder).glob('*.*')):
            df = pd.read_csv(trace, names=[parser.parse(trace.stem)])
            traces = pd.concat([traces, df], axis=1)

    elif format == 1:
        for trace in tqdm(pathlib.Path(folder).glob('*.*')):
            df = pd.read_csv(trace, names=[trace.name])
            traces[parser.parse(trace.name)] = df[trace.name]
        traces = traces.set_index(np.linspace(f0, f1, fc))

    return traces


def read_markerfile(file):

    if file.endswith(".txt"):
        markers = pd.read_csv(
            file, names=['day', 'hour', 'm_freq'], delim_whitespace=True
        )
        markers['time'] = markers['day'] + ' ' + markers['hour']
        markers = markers[['time', 'm_freq']].set_index(['time'])
        markers.index = pd.to_datetime(markers.index)

    elif file.endswith(".csv"):
        markers = pd.read_csv(
            file, names=['time', 'm_freq'], index_col='time', parse_dates=True
        )

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
        data=dict(t_freq=maxima, t_widths=widths),
        index=timestamps,
    )

    return trace_results
