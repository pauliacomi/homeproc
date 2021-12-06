"""
Module comprising processing of DVS data files.

@author: Dr. Paul Iacomi
@date: Jan 2021
"""

import datetime
import pathlib as pth
from itertools import cycle

import numpy as np
import pandas as pd
import pygaps as pg
import pygaps.parsing as pgp
import ruptures as rpt
from dateutil import parser
from matplotlib import pyplot as plt

from ..common import pairwise, plot_transient

__all__ = [
    'read_dvs_file',
    'get_change_points',
    'get_change_points_rpt',
    'get_change_points_rpt_wnd',
    'calc_isotherm_data',
    'trim_meta',
    'get_loading',
    'remove_baseline',
    'get_act_T',
    'dvs_plot',
]

LP_BASELINES_PTH = pth.Path(
    r"~\OneDrive\Documents\Research Documents\Postdoc ICGM\Projects\CNES sensors\Data\DVS\General DVS\flow_baseline\baselines"
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

    dvsdata = pd.read_csv(path, encoding="cp1252", delimiter="\\t", skiprows=41, engine='python')

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
    file_created = parser.parse(file_created) + datetime.timedelta(seconds=offset)

    dvsdata = dvsdata.set_index(file_created + pd.to_timedelta(dvsdata[dvsinfo['columns']['time']], unit='min'))
    dvsinfo = trim_meta(dvsinfo)

    return dvsinfo, dvsdata


def trim_meta(meta):
    return {important_meta[key]: val for key, val in meta.items() if key in important_meta}


def get_change_points_rpt(dvsdata, col, pen=0.5, min_size=2, **kwargs):

    datacol = dvsdata[col].fillna(0)
    algo = rpt.Binseg(model="l2", min_size=min_size, **kwargs).fit(datacol.values)
    chpoints = algo.predict(pen=pen)
    rpt.show.display(datacol.values, chpoints, figsize=(17, 6))

    return chpoints


def get_change_points_rpt_wnd(dvsdata, col, pen=0.5, width=300, **kwargs):

    datacol = dvsdata[col].fillna(0)
    algo = rpt.Window(model="l1", width=width, **kwargs).fit(datacol.values)
    chpoints = algo.predict(pen=pen)
    rpt.show.display(datacol.values, chpoints, figsize=(17, 6))

    return chpoints


def get_change_points(dvsdata, col, pen=0.5, width=300, **kwargs):

    datacol = dvsdata[col].fillna(0)
    diff = np.diff(datacol, prepend=datacol[0])
    chpoints = np.nonzero(diff)[0]
    chpoints = np.append(chpoints, [len(datacol) - 1])

    fig, ax = plt.subplots(1, figsize=(17, 6))
    ax.plot(range(len(datacol)), datacol)
    colors = cycle(["#4286f4", "#f44174"])
    for (start, end), col in zip(pairwise(chpoints), colors):
        ax.axvspan(max(0, start - 0.5), end - 0.5, facecolor=col, alpha=0.2)

    return chpoints


def calc_isotherm_data(dvsdata, pcol, mcol, chpoints, extra_cols=None, offspts=10, meanpts=20):

    mean = offspts + meanpts

    read_cols = {}

    read_cols['pressure'] = [dvsdata[pcol].iloc[n - mean:n - offspts].mean() for n in chpoints]
    read_cols['loading'] = [dvsdata[mcol].iloc[n - mean:n - offspts].mean() for n in chpoints]

    if extra_cols:
        for col in extra_cols:
            read_cols[col] = [dvsdata[col].iloc[n - mean:n - offspts].mean() for n in chpoints]

    return pd.DataFrame(read_cols)


def get_act_T(dvsdata, tcol):
    return max(dvsdata[tcol])


def remove_baseline(iso_points, base_name, folder_path=LP_BASELINES_PTH):
    base_iso = pgp.isotherm_from_csv(pth.Path(folder_path) / base_name)
    base_iso.convert(pressure_unit='torr')
    adj_p = base_iso.loading_at(iso_points['pressure'], interpolation_type='slinear', interp_fill=0)
    return iso_points['loading'] - adj_p


def get_loading(iso_points, m0, c='loading'):
    return (iso_points[c] / m0 - 1)


def dvs_plot(dvsinfo, dvsdata):
    fig = plot_transient(
        dvsdata,
        dvsinfo['col']['mass'],
        dvsinfo['col']['t_heat'],
        dvsinfo['col']['p_abs'],
        dvsinfo['col']['p_abs_tgt'],
    )
    fig.update_layout(yaxis2_range=[20, 200])  # set T
    return fig
