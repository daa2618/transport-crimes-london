
import pandas as pd, numpy as np, re, sys, os, datetime
from london_data_store.api import LondonDataStore
from pathlib import Path
import sys
pardir = Path(__file__).resolve().parent.parent
if not str(pardir) in sys.path:
    sys.path.insert(0, str(pardir))
from utils.dataset import Dataset

class TransportCrimeLondon:
    def __init__(self):
        self.slug = "transport-crime-london"
    
    @property    
    def get_download_url(self):
        download_url = LondonDataStore().get_download_url_for_slug(self.slug)
        print(download_url)
        return download_url[0]

    def get_df(self):
        return Dataset(self.get_download_url).load_data()


    def get_clean_df(self):
        df = self.get_df()['Volume and Rates']
        for a in range(df.shape[1], 1, -2):
            df.insert(a, "passenger_journeys", np.nan, allow_duplicates=True)
        df=pd.concat([pd.DataFrame([df.columns], columns = df.columns), df]).reset_index(drop=True)

        df.columns=[str(x) for x in range(len(df.columns))]
        
        df["group_no"]=df.isnull().all(axis=1).cumsum()
        
        df=df.dropna(subset=['1']).reset_index(drop=True)
        
        dfs = []
        for group in df["group_no"].unique():
            dfs.append(df.loc[df["group_no"]==group].reset_index(drop=True))
        
        out={}
        for df in dfs:
            out[df.iloc[0,0].replace(" ", "_").lower()] = df.drop(columns="group_no", axis=0)

        return out

    def further_clean_df(self):
        data = self.get_clean_df()
        out={}
        for key, value in data.items():
            df = value
            for a in range(3, len(df.columns), 3):
                df.iloc[2:,a]=df.iloc[2:,a-2].apply(lambda x: float(str(x).replace(",", ""))*1000000 if not "-" in str(x) else None) / df.iloc[2:,a-1].apply(lambda x: float(str(x).replace(",", "")) if not "-" in str(x) else None)
            try:
                df.iloc[0]=[None if "Unnamed" in x else x for x in df.iloc[0]]
            except:
                pass
        
            df.iloc[0]=df.iloc[0].ffill()
            
            df=df.transpose()
            
            df.columns=df.iloc[0]
            
            df=df.iloc[1:].reset_index(drop=True)
            
            df=df.reset_index(drop=True)
            
            df=df.rename(columns={np.nan:"unit"})
            
            df.columns=["month" if "network" in x.lower() else x.lower().replace(" ", "_") for x in df.columns]
            df=df.assign(fy=re.findall(r"\d+\/\d+", key)[0])
            for col  in df.columns:
                try:
                    df[col] = [float(str(x).replace(",", "")) if not '-' in str(x) else None for x in df[col]]
                except:
                    df[col] = df[col]
            df.loc[df["unit"].isna(), "unit"] = "passenger_journeys"

            df.loc[df["month"]=="passenger_journeys", "month"] = None

            df["month"]=df["month"].ffill()
                    
            out[key] = df

        return out

    def get_transport_crimes_data(self):
        data = self.further_clean_df()
        df=pd.concat([x for x in data.values()]).reset_index(drop=True)

        df=df.assign(start_year=None)
        df=df.assign(end_year=None)
        
        df["start_year"]=df["fy"].apply(lambda x: x.split("/")[0])
        df["end_year"]=df["fy"].apply(lambda x: "20"+x.split("/")[1])
        
        df["month"]=df["month"].apply(lambda x: x[:3])
        
        endMonths = ["Jan", "Feb", "Mar"]
        startMonths = ["Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
        
        df.loc[df["month"].isin(endMonths), "month"] = df.loc[df["month"].isin(endMonths), "month"] + " " + df.loc[df["month"].isin(endMonths), "end_year"]
        
        df.loc[df["month"].isin(startMonths), "month"] = df.loc[df["month"].isin(startMonths), "month"] + " " + df.loc[df["month"].isin(startMonths), "start_year"]
        
        df["date"]=df["month"].apply(lambda x: datetime.datetime.strptime(x, "%b %Y"))
        
        df = df.rename(columns={"month" : "month_year"})
        df["month"]=df["month_year"].apply(lambda x: re.findall("[A-Za-z]+", x)[0])
        df["year"]=df["date"].dt.year
        return df
        




