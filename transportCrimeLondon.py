#!/usr/bin/env python
# coding: utf-8

# In[6]:


import pandas as pd, numpy as np, re, sys, os, datetime
#sys.path.append(os.path.join(git.Repo(".", search_parent_directories=True).working_tree_dir, "londonDataStore"))
from londonDataStore import LondonDataStore
from dataset import Dataset, WriteFile



class TransportCrimeLondon:
    def __init__(self):
        self.slug = "transport-crime-london"
    
    @property    
    def getDownloadUrl(self):
        downloadUrl = LondonDataStore().getDownloadUrlForSlug(self.slug)
        print(downloadUrl)
        return downloadUrl[0]

    def getDf(self):
        return Dataset(self.getDownloadUrl).loadData()


    def getCleanDf(self):
        df = self.getDf()['Volume and Rates']
        for a in range(df.shape[1], 1, -2):
            df.insert(a, "passengerJourneys", np.nan, allow_duplicates=True)
        df=pd.concat([pd.DataFrame([df.columns], columns = df.columns), df]).reset_index(drop=True)

        df.columns=[str(x) for x in range(len(df.columns))]
        
        df["groupNo"]=df.isnull().all(axis=1).cumsum()
        
        df=df.dropna(subset=['1']).reset_index(drop=True)
        
        dfs = []
        for group in df["groupNo"].unique():
            dfs.append(df.loc[df["groupNo"]==group].reset_index(drop=True))
        
        out={}
        for df in dfs:
            out[df.iloc[0,0].replace(" ", "_").lower()] = df.drop(columns="groupNo", axis=0)

        return out

    def futherCleanDf(self):
        data = self.getCleanDf()
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
            df.loc[df["unit"].isna(), "unit"] = "passengerJourneys"

            df.loc[df["month"]=="passengerJourneys", "month"] = None

            df["month"]=df["month"].ffill()
                    
            out[key] = df

        return out

    def getTransportCrimesData(self):
        data = self.futherCleanDf()
        df=pd.concat([x for x in data.values()]).reset_index(drop=True)

        df=df.assign(startYear=None)
        df=df.assign(endYear=None)
        
        df["startYear"]=df["fy"].apply(lambda x: x.split("/")[0])
        df["endYear"]=df["fy"].apply(lambda x: "20"+x.split("/")[1])
        
        df["month"]=df["month"].apply(lambda x: x[:3])
        
        endMonths = ["Jan", "Feb", "Mar"]
        startMonths = ["Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
        
        df.loc[df["month"].isin(endMonths), "month"] = df.loc[df["month"].isin(endMonths), "month"] + " " + df.loc[df["month"].isin(endMonths), "endYear"]
        
        df.loc[df["month"].isin(startMonths), "month"] = df.loc[df["month"].isin(startMonths), "month"] + " " + df.loc[df["month"].isin(startMonths), "startYear"]
        
        df["date"]=df["month"].apply(lambda x: datetime.datetime.strptime(x, "%b %Y"))
        
        df = df.rename(columns={"month" : "monthYear"})
        df["month"]=df["monthYear"].apply(lambda x: re.findall("[A-Za-z]+", x)[0])
        df["year"]=df["date"].dt.year
        return df
        


# In[ ]:




