#!/usr/bin/env python
import plotly.graph_objects as go


def surface(data, plot_title=""):
    fig = go.Figure(go.Surface(x=data[0], y=data[1], z=data[2]))
    fig.update_traces(colorscale="balance",
                      contours_z=dict(show=True, usecolormap=True, project_z=True))

    fig.update_layout(template="plotly_dark",
                      title_text=plot_title)

    return fig
