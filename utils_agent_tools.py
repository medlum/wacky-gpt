from langchain.agents import Tool
from langchain.tools import StructuredTool
import requests
import json
import time
from bs4 import BeautifulSoup
import streamlit as st
from langchain_community.utilities import WikipediaAPIWrapper
from langchain.agents import Tool
from langchain.tools import StructuredTool
import requests
import time
import datetime
from langchain_community.tools import BraveSearch
from youtubesearchpython import VideosSearch

# -------- wikipedia --------#

wikipedia = WikipediaAPIWrapper()

wikipedia_tool = Tool(
    name='wikipedia',
    func=wikipedia.run,
    description="Use this function to look up information and knowledge"
)


# -------- today's date --------#


def time(text: str) -> str:
    weekdays_map = {i: ['Monday', 'Tuesday', 'Wednesday', 'Thursday',
                        'Friday', 'Saturday', 'Sunday'][i] for i in range(7)}

    today = datetime.datetime.today()
    day = weekdays_map[today.weekday()]

    return today, day


time_tool = StructuredTool.from_function(
    func=time,
    name='today_date',
    description="Use this function to find out today's date"
)
# ---- news headlines ---#

# webscrape on CNA headlines


def news_headlines(genre: str):

    url = "https://www.channelnewsasia.com"
    response = requests.get(url)
    if response.status_code == 200:
        news = []
        soup = BeautifulSoup(response.text, 'html.parser')
        headlines = soup.find('body').find_all('h6')  # headlines at h6
        for index, headline in enumerate(headlines):
            news.append(f"{index+1}. {headline.text.strip()}.")
            if index == 4:
                break
        return '\n'.join(news)
        # return news
    else:
        return "No response from news provider."


news_tool = StructuredTool.from_function(
    func=news_headlines,
    name="news_headlines",
    description="use this function to provide news headlines"
)


# ---- online search with brave search ---#
braveSearch = BraveSearch.from_api_key(
    api_key=st.secrets['brave_api'], search_kwargs={"count": 3})

braveSearch_tool = Tool(
    func=braveSearch,
    name="brave_search",
    description="use this function to answer questions about most current events"
)

# --------- image tools ------------#

# search image with bravesearch


def query_bravesearch_image(query: str):
    brave_api_key = "BSANRhMz7xnB_dIA1nzDwO2uaw3cpVA"
    url = "https://api.search.brave.com/res/v1/images/search"
    headers = {
        "X-Subscription-Token": brave_api_key
    }
    params = {
        "q": query,
        "count": 1,
    }
    response = requests.get(url, headers=headers, params=params)
    data = response.json()

    try:
        img_path = data["results"][0]["properties"]["url"]
        return f'<img width="100%" height="320" src="{img_path}"/>'
    except IndexError:
        return "Try again later"

    # img_path = data["results"][0]["properties"]["url"]
    # return f'<img width="100%" height="320" src="{img_path}"/>'


img_search_tool = StructuredTool.from_function(
    func=query_bravesearch_image,
    name="image_bravesearch",
    description="use this function to search for image url and put the url into html."
)


# ---- weather forecast ---#

# nea api - 4 days forecast


def weather4days(url):
    url = "https://api-open.data.gov.sg/v2/real-time/api/four-day-outlook"
    res = requests.get(url)
    data = json.dumps(res.json(), indent=4)
    return data


weather4days_tool = StructuredTool.from_function(
    func=weather4days,
    name='nea_api_4days',
    description="Use this tool to find out the weather forecast for next 4 days in singapore"
)

# nea api - 24 hours forecast


def weather24hr(url):
    url = "https://api-open.data.gov.sg/v2/real-time/api/twenty-four-hr-forecast"
    res = requests.get(url)
    data = json.dumps(res.json(), indent=4)
    return data


weather24hr_tool = StructuredTool.from_function(
    func=weather24hr,
    name='nea_api_24hr',
    description="Use this tool to find out the weather forecast in the next 24 hour in singapore"
)


def youTubeSearch(query: str):

    videosSearch = VideosSearch(query, limit=1)
    search = videosSearch.result()
    for key in search["result"]:
        link = key['link'][32:]
        # src = f"https://www.youtube.com/embed/{link}"

    return f'<iframe width="400" height="215" src="https://www.youtube.com/embed/{link}" title="YouTube video player" frameborder="0" allow="accelerometer; encrypted-media;"></iframe>'


youTubeSearch_tool = StructuredTool.from_function(
    func=youTubeSearch,
    name='youTubeSearch',
    description="Use this tool to play YouTube videos"
)

toolkit = [weather4days_tool,
           weather24hr_tool,
           img_search_tool,
           news_tool,
           time_tool,
           youTubeSearch_tool,
           braveSearch_tool]
