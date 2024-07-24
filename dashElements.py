#!/usr/bin/env python
# coding: utf-8

# In[ ]:


from transportCrimePlots import TranportCrimePlots
from dash import Dash, html, dcc, Input, Output, State
import dash_bootstrap_components as dbc
import webbrowser, pandas as pd

plots = TranportCrimePlots()

class DashElements:
    def __init__(self):
        return None
    

    def generateStatsCard(self,title,value):
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
                     backgroundColor="steelblue",
                     border = "none",
                     borderRadius="10px") 
        ))
    
    

    def makeCardElements(self):
        longDf = plots.makeLongDf()
        df = plots.df
        valueDf = longDf.loc[longDf["unit"]=="Vol"]

        reqModes = plots.getAvailableModes()

        #avgCounts=valueDf.loc[valueDf["mode"].isin(reqModes)].groupby("mode")["value"].mean().reset_index()
        avgValues = longDf.loc[(longDf["unit"].isin(["Rate", "Vol"]))&
          (longDf["mode"].isin(reqModes))].groupby(["mode", "unit"])["value"].mean().reset_index()
        df=pd.pivot(avgValues,columns="unit", values="value", index="mode").reset_index()
        df["value"]=df["Vol"].astype(int).astype(str) + " / " + df["Rate"].astype(int).astype(str)

        titles=df["mode"].apply(lambda x: x.upper().replace("_", " "))

        #values=[f'{x:,.0f}' for x in df["value"]]

        cards={x:y for x,y in zip(titles, df["value"])}

        cardElements = []
        for title, value in cards.items():
            if not title == "ALL TRANSPORT MODES":
                cardElements.append(self.generateStatsCard(title, value))

        return cardElements
    
    def makeContainerElements(self, title, backgroundColor):
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
                "backgroundColor" : backgroundColor,
                "border" : "none",
                "borderRadius" : "10px"
            }))
        ])
    
    
    @property
    def tabStyle(self):
        return {
    'idle':{
        'borderRadius': '10px',
        'padding': '0px',
        'marginInline': '5px',
        'display':'flex',
        'alignItems':'center',
        'justifyContent':'center',
        'fontWeight': 'bold',
        'backgroundColor': 'antiquewhite',
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
        'backgroundColor': 'steelblue'
    }}
    
    def makeModeTabs(self):
        tabs = ["overview"]
        tabs.extend(plots.getAvailableModes())
        return [dcc.Tab(label=x.replace("_", " ").title(),
                       value=x.replace("_", "-").lower(),
                       style=self.tabStyle["idle"],
                       selected_style=self.tabStyle["active"]) for x in tabs]
    
    
    def getOverViewPlots(self):
        
        return html.Div([
            html.Div([
                dcc.Graph(id="figure-1", figure=plots.barPlotCrimes())
            ], style = {"width" : "100%", "display" : "inline-block"}),
            html.Div([
                dcc.Graph(id="figure-2", figure=plots.plotYearlyJourneysAndCrimes())
            ], style = {"width" : "100%", "display" : "inline-block"}),
            #html.Div([
             #   dcc.Graph(id="figure-3", figure=plots.plotOnboardsPie())
            #], style = {"width" : "100%", "display" : "inline-block"}),
            #html.Div([
             #   dcc.Graph(id="figure-4", figure=plots.plotOnboardsBar())
            #], style = {"width" : "50%", "display" : "inline-block"}),
            
        ])
    
    
    def getPlotsForMode(self, mode):
        return html.Div([
            html.Div([
                dcc.Graph(id="figure-1", figure=plots.plotCrimesByMode(mode, plots.makeLongDf(), plots.getModeColors()))
            ], style = {"width" : "100%", "display" : "inline-block"}),
            html.Div([
                dcc.Graph(id="figure-2", figure=plots.plotCrimesVsRate(mode))
            ], style = {"width" : "100%", "display" : "inline-block"}),
            #html.Div([
             #   dcc.Graph(id="figure-3", figure=plots.plotOnboardsPie())
            #], style = {"width" : "100%", "display" : "inline-block"}),
            #html.Div([
             #   dcc.Graph(id="figure-4", figure=plots.plotOnboardsBar())
            #], style = {"width" : "50%", "display" : "inline-block"}),
            
        ])
    
        
    

