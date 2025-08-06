
from .tcl_plots import TranportCrimePlots
from dash import Dash, html, dcc, Input, Output, State
import dash_bootstrap_components as dbc
import webbrowser, pandas as pd

plots = TranportCrimePlots()

class DashElements:
    def __init__(self):
        return None
    

    def generate_stats_card(self,title,value):
        return html.Div(dbc.Card([
            dbc.CardBody([
                html.P(children=value,
                       className="card-value",
                       #id=valueId,
                      style=dict(margin="0px", 
                                 fontSize="22px", 
                                 fontWeight="bold")),
                html.H4(children=title,
                       className="card-title",
                        #id=titleId,
                       style=dict(margin="0px", 
                                  fontSize="18px", 
                                  fontWeight="bold"))
            ], style=dict(textAlign="center"))
        ], style=dict(paddingBlock="10px", 
                     background_color="steelblue",
                     border = "none",
                     borderRadius="10px") 
        ))
    
    

    def make_card_elements(self):
        long_df = plots.make_long_df()
        df = plots.df
        value_df = long_df.loc[long_df["unit"]=="Vol"]

        req_modes = plots.get_available_modes()

        #avgCounts=value_df.loc[value_df["mode"].isin(req_modes)].groupby("mode")["value"].mean().reset_index()
        avg_values = long_df.loc[(long_df["unit"].isin(["Rate", "Vol"]))&
          (long_df["mode"].isin(req_modes))].groupby(["mode", "unit"])["value"].mean().reset_index()
        df=pd.pivot(avg_values,columns="unit", values="value", index="mode").reset_index()
        df["value"]=df["Vol"].astype(int).astype(str) + " / " + df["Rate"].astype(int).astype(str)

        titles=df["mode"].apply(lambda x: x.upper().replace("_", " "))

        #values=[f'{x:,.0f}' for x in df["value"]]

        cards={x:y for x,y in zip(titles, df["value"])}

        card_elements = []
        for title, value in cards.items():
            if not title == "ALL TRANSPORT MODES":
                card_elements.append(self.generate_stats_card(title, value))

        return card_elements
    
    def make_container_elements(self, title, background_color):
        return dbc.Row([
            dbc.Col(html.Div([
                dbc.CardBody([
                    html.H1(children=title,
                           className="card=title",
                           style={
                       "margin" : "0px",
                       "fontSize" : "24px",
                       "fontWeight" : "bold"
                   })
                ], style={"textAlign" : "center"})
            ], style = {
                "paddingBlock" : "10px",
                "background_color" : background_color,
                "border" : "none",
                "borderRadius" : "10px"
            }))
        ])
    
    
    @property
    def tab_style(self):
        return {
    'idle':{
        'borderRadius': '10px',
        'padding': '0px',
        'marginInline': '5px',
        'display':'flex',
        'alignItems':'center',
        'justifyContent':'center',
        'fontWeight': 'bold',
        'background_color': 'antiquewhite',
        'border':'none'
    },
    'active':{
        'borderRadius': '10px',
        'padding': '0px',
        'marginInline': '5px',
        'display':'flex',
        'alignItems':'center',
        'justifyContent':'center',
        'fontWeight': 'bold',
        'border':'none',
        'textDecoration': 'underline',
        'background_color': 'steelblue'
    }}
    
    def make_mode_tabs(self):
        tabs = ["overview"]
        tabs.extend(plots.get_available_modes())
        return [dcc.Tab(label=x.replace("_", " ").title(),
                       value=x.replace("_", "-").lower(),
                       style=self.tab_style["idle"],
                       selected_style=self.tab_style["active"]) for x in tabs]
    
    
    def get_overview_plots(self):
        
        return html.Div([
            html.Div([
                dcc.Graph(id="figure-1", figure=plots.bar_plot_crimes())
            ], style = {"width" : "100%", "display" : "inline-block"}),
            html.Div([
                dcc.Graph(id="figure-2", figure=plots.plot_yearly_journeys_and_crimes())
            ], style = {"width" : "100%", "display" : "inline-block"}),
            #html.Div([
             #   dcc.Graph(id="figure-3", figure=plots.plotOnboardsPie())
            #], style = {"width" : "100%", "display" : "inline-block"}),
            #html.Div([
             #   dcc.Graph(id="figure-4", figure=plots.plotOnboardsBar())
            #], style = {"width" : "50%", "display" : "inline-block"}),
            
        ])
    
    
    def get_plots_for_mode(self, mode):
        return html.Div([
            html.Div([
                dcc.Graph(id="figure-1", figure=plots.plot_crimes_by_mode(mode, plots.make_long_df(), plots.get_mode_colors()))
            ], style = {"width" : "100%", "display" : "inline-block"}),
            html.Div([
                dcc.Graph(id="figure-2", figure=plots.plot_crimes_vs_rate(mode))
            ], style = {"width" : "100%", "display" : "inline-block"}),
            #html.Div([
             #   dcc.Graph(id="figure-3", figure=plots.plotOnboardsPie())
            #], style = {"width" : "100%", "display" : "inline-block"}),
            #html.Div([
             #   dcc.Graph(id="figure-4", figure=plots.plotOnboardsBar())
            #], style = {"width" : "50%", "display" : "inline-block"}),
            
        ])
    
        
    

