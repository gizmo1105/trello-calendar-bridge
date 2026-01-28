"""
Trrello client utilities.
"""
import requests

from config import TRELLO_KEY, TRELLO_TOKEN, BOARD_ID

def fetch_cards():
    """
    Fetch all cards from the specified Trello board.
    
    Args:
        None

    Returns:
        list: List of card dictionaries.    
    """
    url = f"https://api.trello.com/1/boards/{BOARD_ID}/cards"
    params = {
        "key": TRELLO_KEY,
        "token": TRELLO_TOKEN,
        "fields": "id,name,desc,due,url,closed,labels"
    }
    resp = requests.get(url, params=params)
    resp.raise_for_status()
    return resp.json()
