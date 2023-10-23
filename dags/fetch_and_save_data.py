import requests
from bs4 import BeautifulSoup
import pandas as pd 
import json
import os
from datetime import datetime
from time import sleep

BASE_URL = "https://autot.tori.fi/veneet/myydaan/moottoriveneet?sivu="
HEADERS = {
        "User-Agent":
          "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/118.0",
      }
current_date = datetime.now().strftime("%Y%m%d")
def fetch_page(page_number: str) -> str:
  """
    Send a request to the url with specific page number and headers.
    If the status is successful, then use BeautifulSoup to parse and return content as a json-like string. 
    Else, raise an exception.
  """
  url = BASE_URL + page_number
  response = requests.get(url, headers=HEADERS)
  if response.status_code == 200:
    soup = BeautifulSoup(response.content, "html.parser")
    data = soup.find(id = "__NEXT_DATA__")
    content = data.contents[0]
    return content
  else:
    raise Exception("Error happened when fetching page", response.status_code)

def convert_to_dataframe(content: str):
  """
    Load the json string and get the list of ads from the result key.
    Normalize the content into a dataframe using pandas.
    Write the data frame into a parquet object.
  """
  json_content = json.loads(content)
  listing_ads = json_content['props']['pageProps']['initialReduxState']['search']['result']['list_ads']
  df = pd.json_normalize(listing_ads)
  return df
  # 


def fetch_all_and_save(path, number_of_pages):
  """
    Given a number of pages that need to be fetched, the program will first create an empty dataframe,
    fetch each page and concatenate all pages together.
    If a listing was sponsored, it will appeared in every page. As a result, duplicates will be dropped.
  """
  results = pd.DataFrame()
  for page_number in range(1, number_of_pages + 1):
    content = fetch_page(page_number=str(page_number))
    page_df = convert_to_dataframe(content=content)
    results = pd.concat([results, page_df])
    sleep(4)
  results = results.drop_duplicates(subset=["list_id"], keep="last")
  results.to_parquet(f"{path}/secondhand-boats-{current_date}.parquet")

  

  
