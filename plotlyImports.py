#!/usr/bin/env python
# coding: utf-8

# In[1]:


import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio
from plotly.subplots import make_subplots
import pandas as pd


pio.templates["myWatermark"] = go.layout.Template(layout_annotations=[
    dict(name="watermark",
        text="Dev Anbarasu",
        #textangle=-30,
        opacity=0.1,
        font=dict(color="white", size=25),
        xref="paper",
        yref="paper",
        x=0.5,
        y=0.5,
        showarrow=False)
])
pio.templates.default = "plotly_dark+myWatermark"


class SubplotSpecs:
    def __init__(self, array):
        self.array=pd.Series(array)
        
    def getNUnique(self):
        return self.array.nunique()
    
    def getNRowsColumns(self,n=False):
        if not n:
            n = self.getNUnique()
        nCols = min(3, n)
        #nRows = (nRaces - nCols) 
        nRows=round(n/nCols)
        if nRows * nCols < n:
            nRows = nRows + 1
        return nRows,nCols

    def getSubplotMatrices(self):
        n = self.getNUnique()
        rows, cols = [], []
        for a in range(1,n+1,1):
            x=a
            nRows, nCols = self.getNRowsColumns(x)
            rows.append(nRows)
            cols.append(nCols)


        rows={x:y for x,y in (zip(range(1,n+1),rows))}
        cols={x:y for x,y in (zip(range(1,n+1),[1,2,3]*(n)))}
        return rows, cols
    
    
    def getSpecs(self, d={"type" : "pie"}):
        nRows, nCols = self.getNRowsColumns()
        
        n = nRows * nCols
        specs=list(d.copy() for x in range(n))

        specs=[specs[x:x+3] for x in range(0, n, 3)]
        return specs



