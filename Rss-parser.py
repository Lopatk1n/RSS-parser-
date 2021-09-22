# -*- coding: utf-8 -*-
import requests
from bs4 import BeautifulSoup as bs
import pandas as pd
import fake_useragent

link = "https://www.kommersant.ru/RSS/news.xml"
links_relations = {
    'link':'guid',\
    'cat':'category',\
    'title':'title',\
    'pub_date':'pubdate',\
    'short_desc':'description',\
    'full_text': None\
    } # values are tags in xml 
df=pd.DataFrame(columns=[key for key in links_relations.keys()])
temp_df = pd.DataFrame()


def create_fake_agent():
    user = fake_useragent.UserAgent().random
    headers = {
        'user-agent': user,
            }
    return headers


# parse RSS-content

response = requests.get(link,headers=create_fake_agent()).text
soup = bs(response,'html.parser')
block = soup.find_all('item')
   
for key in links_relations:
    temp_df[f'{key}'] = [item.find(links_relations[key]).text if \
    links_relations[key] else None for item in block ]


# getting full content from https://www.kommersant.ru/

for i, link in enumerate(temp_df['link']):
    
    response = requests.get(link,headers=create_fake_agent()).text
    soup = bs(response,'html.parser')
    
    
    # getting full text of post
    
    text_block = soup.find('div',class_='article_text_wrapper js-search-mark')
    paragraphs = text_block.find_all('p')
    full_text = '\n'.join(list(map(lambda p: p.text, paragraphs)))
    temp_df.loc[i,['full_text']] = full_text
    
    
    # get the image if there is and save
    
    post_block = soup.find('div',class_='grid_cell grid_cell_big js-middle')
    image_blocks = post_block.find_all('img',class_='js-lazyimage-source')
    image_links = list(map(lambda x: x.get('data-lazyimage-src'),\
                           image_blocks))
    for current_link in image_links:
        if "NEWS" in current_link:
            image = requests.get(current_link).content
            img_slug = f'photo{i}'
            with open(f'images/{img_slug}.jpg','wb') as file:
                file.write(image)


# save text-data

df = pd.concat([df,temp_df],axis=0,ignore_index=True)
df.to_csv("output.csv")
