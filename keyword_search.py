#import requests
#from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
import re
from wordcloud import WordCloud
import matplotlib.pyplot as plt


# tags
tag_ref = pd.read_excel('C:\\Users\\ghoffman\\OneDrive - RMI\\01. Projects\\Consultation\\zeroGrid_textAnalysis\\tags.xlsx')

# Read the .xlsx file and extract the URLs
df = pd.read_excel('C:\\Users\\ghoffman\\OneDrive - RMI\\01. Projects\\Consultation\\zeroGrid_textAnalysis\\corporate_commitments_v2.xlsx', sheet_name='Articles')
urls = df['URL'].tolist()

news = df

news = news[news['Snippet'].notna()]

if len(news) < len(df):
    print('True')
else:
    print('False')


tag_ref['phrase'] = tag_ref.phrase.str.lower()


# create a description field for tag matching in lower case
news['desc_match'] = news['Snippet'].str.lower()


# Define string matching function
def get_matching_values(row, keywords):
    matching_values = {keywords_to_tag[keyword] for keyword in keywords if row.lower().find(keyword) != -1}
    return ','.join(matching_values) if matching_values else ''

# Loop through descriptions, stringing together all matching tags
for i in tag_ref['tag_cat']:
    keywords_tag = tag_ref[tag_ref['tag_cat'] == i]
    keywords_tag = keywords_tag[['tag', 'phrase']]
    keywords_tag.rename(columns={"phrase":"keyword"}, inplace=True)
    keywords_to_tag = keywords_tag.set_index('keyword')['tag'].to_dict()
    news[i] = news['desc_match'].apply(get_matching_values, keywords= keywords_to_tag.keys())

# Create concatenated tag variable
#news['tag'] = news[['corporate_partners', 'interventions', 'geography', 'operator_region','scale']].fillna('').agg(','.join, axis=1)

news['tag'] = news[['interventions', 'geography', 'operator_region','scale']].fillna('').agg(','.join, axis=1)


# Create id for unique article
news['uid'] = np.arange(0,len(news),1)

# Transform tags to long format 
score_sub = news[['uid', 'interventions', 'geography', 'operator_region','scale']]

# drop nulls
score = score_sub.melt(id_vars = ['uid'], ignore_index=False).reset_index().fillna('')
score = score.dropna()
score = score[score['value'] != '']


# Create count of tag categories
#tag_score = score.groupby('uid')['value'].count()

news2 = news[['uid', 'Article', 'Snippet', 'URL', 'corporate_partners','tag']]


# Join score back to news df
news_full = pd.merge(news2, score, on='uid', how='outer')


# Remove duplicate and trailing commas from null tags
pattern = re.compile(r',{2,}')
news_full['tag'].replace(pattern, ',', regex = True, inplace = True)

pattern = re.compile(r'(^[,\s]+)|([,\s]+$)')
news_full['tag'].replace(pattern, '', regex = True, inplace = True)

news_full = news_full[['uid', 'Article', 'Snippet', 'URL', 'corporate_partners','tag', 'variable', 'value']]

# Separate the value and partner columns by comma and create a new row for each value
news_full['value'] = news_full['value'].str.split(',')
news_full = news_full.explode('value').reset_index(drop=True)

news_full['corporate_partners'] = news_full['corporate_partners'].str.split(',')
news_full = news_full.explode('corporate_partners').reset_index(drop=True)

news_full.to_excel('testing2.xlsx')



news_grouped = news_full[['corporate_partners', 'variable', 'value']]

#news_grouped = news_grouped.groupby('corporate_partners', 'variable')

print(news_grouped.head())

grouped_tags = news_grouped

grouped_tags = grouped_tags[grouped_tags['corporate_partners'] != '']
print(grouped_tags.head())

# Separate the value column by comma and create a new row for each value
# grouped_tags['value'] = grouped_tags['value'].str.split(',')
# grouped_tags = grouped_tags.explode('value').reset_index(drop=True)

# grouped_tags['corporate_partners'] = grouped_tags['corporate_partners'].str.split(',')
# grouped_tags = grouped_tags.explode('corporate_partners').reset_index(drop=True)


# Create a word cloud for each unique "corporate_partners" value
for corporate_partner in grouped_tags['corporate_partners'].unique():
    # Filter the dataframe for the specific corporate_partner
    tags = grouped_tags[grouped_tags['corporate_partners'] == corporate_partner]['value']
    
    # Count the unique values
    tag_counts = tags.value_counts()
    
    # Generate the word cloud based on the count of unique values
    wordcloud = WordCloud().generate_from_frequencies(tag_counts)
    
    # Plot the word cloud
    plt.figure()
    plt.imshow(wordcloud, interpolation="bilinear")
    plt.title(f"Word Cloud for {corporate_partner}")
    plt.axis("off")
    plt.savefig(f"{corporate_partner}.jpg")
















# #######
# ## Tested grabbing full text from html, but too many issues with credentials/bot detection
    
    # def extract_html_text(url):
    # response = requests.get(url)
    # html_text = response.text
    # return html_text


# urls2 = urls[0:5]
# print(urls2)
# html_texts = []
# page_titles = []

# for url in urls:
#     html_text = extract_html_text(url)
#     html_texts.append(html_text)
    
#     soup = BeautifulSoup(html_text, 'html.parser')
#     title = soup.title.string if soup.title else None
#     page_titles.append(title)
#     print(title)


# data = {'Title': page_titles, 'Text': html_texts}
# df = pd.DataFrame(data)

#     # Print the dataframe
# print(df)







