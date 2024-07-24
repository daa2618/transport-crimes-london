#!/usr/bin/env python
# coding: utf-8

# In[ ]:


from transportCrimeLondon import TransportCrimeLondon
import re, sys, os, datetime, numpy as np
#sys.path.append(os.path.join(git.Repo(".", search_parent_directories=True).working_tree_dir, "Plotly"))
from plotlyImports import *
#from savePlot import SavePlot

class TransportCrimePlotData:
    def __init__(self):
        self.df = TransportCrimeLondon().getTransportCrimesData()
        
    def makeLongDf(self):
        longDf=pd.melt(self.df, id_vars=["monthYear", "unit", "fy", "startYear", "endYear", "date", "year", "month"]).rename(columns={"variable" : "mode"})
        
        return longDf
    
    def getAllTranportModes(self):
        return self.makeLongDf()["mode"].unique()
    
    def getModeColors(self):
        modes = self.getAllTranportModes()
        colors = {x:y for x,y in zip(modes, px.colors.qualitative.Dark24)}
        return colors
    
    def getAvailableModes(self):
        reqModes = self.df.iloc[-1][self.df.iloc[-1].notna()].index
        modes = self.makeLongDf()["mode"].unique()
        return list(set(modes).intersection(reqModes))
    
    def getTripsByYear(self):
        longDf = self.makeLongDf()
        for monthYear in longDf["monthYear"].unique():
            longDf.loc[(longDf["monthYear"]==monthYear)&
                  (longDf["unit"]=="Vol")&
                  (longDf["mode"]=="all_transport_modes"), "value"] = longDf.loc[(longDf["monthYear"]==monthYear)&
                      (longDf["unit"]=="Vol")&
                      (longDf["mode"]!="all_transport_modes"), "value"].sum()

            longDf.loc[(longDf["monthYear"]==monthYear)&
                  (longDf["unit"]=="passengerJourneys")&
                  (longDf["mode"]=="all_transport_modes"), "value"] = longDf.loc[(longDf["monthYear"]==monthYear)&
                      (longDf["unit"]=="passengerJourneys")&
                      (longDf["mode"]!="all_transport_modes"), "value"].sum()
            
        df=longDf.loc[longDf["unit"].isin(["Vol", "passengerJourneys"])].groupby(["year", "unit"])["value"].sum().reset_index().rename(columns={"value":"observation"})

        df=pd.pivot(df, columns="unit", index="year", values="observation").reset_index()

        df["Rate"]=(df["Vol"] / df["passengerJourneys"]) * 1000000
        
        
        return df

class TranportCrimePlots(TransportCrimePlotData):
    def __init__(self):
        self.df = TransportCrimeLondon().getTransportCrimesData()
        return None
        #super().__init__(self.df)
        
        
    def makeHoverTemplateForTime(self, time):
        if time == "month":
            return "<b>Month :</b> %{customdata[0]}<br>"
        elif time == "year":
            return "<b>Year :</b> %{customdata[0]}<br>"
        
    def updateMonthAxes(self, fig, time):
        
        if time == "month":
            fig = fig.update_xaxes(tickmode="array",
                            categoryarray=["Jan", "Feb", "Mar", "Apr", "May", "Jun",
                                          "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"])
            return fig
        else:
            return fig
        
        
        
    def plotMonthlyAverageCrimes(self, time):
        longDf = self.makeLongDf()
        reqModes = self.getAvailableModes()
        
        groupedDf = longDf.loc[(longDf["unit"]=="Vol") & 
                      (longDf["mode"].isin(reqModes))].groupby([time, "mode"])["value"].mean().dropna().reset_index()

        fig = go.Figure()
        colors = self.getModeColors()
        
        for mode in groupedDf["mode"].unique():
            if mode != "all_transport_modes":
                filtered = groupedDf.loc[groupedDf["mode"]==mode]
                fig.add_trace(go.Bar(x=filtered[time],
                                    y=filtered["value"],
                                    name=mode,
                                    marker_color=colors[mode],
                                    customdata=filtered[[time, "mode"]],
                                         hovertemplate=self.makeHoverTemplateForTime(time)+
                                         "<b>Tranport Mode :</b> %{customdata[1]}<br>" + 
                                         "<b>Reported Crimes : </b> %{y:,.0f}<br>" +
                                         "<extra></extra>"))

        fig.update_layout(barmode="stack", 
                          #barnorm="percent",
                          title=f"<b>Monthly Average Reported Crimes</b><br><sup>By {time.title()} and Transport Mode</sup>",
                          legend=dict(title="Transport Modes",
                                                      orientation="h"))
        fig.update_xaxes(title=time, tickvals=(groupedDf[time].unique()))
        fig.update_yaxes(title="Reported Crimes")
        fig = self.updateMonthAxes(fig, time)
        return fig
    
    
    def plotCrimesVsRate(self, mode):
        longDf = self.makeLongDf()
        
        fig = make_subplots(specs=[[{"secondary_y" : True}]])

        colors = {x:y for x,y in zip(longDf["unit"].unique(), ["steelblue", "antiquewhite"])}

        filtered = longDf.loc[longDf["mode"]==mode].dropna()
        units=longDf["unit"].unique()
        valueDf = filtered.loc[filtered["unit"]==units[0]]

        fig.add_trace(go.Scatter(y=valueDf["value"],
                        x=np.array(valueDf["date"]),
                        marker_color=colors[units[0]],

                            mode="markers+lines",
                            name="Reported Crimes",
                                 meta="Reported Crimes",
                                ))
        valueDf = filtered.loc[filtered["unit"]==units[1]]
        fig.add_trace(go.Scatter(y=valueDf["value"],
                        x=np.array(valueDf["date"]),
                        marker_color=colors[units[1]],

                            mode="markers+lines",
                            name="Crimes Per Million Passenger Journeys",
                                meta="Crimes Per Million Passenger Journeys"),
                     secondary_y=True)


        fig.update_yaxes(tickmode="sync")
        fig.update_yaxes(title="Reported Crimes")
        fig.update_yaxes(title="Rate", secondary_y=True)
        fig.update_xaxes(title="Month")
        fig.update_layout(title=f"<b>Reported Volume Vs. Rate of Crimes per Million Passenger Journeys - {mode.replace('_', ' ').title()}",
                         legend=dict(orientation="h", x=0.3)
                         )
        
        fig.update_traces(hovertemplate="<b>Month :</b> %{x}<br><b>%{meta} : </b>%{y}<br><extra></extra>")

        return fig
    
    
    def plotCrimesByMode(self, mode, longDf, colors):
        #longDf = self.makeLongDf()
        #colors=self.getModeColors()
        fig = go.Figure()
        valueDf = longDf.loc[longDf["unit"]=="Vol"]
        filtered = valueDf.loc[valueDf["mode"]==mode].dropna()
        fig.add_trace(go.Bar(y=filtered["value"],
                            x=np.array(filtered["date"]),
                            marker_color=colors[mode],
                                #mode="markers+lines",
                                name=mode.replace("_", " ").title(),
                                 meta=mode.replace("_", " ").title(),
                            customdata=filtered[["monthYear"]],
                            #hovertemplate="<b>Month :</b> %{x}<br><b>Reported Crimes : </b>%{y}<br><extra></extra>"
                                hovertemplate="<b>Month :</b> %{customdata[0]}<br>"+
                                     "<b>Tranport Mode :</b> %{meta}<br>" + 
                                     "<b>Reported Crimes : </b> %{y:,.0f}<br>" +
                                     "<extra></extra>")
                                )
        
        fig.update_yaxes(title="Reported Crimes")
        fig.update_xaxes(title="Month")
        fig.update_layout(title=f"<b>Monthly Reported Crimes</b><br><sup>Transport Mode:{mode.replace('_', ' ').title()}")
        
        
        return fig
    
    def barPlotCrimes(self):
        longDf = self.makeLongDf()
        modes = self.getAllTranportModes()
        colors = self.getModeColors()
    
        fig = go.Figure()
        valueDf = longDf.loc[longDf["unit"]=="Vol"]
        for mode in modes:
            if mode != "all_transport_modes":
                fig.add_trace(self.plotCrimesByMode(mode, longDf, colors).data[0])

        fig.update_layout(title="<b>London Crime Statistics</b><br><sup>By Transport Mode</sup>",
                          barmode="stack", #barnorm="percent", 
                          legend={"orientation" : "h",
                                 #"yanchor" : "top",
                                 #"xanchor" : "left",
                                  #"itemwidth" : 70,
                                 "x" : 0.25,
                                 #"y" : -0.5,
                                 "bordercolor" : "antiquewhite",
                                 "borderwidth" : 2})


        return fig
    
    
    def plotYearlyJourneysAndCrimes(self):
        df = self.getTripsByYear()
        
        fig = make_subplots(rows=2, cols=1, shared_xaxes=True, specs=[[{"secondary_y":True}], [{}]])

        cols = {"Vol" : "Reported Crimes", 
               "passengerJourneys" : "Passenger Journerys",
               "Rate" : "Crimes Per Million Passenger Journeys"}

        colors = {x:y for x,y in zip(cols.keys(), px.colors.qualitative.Dark24)}

        col="Vol"
        fig.add_trace(go.Scatter(x=df["year"],
                                y=df[col],
                                marker_color=colors[col],
                                name=cols[col],
                                meta=cols[col]),
                     row=1, col=1)
        col="Rate"
        fig.add_trace(go.Scatter(x=df["year"],
                                y=df[col],
                                marker_color=colors[col],
                                name=cols[col],
                                meta=cols[col]),
                     row=1, col=1, secondary_y=True)
        col="passengerJourneys"
        fig.add_trace(go.Scatter(x=df["year"],
                                y=df[col],
                                marker_color=colors[col],
                                name=cols[col],
                                meta=cols[col]),
                     row=2, col=1)
        fig.update_yaxes(tickmode="sync")
        fig.update_yaxes(title="Reported Crimes", row=1, col=1)
        fig.update_yaxes(title="Crimes Per Million Journeys", row=1, col=1, secondary_y=True)
        fig.update_yaxes(title="Passenger Journeys", row=2, col=1)
        fig.update_xaxes(title="Year", row=2, col=1)
        fig.update_layout(title="<b>Crime Stats By Year</b>",
                         legend={"orientation" : "h",
                                "x":0.25})

        fig.update_traces(hovertemplate="<b>Year : </b> %{x}<br><b>%{meta} : </b>%{y}<br><extra></extra>")
        
        return fig

        

