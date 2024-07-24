#!/usr/bin/env python
# coding: utf-8

# In[109]:


#!/usr/bin/env python
# coding: utf-8

# In[48]:


import requests
from urllib.parse import urlsplit, urlunsplit


class Response:
    def __init__(self, url):
        self.url = url
        
    def assertResponse(self):
        #print(f"Getting the response from {self.url}")
        response = requests.get(self.url)
        assert response.status_code == 200, response.raise_for_status()
        #print("The response was obtained")
        return response
    
    def getBaseUrl(self):
        splitUrl = urlsplit(self.url)
        return "://".join([splitUrl.scheme, splitUrl.netloc])



# In[ ]:




