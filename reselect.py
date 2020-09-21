#!/usr/bin/env python
# coding: utf-8

# In[9]:


from stocktools import StockTools
from datetime import datetime, timedelta


# In[10]:


today = datetime.now().strftime('%Y-%m-%d')
st = StockTools(today)


# In[11]:


start_date = datetime(2020, 1, 1)
end_date = datetime(2020, 1, 2)
delta = timedelta(days=1)
while start_date <= end_date:
    print (start_date.strftime("%Y-%m-%d"))
    
    st.strdate = (start_date - timedelta(days=31)).strftime("%Y-%m-%d")
    st.enddate = start_date.strftime("%Y-%m-%d")
    st.select(force=True)

    start_date += delta


# In[ ]:




