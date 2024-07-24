from response import Response
import json
from nltk.stem.snowball import SnowballStemmer
stemmer = SnowballStemmer("english")
import re
from itertools import chain
from urllib.parse import urlsplit, urlunsplit
from dataset import Dataset
import datetime

class SearchTerms:
    def getListOfWords(string):
        return [stemmer.stem(x) for x in re.sub("[-_]", " ", string.rstrip(" ").lstrip(" ").lower()).split(" ")]

class LondonDataStore(Response, SearchTerms):
    def __init__(self):
        self._jsonUrl = "https://data.london.gov.uk/api/datasets/export.json"
        
    def getDataFromUrl(self):
        response = Response(self._jsonUrl).assertResponse()
        #print()
        return json.loads(response.content)
    
    
    def getAllSlugs(self):
        slugs = list(set([x.get("slug") for x in self.getDataFromUrl()]))
        slugs.sort()
        return slugs
    
    
    def filterSlugsForString(self, string):
        searchTerms = SearchTerms.getListOfWords(string)
        filtered = [x for x in self.getAllSlugs() if any(word in y for y in SearchTerms.getListOfWords(x) for word in searchTerms)]
        if not filtered:
            raise ValueError("The string does not match any existing slugs")
        else:
            return filtered
        
    def getAllDTypes(self):

        dtypes = [[value.get("format") for key, value in x.get("resources").items()] for x in self.getDataFromUrl()]
        dtypes = list(set(list(chain.from_iterable(dtypes))))
        return dtypes
    
    def filterSlugForDType(self, reqFormat):
        if not reqFormat in self.getAllDTypes():
            raise ValueError(f"Available Data types: {', '.join(self.getAllDTypes())}")
        
        filtered = [y.get("slug") for y in self.getDataFromUrl() if reqFormat in [x.get("format") for x in [value for key, value in y.get("resources").items()]]]
        if not filtered:
            raise ValueError("No slugs was found for the required data type")
        else:
            return filtered
        
    def getDownloadUrlForSlug(self, slug, getDescription=False):
        urls = []
        for y in self.getDataFromUrl():
            if y.get("slug") == slug:
                updatedAt = datetime.datetime.strftime(datetime.datetime.fromisoformat(y.get('updatedAt')), "%d %B %Y")
                
                print(f"The Data was last updated on '{updatedAt}'")
                if getDescription:
                    print(y.get("description"))
                for key, value in y.get("resources").items():
                    #print(f"{key}/{value.get('searchFilename').replace(' ', '-')}")
                    urls.append(f"{Response(self._jsonUrl).getBaseUrl()}/download/{y.get('slug')}/{key}/{urlsplit(value.get('url')).path.split('/')[-1]}")
        print(f"{len(urls)} urls have been found. Choose relevant url.")
        return urls
    
    
    def filterSlugsForKeyword(self, keyword):
        #slugs = []
        searchTerms = SearchTerms.getListOfWords(keyword)
        slugs = [x.get("slug") for x in self.getDataFromUrl() if any(word in y for y in [stemmer.stem(z) for z in x.get("tags")] for word in searchTerms)]
        return slugs