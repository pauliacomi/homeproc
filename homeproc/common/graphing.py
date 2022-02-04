"""
Module comprising general plotting utilities.

@author: Dr. Paul Iacomi
@date: Jan 2021
"""

__all__ = [
    "plot_transient",
]

import plotly.graph_objects as go


def plot_transient(data, y1=None, y2=None, y3=None, y4=None):

    pdata = []
    layout = dict(
        template="simple_white",
        autosize=True,
        width=800,
        margin=dict(l=10, r=10, b=10, t=20, pad=4),
        xaxis=dict(
            title_text="Time (min)",
            domain=[0.2, 0.8],
        ),
        legend=dict(
            orientation="h",
            x=1,
            y=1.02,
            yanchor="bottom",
            xanchor="right",
        )
    )
    afs = 12

    if y1:
        pdata.append(go.Scatter(
            x=data.index,
            y=data[y1],
            line=dict(color="blue"),
            name=y1,
        ))
        layout['yaxis'] = dict(
            title=dict(text=y1, standoff=0),
            titlefont=dict(color="blue", size=afs),
            tickfont=dict(color="blue", size=afs),
        )
    if y2:
        pdata.append(
            go.Scatter(
                x=data.index,
                y=data[y2],
                line=dict(color="red"),
                name=y2,
                yaxis='y2',
            )
        )
        layout['yaxis2'] = dict(
            title=dict(text=y2, standoff=0),
            titlefont=dict(color="red", size=afs),
            tickfont=dict(color="red", size=afs),
            anchor="free",
            overlaying="y",
            side="left",
            position=0.1
        )
    if y3:
        pdata.append(
            go.Scatter(
                x=data.index,
                y=data[y3],
                line=dict(color="black"),
                name=y3,
                yaxis='y3',
            )
        )
        layout['yaxis3'] = dict(
            title=dict(text=y3, standoff=0),
            titlefont=dict(color="black", size=afs),
            tickfont=dict(color="black", size=afs),
            anchor="x",
            overlaying="y",
            side="right"
        )
    if y4:
        pdata.append(
            go.Scatter(
                x=data.index,
                y=data[y4],
                line=dict(color="green"),
                name=y4,
                yaxis='y4',
            )
        )
        layout['yaxis4'] = dict(
            title=dict(text=y4, standoff=0),
            titlefont=dict(color="green", size=afs),
            tickfont=dict(color="green", size=afs),
            anchor="free",
            overlaying="y",
            side="right",
            position=0.925
        )
    return go.Figure(
        data=pdata,
        layout=layout,
    )
