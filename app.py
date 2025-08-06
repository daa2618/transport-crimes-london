from pathlib import Path
import sys
pardir = Path(__file__).resolve().parent.parent
if not str(pardir) in sys.path:
    sys.path.insert(0, str(pardir))
from elements.dash_elements import *


app_elements=DashElements()

app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP], title="London Tranport Crime Dashboard")
server = app.server

app.layout = html.Div([
    app_elements.make_container_elements(title="London Transport Crime Dashboard", background_color="antiquewhite"),
    
    dbc.Row([
        dbc.Col(dcc.Tabs(id="mode-tabs", 
                         value="overview", 
                         children=app_elements.make_mode_tabs(),
                        style={'marginTop': '15px', 
                               'width':'2000px',
                               'height':'50px'}))
    ]),
    
    app_elements.make_container_elements(title="Monthly Average Reported Crimes / Crimes Per Million Passenger Journeys", background_color="steelblue"),
    
    
    dbc.Row(
        [dbc.Col(x, width=2) for x in app_elements.make_card_elements()]
    , style=dict(marginBlock="10px")),
    
    
    dbc.Row([
        dcc.Loading([
            html.Div(id="tabs-content")
        ], type = "default", color="steelblue")
    ]),    
        
    
], style = {"backgroundColor" : "black", "minHeight" : "100vh"})

@app.callback(Output("tabs-content", "children"),
             Input("mode-tabs", "value"),
             )

def getPlots(tab:str):
    if tab == "overview":
        return app_elements.get_overview_plots()
    else:
        tab = tab.replace("-", "_").lower()
        return app_elements.get_plots_for_mode(tab)


if __name__ == "__main__":
    webbrowser.open_new("http://127.0.0.1:8051/")
    app.run(debug=True ,use_reloader=False, port=8051
                  )

