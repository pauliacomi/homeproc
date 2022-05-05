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
import pygaps.parsing as pgp
import ruptures as rpt
from dateutil import parser
from matplotlib import pyplot as plt

from ..common import pairwise, plot_transient

__all__ = [
    'read_dvs_file',
    'get_change_points',
    'calc_isotherm_data',
    'trim_meta',
    'get_loading',
    'remove_baseline',
    'get_act_T',
    'dvs_plot',
    'cols',
]

try:
    LP_BASELINES_PTH = pth.Path(
        r"~\OneDrive\Documents\Research Documents\Postdoc ICGM\Projects\CNES sensors\Data\DVS\General DVS\flow_baseline\baselines"
    ).expanduser()
except:
    LP_BASELINES_PTH = ""

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
    "columns": "columns"
}

cols = dict(
    time=0,
    mass=1,
    dmass=2,
    dmdt=3,
    t_inc_tgt=4,
    t_inc=5,
    t_heat_tgt=6,
    t_heat=7,
    p_rel_tgt=8,
    p_rel=9,
    p_abs_tgt=10,
    p_abs=11,
    p_vac=12,
    p_low=13,
    p_high=14,
    v_flow_tgt=15,
    v_flow=16,
    g_flow_tgt=17,
    g_flow=18,
    vlv_pos=32
)


def read_dvs_file(path, offset=20):
    """Read a DVS 'txt' file and return its metadata and data."""

    # Read metadata
    with open(path, encoding="cp1252") as f:
        f.readline()
        dvsinfo = {}
        for i, line in enumerate(f.readlines()):
            key, val = map(str.strip, line.split(':', 1))
            dvsinfo[key] = val
            if i > 14:
                break

    # Read data
    dvsdata = pd.read_csv(
        path,
        encoding="cp1252",
        delimiter="\\t",
        skiprows=41,
        engine='python',
    )

    # Add some other metadata
    # columns
    dvsinfo['columns'] = {k: dvsdata.columns[v] for k, v in cols.items()}
    # creation date
    file_created = dvsinfo['Raw Data File Created'][:19]
    file_created = parser.parse(file_created) + datetime.timedelta(seconds=offset)
    # Trim unneeded data
    dvsinfo = trim_meta(dvsinfo)
    # activation T
    dvsinfo['activation_temp [C]'] = get_act_T(dvsdata, dvsinfo['columns']['t_heat'])

    # Reindex data
    dvsdata = dvsdata.set_index(
        file_created + pd.to_timedelta(dvsdata[dvsinfo['columns']['time']], unit='min')
    )

    return dvsinfo, dvsdata


def get_act_T(dvsdata, tcol):
    """Find activation temperature as maximum temperature of data"""
    return max(dvsdata[tcol])


def trim_meta(meta):
    """Trim metadata to remove unnecessary values."""
    return {important_meta[key]: val for key, val in meta.items() if key in important_meta}


def dvs_plot(dvsinfo, dvsdata):
    """Plot kinetic DVS data."""
    fig = plot_transient(
        dvsdata,
        dvsinfo['columns']['mass'],
        dvsinfo['columns']['t_heat'],
        dvsinfo['columns']['p_abs'],
        dvsinfo['columns']['p_abs_tgt'],
    )
    fig.update_layout(yaxis2_range=[20, 200])  # set T
    return fig


def get_change_points(
    dvsdata,
    col,
    method="window",
    pen=0.5,
    width=300,
    log=False,
    **kwargs,
):
    """Find the change points in a data series (usually pressure)."""

    datacol = dvsdata[col].fillna(0)
    if log:
        datacol = np.log10(datacol)

    if method == "derivative":
        datacol = dvsdata[col].fillna(0)
        diff = np.diff(datacol, prepend=datacol[0])
        chpoints = np.nonzero(diff)[0]
        chpoints = np.append(chpoints, [len(datacol) - 1])

        fig, ax = plt.subplots(1, figsize=(17, 6))
        ax.plot(range(len(datacol)), datacol)
        colors = cycle(["#4286f4", "#f44174"])
        for (start, end), col in zip(pairwise(chpoints), colors):
            ax.axvspan(max(0, start - 0.5), end - 0.5, facecolor=col, alpha=0.2)

    elif method == "window":
        algo = rpt.Window(model="l1", width=width, **kwargs).fit(datacol.values)
        chpoints = algo.predict(pen=pen)
        rpt.show.display(datacol.values, chpoints, figsize=(17, 6))

    elif method == "binary_segment":
        algo = rpt.Binseg(model="l2", min_size=width, **kwargs).fit(datacol.values)
        chpoints = algo.predict(pen=pen)
        rpt.show.display(datacol.values, chpoints, figsize=(17, 6))

    else:
        raise BaseException("Incorrect method.")

    return chpoints


def get_loading(iso_points, m0, c='loading'):
    """Find loading by dividing by initial mass"""
    return (iso_points[c] / m0 - 1)


def calc_isotherm_data(dvsdata, pcol, mcol, chpoints, extra_cols=None, offspts=10, meanpts=20):
    """Select and average points to calculate isotherm data."""

    mean = offspts + meanpts

    read_cols = {}

    read_cols['pressure'] = [dvsdata[pcol].iloc[n - mean:n - offspts].mean() for n in chpoints]
    read_cols['loading'] = [dvsdata[mcol].iloc[n - mean:n - offspts].mean() for n in chpoints]

    if extra_cols:
        for col in extra_cols:
            read_cols[col] = [dvsdata[col].iloc[n - mean:n - offspts].mean() for n in chpoints]

    return pd.DataFrame(read_cols)


def remove_baseline(iso_points, base_name, folder_path=LP_BASELINES_PTH):
    """Remove isotherm baseline."""
    base_iso = pgp.isotherm_from_csv(pth.Path(folder_path) / base_name)
    base_iso.convert(pressure_unit='torr')
    adj_p = base_iso.loading_at(iso_points['pressure'], interpolation_type='slinear', interp_fill=0)
    return iso_points['loading'] - adj_p
