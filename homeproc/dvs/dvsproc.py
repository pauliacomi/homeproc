import datetime
import pathlib as pth

import pandas as pd
import numpy as np
import plotly.graph_objects as go
from matplotlib import pyplot as plt
from itertools import cycle
import pygaps as pg
import ruptures as rpt
from dateutil import parser

from ..common import pairwise

__all__ = [
    'read_dvs_file',
    'get_change_points',
    'get_change_points_rpt',
    'calc_isotherm_data',
    'dvs_plot',
    'trim_meta',
    'get_loading',
    'remove_baseline',
    'get_act_T',
]

LP_BASELINES_PTH = pth.Path(
    r"~\OneDrive\Documents\Research Documents\Postdoc ICGM\Projects\CNES sensors\Data\General DVS\flow_baseline\baselines"
).expanduser()

important_meta = {
    "Method Name": "dvs_method_name",
    "Sample Name": "dvs_sample_name",
    "Sample Description": "dvs_sample_description",
    "Initial Mass [mg]": "dvs_initial_mass [mg]",
    "Raw Data File Created": "dvs_method_date",
    "User Name": "dvs_user_name",
    "Vapour": "dvs_adsorbate",
    "Vapour Pressure [Torr]": "dvs_p0 [torr]",
    "Control Mode": "dvs_control_mode",
    "columns": "col"
}


def read_dvs_file(path, offset=20):

    with open(path) as f:
        f.readline()

        dvsinfo = {}
        for i, line in enumerate(f.readlines()):
            key, val = map(str.strip, line.split(':', 1))
            dvsinfo[key] = val
            if i > 14:
                break

    dvsdata = pd.read_csv(
        path, encoding="cp1252", delimiter="\\t", skiprows=41
    )

    dvsinfo['columns'] = dict(
        time=dvsdata.columns[0],
        mass=dvsdata.columns[1],
        dmass=dvsdata.columns[2],
        dmdt=dvsdata.columns[3],
        t_inc_tgt=dvsdata.columns[4],
        t_inc=dvsdata.columns[5],
        t_heat_tgt=dvsdata.columns[6],
        t_heat=dvsdata.columns[7],
        p_rel_tgt=dvsdata.columns[8],
        p_rel=dvsdata.columns[9],
        p_abs_tgt=dvsdata.columns[10],
        p_abs=dvsdata.columns[11],
        p_vac=dvsdata.columns[12],
        p_low=dvsdata.columns[13],
        p_high=dvsdata.columns[14],
        v_flow_tgt=dvsdata.columns[15],
        v_flow=dvsdata.columns[16],
        g_flow_tgt=dvsdata.columns[17],
        g_flow=dvsdata.columns[18],
    )

    file_created = dvsinfo['Raw Data File Created'][:19]
    file_created = parser.parse(file_created) + datetime.timedelta(
        seconds=offset
    )

    dvsdata = dvsdata.set_index(
        file_created +
        pd.to_timedelta(dvsdata[dvsinfo['columns']['time']], unit='min')
    )
    dvsinfo = trim_meta(dvsinfo)

    return dvsinfo, dvsdata


def trim_meta(meta):
    return {
        important_meta[key]: val
        for key, val in meta.items()
        if key in important_meta
    }


def get_change_points_rpt(dvsdata, col, pen=0.5, width=300, **kwargs):

    datacol = dvsdata[col].fillna(0)
    algo = rpt.Window(model="l1", width=width, **kwargs).fit(datacol.values)
    chpoints = algo.predict(pen=pen)
    rpt.show.display(datacol.values, chpoints, figsize=(17, 6))

    return chpoints


def get_change_points(dvsdata, col, pen=0.5, width=300, **kwargs):

    datacol = dvsdata[col].fillna(0)
    diff = np.diff(datacol, prepend=datacol[0])
    chpoints = np.nonzero(diff)[0]

    fig, ax = plt.subplots(1, figsize=(17, 6))
    ax.plot(range(len(datacol)), datacol)
    colors = cycle(["#4286f4", "#f44174"])
    for (start, end), col in zip(pairwise(chpoints), colors):
        ax.axvspan(max(0, start - 0.5), end - 0.5, facecolor=col, alpha=0.2)

    return chpoints


def calc_isotherm_data(
    dvsdata, pcol, mcol, chpoints, extra_cols=None, offspts=10, meanpts=20
):

    mean = offspts + meanpts

    read_cols = {}

    read_cols['pressure'] = [
        dvsdata[pcol].iloc[n - mean:n - offspts].mean() for n in chpoints
    ]
    read_cols['loading'] = [
        dvsdata[mcol].iloc[n - mean:n - offspts].mean() for n in chpoints
    ]

    if extra_cols:
        for col in extra_cols:
            read_cols[col] = [
                dvsdata[col].iloc[n - mean:n - offspts].mean()
                for n in chpoints
            ]

    return pd.DataFrame(read_cols)


def get_act_T(dvsdata, tcol):
    return max(dvsdata[tcol])


def remove_baseline(iso_points, base_name):
    base_iso = pg.isotherm_from_csv(LP_BASELINES_PTH / base_name)
    base_iso.convert(pressure_unit='torr')
    adj_p = base_iso.loading_at(
        iso_points['pressure'], interpolation_type='slinear', interp_fill=0
    )
    return iso_points['loading'] - adj_p


def get_loading(iso_points, m0, c='loading'):
    return (iso_points[c] / m0 - 1)


def dvs_plot(data, y1, y2, y3, y4):

    fig = go.Figure()
    fig.update_layout(template="simple_white")

    # Add traces
    fig.add_trace(
        go.Scatter(x=data.index, y=data[y1], line=dict(color="blue"), name=y1)
    )
    fig.add_trace(
        go.Scatter(
            x=data.index,
            y=data[y2],
            line=dict(color="red"),
            name=y2,
            yaxis='y2'
        )
    )
    fig.add_trace(
        go.Scatter(
            x=data.index,
            y=data[y3],
            line=dict(color="black"),
            name=y3,
            yaxis='y3'
        )
    )
    fig.add_trace(
        go.Scatter(
            x=data.index,
            y=data[y4],
            line=dict(color="green"),
            name=y4,
            yaxis='y4'
        )
    )

    # Set x-axis title
    fig.update_xaxes(title_text="Time (min)", domain=[0.2, 0.8])

    afs = 12

    # Create y-axis objects
    fig.update_layout(
        yaxis=dict(
            title=dict(text=y1, standoff=0),
            titlefont=dict(color="blue", size=afs),
            tickfont=dict(color="blue", size=afs),
            # type='log'
        ),
        yaxis2=dict(
            title=dict(text=y2, standoff=0),
            titlefont=dict(color="red", size=afs),
            tickfont=dict(color="red", size=afs),
            anchor="free",
            overlaying="y",
            side="left",
            position=0.1
        ),
        yaxis3=dict(
            title=dict(text=y3, standoff=0),
            titlefont=dict(color="black", size=afs),
            tickfont=dict(color="black", size=afs),
            anchor="x",
            overlaying="y",
            side="right"
        ),
        yaxis4=dict(
            title=dict(text=y4, standoff=0),
            titlefont=dict(color="green", size=afs),
            tickfont=dict(color="green", size=afs),
            anchor="free",
            overlaying="y",
            side="right",
            position=0.925
        ),
    )

    fig.update_layout(
        legend=dict(
            orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1
        )
    )

    fig.update_layout(
        autosize=True,
        width=800,
        margin=dict(l=10, r=10, b=10, t=20, pad=4),
    )

    return fig
