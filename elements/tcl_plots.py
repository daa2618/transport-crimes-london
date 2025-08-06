
from pathlib import Path
import sys
utils_dir = Path(__file__).resolve().parent.parent/"utils"
if not str(utils_dir) in sys.path:
    sys.path.insert(0, str(utils_dir))

from plotly_imports import *

data_dir = utils_dir.parent/"data"
if not str(data_dir) in sys.path:
    sys.path.insert(0, str(data_dir))
from tcl import TransportCrimeLondon
import re, sys, os, datetime, numpy as np



class TransportCrimePlotData:
    def __init__(self):
        self._df = None

    @property
    def df(self):
        if self._df is None:
            self._df = TransportCrimeLondon().get_transport_crimes_data()
        return self._df

    def make_long_df(self):
        long_df=pd.melt(self.df, id_vars=["month_year", "unit", "fy", "startYear", "endYear", "date", "year", "month"]).rename(columns={"variable" : "mode"})
        
        return long_df
    
    def get_all_transport_modes(self):
        return self.make_long_df()["mode"].unique()
    
    def get_mode_colors(self):
        modes = self.get_all_transport_modes()
        colors = {x:y for x,y in zip(modes, px.colors.qualitative.Dark24)}
        return colors
    
    def get_available_modes(self):
        req_modes = self.df.iloc[-1][self.df.iloc[-1].notna()].index
        modes = self.make_long_df()["mode"].unique()
        return list(set(modes).intersection(req_modes))
    
    def get_trips_by_year(self):
        long_df = self.make_long_df()
        for month_year in long_df["month_year"].unique():
            long_df.loc[(long_df["month_year"]==month_year)&
                  (long_df["unit"]=="Vol")&
                  (long_df["mode"]=="all_transport_modes"), "value"] = long_df.loc[(long_df["month_year"]==month_year)&
                      (long_df["unit"]=="Vol")&
                      (long_df["mode"]!="all_transport_modes"), "value"].sum()

            long_df.loc[(long_df["month_year"]==month_year)&
                  (long_df["unit"]=="passenger_journeys")&
                  (long_df["mode"]=="all_transport_modes"), "value"] = long_df.loc[(long_df["month_year"]==month_year)&
                      (long_df["unit"]=="passenger_journeys")&
                      (long_df["mode"]!="all_transport_modes"), "value"].sum()
            
        df=long_df.loc[long_df["unit"].isin(["Vol", "passenger_journeys"])].groupby(["year", "unit"])["value"].sum().reset_index().rename(columns={"value":"observation"})

        df=pd.pivot(df, columns="unit", index="year", values="observation").reset_index()

        df["Rate"]=(df["Vol"] / df["passenger_journeys"]) * 1000000
        
        
        return df
class TranportCrimePlots(TransportCrimePlotData):
    def __init__(self):
        super().__init__()
        
    def make_hover_template_for_time(self, time):
        if time == "month":
            return "<b>Month :</b> %{customdata[0]}<br>"
        elif time == "year":
            return "<b>Year :</b> %{customdata[0]}<br>"
        
    def update_month_axes(self, fig, time):
        
        if time == "month":
            fig = fig.update_xaxes(tickmode="array",
                            categoryarray=["Jan", "Feb", "Mar", "Apr", "May", "Jun",
                                          "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"])
            return fig
        else:
            return fig
        
        
        
    def plot_monthly_average_crimes(self, time):
        long_df = self.make_long_df()
        req_modes = self.get_available_modes()
        
        grouped_df = long_df.loc[(long_df["unit"]=="Vol") & 
                      (long_df["mode"].isin(req_modes))].groupby([time, "mode"])["value"].mean().dropna().reset_index()

        fig = go.Figure()
        colors = self.get_mode_colors()
        
        for mode in grouped_df["mode"].unique():
            if mode != "all_transport_modes":
                filtered = grouped_df.loc[grouped_df["mode"]==mode]
                fig.add_trace(go.Bar(x=filtered[time],
                                    y=filtered["value"],
                                    name=mode,
                                    marker_color=colors[mode],
                                    customdata=filtered[[time, "mode"]],
                                         hovertemplate=self.make_hover_template_for_time(time)+
                                         "<b>Tranport Mode :</b> %{customdata[1]}<br>" + 
                                         "<b>Reported Crimes : </b> %{y:,.0f}<br>" +
                                         "<extra></extra>"))

        fig.update_layout(barmode="stack", 
                          #barnorm="percent",
                          title=f"<b>Monthly Average Reported Crimes</b><br><sup>By {time.title()} and Transport Mode</sup>",
                          legend=dict(title="Transport Modes",
                                                      orientation="h"))
        fig.update_xaxes(title=time, tickvals=(grouped_df[time].unique()))
        fig.update_yaxes(title="Reported Crimes")
        fig = self.update_month_axes(fig, time)
        return fig
    
    
    def plot_crimes_vs_rate(self, mode):
        long_df = self.make_long_df()
        
        fig = make_subplots(specs=[[{"secondary_y" : True}]])

        colors = {x:y for x,y in zip(long_df["unit"].unique(), ["steelblue", "antiquewhite"])}

        filtered = long_df.loc[long_df["mode"]==mode].dropna()
        units=long_df["unit"].unique()
        value_df = filtered.loc[filtered["unit"]==units[0]]

        fig.add_trace(go.Scatter(y=value_df["value"],
                        x=np.array(value_df["date"]),
                        marker_color=colors[units[0]],

                            mode="markers+lines",
                            name="Reported Crimes",
                                 meta="Reported Crimes",
                                ))
        value_df = filtered.loc[filtered["unit"]==units[1]]
        fig.add_trace(go.Scatter(y=value_df["value"],
                        x=np.array(value_df["date"]),
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
    
    
    def plot_crimes_by_mode(self, mode, long_df, colors):
        #long_df = self.make_long_df()
        #colors=self.get_mode_colors()
        fig = go.Figure()
        value_df = long_df.loc[long_df["unit"]=="Vol"]
        filtered = value_df.loc[value_df["mode"]==mode].dropna()
        fig.add_trace(go.Bar(y=filtered["value"],
                            x=np.array(filtered["date"]),
                            marker_color=colors[mode],
                                #mode="markers+lines",
                                name=mode.replace("_", " ").title(),
                                 meta=mode.replace("_", " ").title(),
                            customdata=filtered[["month_year"]],
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
    
    def bar_plot_crimes(self):
        long_df = self.make_long_df()
        modes = self.get_all_transport_modes()
        colors = self.get_mode_colors()
    
        fig = go.Figure()
        value_df = long_df.loc[long_df["unit"]=="Vol"]
        for mode in modes:
            if mode != "all_transport_modes":
                fig.add_trace(self.plot_crimes_by_mode(mode, long_df, colors).data[0])

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
    
    
    def plot_yearly_journeys_and_crimes(self):
        df = self.get_trips_by_year()
        
        fig = make_subplots(rows=2, cols=1, shared_xaxes=True, specs=[[{"secondary_y":True}], [{}]])

        cols = {"Vol" : "Reported Crimes", 
               "passenger_journeys" : "Passenger Journerys",
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
        col="passenger_journeys"
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

        

