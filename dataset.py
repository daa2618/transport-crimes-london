#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import csv 
import pandas as pd
import json
import io
import os
from response import Response

class Dataset(Response):
    def __init__(self, docUrl):
        self.docUrl = docUrl
        
    def loadData(self):
        extension = os.path.splitext(self.docUrl)[1]
        response = Response(self.docUrl).assertResponse()
        if extension == "":
            extension = response.headers.get("Content-Type")

        if extension == ".ods":
            xls = pd.ExcelFile(io.BytesIO(response.content))
            print(f"Sheets in this file: {xls.sheet_names}")
            out = {}
            for sheet in xls.sheet_names:
                out[sheet] = pd.read_excel(xls, sheet, engine="odf")

            return out

        elif extension == ".csv" or "csv" in extension:
            with io.StringIO(response.text) as f:
                dat = csv.DictReader(f)
                colNames = dat.fieldnames
                print(f"columns: {colNames}")
                print("Converting the response into json format")
                content = [{col.replace(" ", "_").lower() : row[col] for col in colNames} for row in dat]

            return content

        elif extension == ".xlsx" or extension == ".xls":
            xls = pd.ExcelFile(io.BytesIO(response.content))
            out = {}
            for sheet in xls.sheet_names:
                out[sheet] = pd.read_excel(xls, sheet)

            return out

        elif extension == ".json" or "json" in extension:
            responseDict = response.json()
            return responseDict

        else:
            return None
        
class WriteFile:
    def __init__(self, basePath, dataToWrite, fileName, extension):
        self.basePath = basePath
        self.dataToWrite = dataToWrite
        self.fileName = fileName
        self.extension = extension
        
       
    def writeFileToDisk(self):
        #basePath = "data"
        if not os.path.exists(self.basePath):
            os.mkdir(self.basePath)
        if not "." in self.extension:
            extension = f".{self.extension}"
        filePath = os.path.join(self.basePath, f"{self.fileName}{extension}")
        
        print(f"\nWriting the file at {(os.path.abspath(filePath))}....")
        for file in os.listdir(self.basePath):
            if file == f"{self.fileName}{extension}":
                os.remove(filePath)
        
        if "json" in self.extension:
            if isinstance(self.dataToWrite, list): 
                with open(filePath, "x") as f:
                    f.write(json.dumps(self.dataToWrite))
                #print(f"written at {filePath}")
            else:
                raise TypeError(f"The file to write is of type {type(self.dataToWrite)}.\nTherefore, cannot be saved as a json file")
                        
        if "csv" in self.extension:           
            if "dataframe" in str(type(self.dataToWrite)).lower():
                self.dataToWrite.to_csv(filePath, index=False)
            else:
                raise TypeError(f"The file to write is of type {type(self.dataToWrite)}.\nTherefore, cannot be saved as a csv file")
                        
        print(f"The file has been written")
        return None
    
