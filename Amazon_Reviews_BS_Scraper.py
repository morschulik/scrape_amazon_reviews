#!/usr/bin/env python
# coding: utf-8

# In[3]:


# import libraries 

from bs4 import BeautifulSoup
import requests
import pandas as pd


# In[62]:


# Connect to the product Website and get the name and price of this
URL = 'https://www.amazon.com/Galanz-GLR16FS2K16-Refrigerator-Adjustable-Electrical/dp/B08QVPBFCS/ref=cm_cr_arp_d_product_top?ie=UTF8'

headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36", "Accept-Encoding":"gzip, deflate", "Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8", "DNT":"1","Connection":"close", "Upgrade-Insecure-Requests":"1"}

page = requests.get(URL, headers=headers)

soup1 = BeautifulSoup(page.content, "html.parser")

soup = BeautifulSoup(soup1.prettify(), "html.parser")

title = soup.find(id='productTitle').get_text()

print(title)

##No displayed Price for this product! if so>price = soup2.find(id='priceblock_ourprice').get_text()

#print(title)
##print(price)


# In[16]:


# Connect to the reviews Website and pull in data (eg.Title ?)

URL = 'https://www.amazon.com/Galanz-GLR16FS2K16-Refrigerator-Adjustable-Electrical/product-reviews/B08QVPBFCS/ref=cm_cr_dp_d_show_all_btm?ie=UTF8&reviewerType=all_reviews'

headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36", "Accept-Encoding":"gzip, deflate", "Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8", "DNT":"1","Connection":"close", "Upgrade-Insecure-Requests":"1"}

page = requests.get(URL, headers=headers)

soup1 = BeautifulSoup(page.content, "html.parser")

soup = BeautifulSoup(soup1.prettify(), "html.parser")

#print(soup2)
print (soup.title.text.strip()) ##strip() to remove spaces


# In[64]:


## Get the reviews and loop through each one of them

reviews = soup.find_all('div',{'data-hook':'review'})

# Retrieve reviews titles
for r in reviews:
    print(r.find('a',{'data-hook':'review-title'}).text.strip())


# In[65]:


# Retrieve reviews stars rating
for r in reviews:
    print(r.find('i', {'data-hook': 'review-star-rating'}).text.strip())


# In[26]:


# Retrieve reviews dates 
for r in reviews:
    print(r.find('span', {'data-hook': 'review-date'}).text.strip())


# In[27]:


# Retrieve reviews text or body 
for r in reviews:
    print(r.find('span', {'data-hook': 'review-body'}).text.strip())


# In[33]:


# group all retrieved variables in a dictonary 

for r in reviews:
    review = { 
        'product_name':soup.title.text.replace('Amazon.com: Customer reviews:',' ').strip(),##we removed the start 
        'review_title': r.find('a',{'data-hook':'review-title'}).text.strip(),
        'review_stars': r.find('i', {'data-hook': 'review-star-rating'}).text.strip(),
        'review_date': r.find('span', {'data-hook': 'review-date'}).text.strip(),
        'review_body': r.find('span', {'data-hook': 'review-body'}).text.strip()
    }
    print(review)
        
        
        


# In[47]:


# Done, we get the reviews, but only on the first page, we need to have them for all pages!

# First let's make what did as functions 1:get_soup() 2:get_review(), at the end we want a list of all reviews []

# First create an empty list variable 
reviews_list = []

# Create a function where we get the soup of a specific URL
def get_soup(irl):
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36", "Accept-Encoding":"gzip, deflate", "Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8", "DNT":"1","Connection":"close", "Upgrade-Insecure-Requests":"1"}
    page = requests.get(URL, headers=headers)
    soup1 = BeautifulSoup(page.content, "html.parser")
    soup = BeautifulSoup(soup1.prettify(), "html.parser")
    return soup 


# In[53]:


# Define a function where we get the reviews from a soup
def get_reviews(soup):
    try:
        for r in reviews:
            review = { 
                'product_name':soup.title.text.replace('Amazon.com: Customer reviews:',' ').strip(),##we removed the start 
                'review_title': r.find('a',{'data-hook':'review-title'}).text.strip(),
                'review_stars': r.find('i', {'data-hook': 'review-star-rating'}).text.strip(),
                'review_date': r.find('span', {'data-hook': 'review-date'}).text.strip(),
                'review_body': r.find('span', {'data-hook': 'review-body'}).text.strip()
            }
            reviews_list.append(review)
    except:
        pass

    #for each page
for i in range(1,4):
    soup = get_soup(f'https://www.amazon.com/Galanz-GLR16FS2K16-Refrigerator-Adjustable-Electrical/product-reviews/B08QVPBFCS/ref=cm_cr_getr_d_paging_btm_prev_1?ie=UTF8&reviewerType=all_reviews&pageNumber={i}')
    get_reviews(soup)
    ##print(len(reviews_list))
    if not soup.find('li',{'class':'a-disabled a-last'}):
        pass
    else:
        break
        


# In[54]:


# Create an excel file of the reviews
df = pd.DataFrame(reviews_list)
df.to_excel('fridge_amazon_reviews.xlsx', index=False)
print('Fin.')


# In[ ]:




