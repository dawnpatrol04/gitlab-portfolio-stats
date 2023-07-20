import dash
import dash_bootstrap_components as dbc
from dash import dcc
from dash import html
import pandas as pd
import plotly.graph_objs as go
from plotly.subplots import make_subplots

# Data (Placeholder)
df = pd.DataFrame({
    'Date': pd.date_range(start='1/1/2020', periods=24, freq='M'),
    'Growth': [0.05 * i for i in range(24)],
    'Cumulative Total': [100 * 1.05 ** i for i in range(24)],
})

# Dash App
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.CYBORG])

# Create growth over time chart
growth_chart = go.Scatter(x=df['Date'], y=df['Growth'], name='% Growth', 
                          line=dict(color='firebrick', width=2))

# Create cumulative total over time chart
cumulative_chart = go.Scatter(x=df['Date'], y=df['Cumulative Total'], name='Cumulative Total', 
                              line=dict(color='goldenrod', width=2))

# Combine charts into a subplot figure
fig = make_subplots(rows=2, cols=1, subplot_titles=("% Growth Over Time", "Cumulative Total Over Time"))
fig.add_trace(growth_chart, row=1, col=1)
fig.add_trace(cumulative_chart, row=2, col=1)

# Styling the figure layout
fig.update_layout(
    autosize=False,
    width=800,
    height=600,
    margin=dict(l=50, r=50, b=100, t=100, pad=4),
    paper_bgcolor="Black",  # background color
    font=dict(color="white"),  # Font color
)

# Create dash layout
app.layout = html.Div(
    children=[
        html.H1(children="My Stylish Dashboard", style={"textAlign": "center", "color": "white"}),
        dcc.Graph(id="growth_cumulative", figure=fig),
    ],
    style={"background-color": "#000000"},
)

# Run app
if __name__ == "__main__":
    app.run_server(debug=True)
