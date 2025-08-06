import sys
from pathlib import Path
from .logging_helper import BasicLogger

_bl = BasicLogger(verbose=False, log_directory=None, logger_name="DATA_LOADER")

import os, re, json, pandas as pd, io
from .response import Response
import urllib.parse as urlparser
#from opExcel import MoreOpenPyExcel
#from extractZipFile import ExtractZipFile
from typing import Union, Optional

class FilePathError(Exception):
    pass

class UnsupportedExtension(Exception):
    pass


class Dataset:
    """
    provide doc_url for an url or the file_path to a file
    """
    def __init__(self, **kwargs):
        """Initializes the object with optional parameters.

        Args:
            **kwargs: A dictionary of keyword arguments.  The following keys are supported:
                - doc_url (str): The URL of the documentation.
                - file_path (str): The path to a file.

        """
        self.doc_url = kwargs.get("doc_url")
        self.file_path = kwargs.get("file_path")
        self._supported_extensions = ["csv", "ods", "xlsx", "xls", "json", "pdf",
                                     "text/csv", "geojson"]
    
    def _response(self, **kwargs):
        if self.doc_url:
            return Response(self.doc_url).assert_response()
        else:
            return Response(**kwargs).assert_response()
    
    def _guess_extension(self):
    
        if self.doc_url:
            response = self._response()
            return response.headers.get("Content-Type")
        
    @property
    def _extension(self):
        extension = os.path.splitext(self.doc_url or self.file_path)[1]
        if extension:
            return extension
        else:

            return None

    @_extension.setter
    def _extension(self, value):
        self._extension = value

    @property
    def _github_doc_url(self):
        if self.doc_url:
            if "github" in self.doc_url:
                return re.sub("blob", "raw", self.doc_url)
    
    @property
    def _assert_file_path(self):
        if self.file_path:
            if not os.path.exists(self.file_path):
                raise FileNotFoundError("File path does not exist")

    def _check_extension(self, extension:str):
        extension = extension.lower()
        if not any(extension.endswith(x) for x in self._supported_extensions) and \
            not any(x in re.sub("\\.", "", extension) for x in self._supported_extensions):
            raise UnsupportedExtension(f"Extension: {extension} is not supported")
        
    
    def _try_loading_from_github(self):
        if self.doc_url and "github" in self.doc_url:
            path = urlparser.urlsplit(self.doc_url).path
            doc_url = re.sub("blob", "refs/heads", urlparser.urljoin("https://raw.githubusercontent.com", path))
            #_bl.info(doc_url)
            return self._response(url=doc_url)
        
    @property    
    def _load_csv(self):
        import csv

        if self.doc_url:
            if "github" in self.doc_url:
            #    url = self._github_doc_url
                response = self._try_loading_from_github()
            else:
                url= self.doc_url
                response = self._response(url=url)

            if not self._extension:
                self._extension = response.headers.get("Content-Type")

            with io.StringIO(response.text) as f:
                dat = csv.DictReader(f)
                col_names = dat.fieldnames
                if col_names:
                    _bl.info(f"columns: {col_names}")
                    _bl.info("Converting the response into json format")
                content = [{col.replace(" ", "_").lower() : row[col] for col in col_names} for row in dat]
                non_empty_content = [x for x in content if x]
            if not non_empty_content:
                if "github" in self.doc_url:
                    path = urlparser.urlsplit(self.doc_url).path
                    doc_url = re.sub("blob", "refs/heads", urlparser.urljoin("https://raw.githubusercontent.com", path))
                else:
                    doc_url=self.doc_url
                df=pd.read_csv(doc_url)
                df.columns = [re.sub(" ", "_", str(x).lower()) for x in df.columns]
                content = json.loads(df.to_json(orient="records"))

        
        elif self.file_path:
            self._assert_file_path

            with open(self.file_path, "r") as f:
                dat = csv.DictReader(f)
                col_names = dat.fieldnames
                _bl.info(f"columns: {col_names}")
                _bl.info("Converting the response into json format")
                content = [{col.replace(" ", "_").lower() : row[col] for col in col_names} for row in dat]
        
        
        return content
    
    @property
    def _load_ods(self):
        if self.doc_url:
            response = self._response(url=self.doc_url)
            content = io.BytesIO(response.content)
        elif self.file_path:
            content = self.file_path
        
        xls = pd.ExcelFile(content)
        _bl.info(f"Sheets in this file: {xls.sheet_names}")
        out = {}
        for sheet in xls.sheet_names:
            out[sheet] = pd.read_excel(xls, sheet, engine="odf")
        
        return out
    @property
    def _load_excel(self):
        if self.doc_url:
            content = io.BytesIO(self._response().content)
        elif self.file_path:
            content = self.file_path
        
        xls = pd.ExcelFile(content)
        out = {}
        _bl.info(f"Sheets in this file: {xls.sheet_names}")
        for sheet in xls.sheet_names:
            out[sheet] = pd.read_excel(xls, sheet)
        return out
    @property
    def _load_json(self):
        if self.doc_url:
            try:
                responseDict = json.loads(self._response().content)
            except:
                try:
                    path = urlparser.urlsplit(self.doc_url).path
                    if "github" in self.doc_url:
                        doc_url = re.sub("blob", "refs/heads", urlparser.urljoin("https://raw.githubusercontent.com", path))
                        _bl.info(f"{doc_url=}")
                        responseDict = json.loads(self._response(url=doc_url).content)
                except Exception as e:
                    _bl.error(f"Failed to load data : \n\t{e}")
                    pass
        elif self.file_path:
            self._assert_file_path
            with open(self.file_path, "r") as f:
                responseDict = json.load(f)
        
        return responseDict
    
    @property
    def _load_pdf(self):
        import pdfplumber
        if self.doc_url:
            try:
                content = io.BytesIO(self._response().content)
                return pdfplumber.open(content)
            except Exception as e:
                _bl.error(f"Error obtaining pdf from url\n\t{e}")
        
        elif self.file_path:
            self._assert_file_path
            try:
                return pdfplumber.open(self.file_path)
            except Exception as e:
                _bl.error(f"Failed to load pdf from filepath\n\t{e}")
    
    @property
    def _load_geojson(self):
        import geopandas as gpd
        if self.doc_url:
            try:
                return gpd.read_file(self.doc_url)
            except Exception as e:
                _bl.error("Failed to load geojson from url\n\t{e}")
        elif self.file_path:
            try:
                return gpd.read_file(self.file_path)
            except Exception as e:
                _bl.error("Failed to load geojson from file\n\t{e}")

    @property
    def _load_for_extension(self):
        extension = self._extension
        if extension:
            extension = extension.lower()
            self._check_extension(extension)
            if extension.endswith("csv") or "csv" in extension:
                try:
                    return self._load_csv
                except Exception as e:
                    _bl.error("Failed to load from csv",e)
            elif extension.endswith("ods") or "ods" in extension:
                try:
                    return self._load_ods
                except Exception as e:
                    _bl.error("Failed to load from ODS",e)
            elif extension.endswith("xlsx") or extension.endswith("xls") or \
                "xlsx" in extension or "xls" in extension:
                try:
                    return self._load_excel
                except Exception as e:
                    _bl.error("Failed to load from excel",e)
            elif extension.endswith("json") or "json" in extension:
                try:
                    return self._load_json
                except Exception as e:
                    _bl.error("Failed to load from json",e)
            elif extension.endswith("pdf") or "pdf" in extension:
                try:
                    return self._load_pdf
                except Exception as e:
                    _bl.error("Failed to load from pdf",e)
            elif extension.endswith("geojson") or "geojson" in extension or \
                "geo+json" in extension:
                try:
                    return self._load_geojson
                except Exception as e:
                    _bl.error("Failed to load from geojson",e)
    

    def load_data(self):
        """Loads data from a specified URL or file path.

        This method attempts to load data from either a URL (self.doc_url) or a local file path (self.file_path).
        It supports various file formats including CSV, XLSX, XLS, ODS, PDF, and JSON based on the file extension or the Content-Type header 
        if fetched from a URL.  The data is then parsed and returned accordingly.  Handles GitHub URLs by urlsplit and urljoin methods.

        Returns:
            dict or list or None:  Returns a dictionary containing dataframes for each sheet in Excel files (.xls, .xlsx, .ods), 
                                a list of dictionaries for CSV files, a dictionary for JSON files, or None if the file type is unsupported or an error occurs.
                                For ODS files, the keys are the sheet names. For CSV files, the keys are the lowercase versions of column names with spaces replaced by underscores.
                                PDF files are returned as pdfplumber.PDF

        Raises:
            Various exceptions:  Exceptions may be raised during file I/O, data parsing, or network requests 
                           depending on the file type and source.  Error messages are printed to the console.
        """
        try:
            extension = self._extension
            if not extension and self.doc_url:
                guessed_extension = self._guess_extension()
                self._supported_extensions.append(guessed_extension)
                self._extension = guessed_extension
                return self._load_for_extension
            else:
                return self._load_for_extension
            
        except Exception as e:
            _bl.error("Failed to load data\nReason:", e)
            return None
        

class PostProcess:

    
    @staticmethod
    def set_columns_from_index_and_drop_rows(df:pd.DataFrame, col_index:Union[str, int])->Optional[pd.DataFrame]:
        """Sets DataFrame columns from a specified row and drops rows above that row.

        This function takes a Pandas DataFrame and an integer index as input.  It uses the row at the specified index as the new column names for the DataFrame.  All rows above the specified index are then dropped. Finally, it cleans the column names by removing leading digits and whitespace, converting to lowercase, and replacing spaces with underscores.

        Args:
            df (pd.DataFrame): The input Pandas DataFrame.
            col_index (int): The index of the row to use as new column names.

        Returns:
            pd.DataFrame: A new DataFrame with updated column names and rows above `col_index` dropped.  Returns None if `col_index` is out of bounds.

        Raises:
            IndexError: If `col_index` is out of bounds for the DataFrame.

        """
        col_index = int(col_index)

        df_copy = df.copy()
        df_copy.columns = df_copy.iloc[col_index]
        df_copy = df_copy.iloc[col_index + 1:,].reset_index(drop=True)
        df_copy.columns = [re.sub(r"\d+\.?\s+?", "", col.lower()).replace(" ", "_") for col in df_copy.columns]
        return df_copy


    @staticmethod
    def convert_data_types_of_cols(df:pd.DataFrame, d_type:str)->Optional[pd.DataFrame]:

        d_type_lower = d_type.lower()
        if  d_type_lower not in ["float", "int", "category"]:
            raise TypeError(f"Invalid data type '{d_type}'. Choose from 'float, int'")
        

        df_copy = df.copy()
        
        for col in df_copy.columns:
            _bl.info(f"Processing column: '{col}'")
            try:
                df_copy[col] = df_copy[col].astype(d_type_lower)
                _bl.info(f"Column: '{col}' converted to data type '{d_type}'.")
            except:
                _bl.error(f"Processing failed for column: '{col}'. Retaining original data type")
                df_copy[col] = df_copy[col]
        
        return df_copy
    
    

    

    



            

    

        

        

                

            


        