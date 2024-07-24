#!/usr/bin/env python
# coding: utf-8

# In[3]:


from dashElements import *


# In[4]:


appElements=DashElements()

app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP], title="London Tranport Crime Dashboard")
server = app.server

app.layout = html.Div([
    appElements.makeContainerElements(title="London Transport Crime Dashboard", backgroundColor="antiquewhite"),
    
    dbc.Row([
        dbc.Col(dcc.Tabs(id="mode-tabs", 
                         value="overview", 
                         children=appElements.makeModeTabs(),
                        style={'marginTop': '15px', 
                               'width':'2000px',
                               'height':'50px'}))
    ]),
    
    appElements.makeContainerElements(title="Monthly Average Reported Crimes / Crimes Per Million Passenger Journeys", backgroundColor="steelblue"),
    
    
    dbc.Row(
        [dbc.Col(x, width=2) for x in appElements.makeCardElements()]
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

def getPlots(tab):
    if tab == "overview":
        return appElements.getOverViewPlots()
    else:
        tab = tab.replace("-", "_").lower()
        return appElements.getPlotsForMode(tab)


if __name__ == "__main__":
    #webbrowser.open_new("http://127.0.0.1:8051/")
    app.run(debug=True #,use_reloader=False, port=8051
                  )


# In[ ]:




