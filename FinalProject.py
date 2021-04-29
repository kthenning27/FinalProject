#########################################
##### Name:  Katie Henning          #####
##### Uniqname: khenning            #####
#########################################


import json
import requests
from requests_oauthlib import OAuth1
from collections import defaultdict
import secrets # file that contains your OAuth credentials
import pprint
import spacy
nlp = spacy.load('en_core_web_sm')
from collections import Counter
from spacy.lang.en.stop_words import STOP_WORDS
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from spacy.tokens import Doc
from track import Track
from playlist import Playlist
from spotify_client import Spotify_client
from musixmatch import Musixmatch
import datetime
import sqlite3
import sql_commands





sent_analyzer = SentimentIntensityAnalyzer()
nlp = spacy.load('en_core_web_sm')

CACHE_FILENAME = "final_project_twitter_cache.json"
CACHE_DICT = {}

COUNT = 25
TWITTER_BASEURL = "https://api.twitter.com/1.1/search/tweets.json"

client_key = secrets.API_KEY
client_secret = secrets.API_SECRET_KEY
access_token = secrets.ACCESS_TOKEN
access_token_secret = secrets.TWITTER_ACCESS_TOKEN_SECRET


spotify_client_id = secrets.SPOTIFY_CLIENT_ID
spotify_client_secret = secrets.SPOTIFY_CLIENT_SECRET
spotify_authorization_token = secrets.SPOTIFY_RECENTLY_PLAYED
spotify_user_id = secrets.USER_ID
#spotify_playlist_id = secrets.SPOTIFY_PLAYLIST_ID_TOKEN

twitter_oauth = OAuth1(client_key,
            client_secret=client_secret,
            resource_owner_key=access_token,
            resource_owner_secret=access_token_secret)





def test_oauth():
    ''' Helper function that returns an HTTP 200 OK response code and a
    representation of the requesting user if authentication was
    successful; returns a 401 status code and an error message if
    not. Only use this method to test if supplied user credentials are
    valid. Not used to achieve the goal of this assignment.'''

    url = "https://api.twitter.com/1.1/account/verify_credentials.json"
    auth = OAuth1(client_key, client_secret, access_token, access_token_secret)
    authentication_state = requests.get(url, auth=auth).json()
    return authentication_state


def open_cache():
    ''' Opens the cache file if it exists and loads the JSON into
    the CACHE_DICT dictionary.
    if the cache file doesn't exist, creates a new cache dictionary

    Parameters
    ----------
    None

    Returns
    -------
    The opened cache: dict
    '''
    try:
        cache_file = open(CACHE_FILENAME, 'r')
        cache_contents = cache_file.read()
        cache_dict = json.loads(cache_contents)
        cache_file.close()
    except:
        cache_dict = {}
    return cache_dict


def save_cache(cache_dict):
    ''' Saves the current state of the cache to disk

    Parameters
    ----------
    cache_dict: dict
        The dictionary to save

    Returns
    -------
    None
    '''
    dumped_json_cache = json.dumps(cache_dict)
    fw = open(CACHE_FILENAME,"w")
    fw.write(dumped_json_cache)
    fw.close()


def construct_unique_key(params):
    ''' constructs a key that is guaranteed to uniquely and
    repeatably identify an API request by its baseurl and params

    AUTOGRADER NOTES: To
    correctly test this using the autograder, use an underscore ("_")
    to join your baseurl the params and all the key-value pairs from params
    E.g., baseurl_key1_value1

    Parameters
    ----------
    params: dict
        A dictionary of param:value pairs

    Returns
    -------
    string
        the unique key as a string

        make url from base and params
    '''
    # s = Session()
    # p = Request('GET', baseurl, params=params).prepare()
    # url = p.url
    # uniquekey = uuid.uuid3(NAMESPACE_URL, url)
    param_strings = []
    connector = '_'
    for k in params.keys():
        param_strings.append(f'{k}_{params[k]}')
    unique_key = TWITTER_BASEURL + connector + connector.join(param_strings)
    return unique_key

def make_request(params):
    '''Make a request to the Web API using the baseurl and params

    Parameters
    ----------
    params: dictionary
        A dictionary of param:value pairs

    Returns
    -------
    dict
        the data returned from making the request in the form of
        a dictionary
    '''
    #print(params)
    r = requests.get(TWITTER_BASEURL, params=params, auth=twitter_oauth)
    return r.json()


def make_request_with_cache(username):
    '''Check the cache for a saved result for this baseurl+params:values
    combo. If the result is found, return it. Otherwise send a new
    request, save it, then return it.

    Do no include the print statements in your return statement. Just print them as appropriate.
    This, of course, does not ensure that you correctly retrieved that data from your cache,
    but it will help us to see if you are appropriately attempting to use the cache.

    Parameters
    ----------
    hashtag: string
        The hashtag to search for

    Returns
    -------
    dict
        the results of the query as a dictionary loaded from cache
        JSON
    '''
    # 0. baseurl = baseurl, params = ?
    # 1. constuct_unique_key
    # 2.search if it's in cache dict.keys()
    # 3. else make_request
    # 4. Cache_dict[unique_key] = result
    param_dict = {'from': username, 'count': COUNT}
    unique_key = construct_unique_key(param_dict)
    if unique_key in CACHE_DICT.keys():
        print("fetching cached data")
        return CACHE_DICT[unique_key]
    else:
        print ("making new request")
        api_results = make_request(param_dict)
        CACHE_DICT[unique_key] = api_results
        save_cache(CACHE_DICT)
        return CACHE_DICT[unique_key]


def get_tweet_text(tweet_data):
    ''' Finds the hashtag that most commonly co-occurs with the hashtag
    queried in make_request_with_cache().

    Parameters
    ----------
    tweet_data: dict
        Twitter data as a dictionary for a specific query
    hashtag_to_ignore: string
        the same hashtag that is queried in make_request_with_cache()
        (e.g. "#MarchMadness2021")

    Returns
    -------
    string
        the hashtag that most commonly co-occurs with the hashtag
        queried in make_request_with_cache()

    '''

    #2. search the results for hashtags
    #3. return the hashtag that appears the most besides the queried one
    #4. This could be done with a counter, return second highest hashtag?
    # for individual hashtag add 1, make a dictionary
    # of the hashtags and their count,
    #find a way to delete a key value pair in dictionary or do not count it at all
    tweet_text_dict = {}
    t_key = 0
    #print(f"length of tweetdata: {len(tweet_data['statuses'])}")
    for tweet in tweet_data['statuses']:
        t_key += 1
        tweet_text_dict[t_key] = tweet["text"]
    return tweet_text_dict

def remove_punctuation(text):
    punctuations = '''!()-[]{};:'"\,<>./?@#$%^&*_~‘’''' # list of special characters you want to exclude
    text_low_nopunct = ""
    for char in text:
        if char not in punctuations:
            text_low_nopunct = text_low_nopunct + char
    return text_low_nopunct

def remove_stop_words(text):
    words_nostop = []
    words = text.split()
    for word in words:
        if word not in STOP_WORDS:
            words_nostop.append(word)
    return words_nostop

def sentiment_scores(docx):
    return sent_analyzer.polarity_scores(docx.text)

Doc.set_extension("sentimenter",getter=sentiment_scores)

def listToString(s):

    # initialize an empty string
    str1 = " "

    # return string
    return (str1.join(s))

def tweet_sentiment_analysis(tweet_text_dict):
    tweet_sentiment_dict = {}
    t_key = 0
    for tweet_text in tweet_text_dict.values():
        lower_text = tweet_text.lower()
        text_low_nopunct = remove_punctuation(lower_text)
        text_low_nopunct_nostop = remove_stop_words(text_low_nopunct)
        list_ready = listToString(text_low_nopunct_nostop)
        sentiment_score = nlp(list_ready)._.sentimenter['compound']
        t_key += 1
        tweet_sentiment_dict[t_key] = sentiment_score
    return tweet_sentiment_dict


def completesearch(username):

    tweet_data = make_request_with_cache(username)
    # print(tweet_data)
    tweet_text_dict = get_tweet_text(tweet_data)

    tweet_sentiment_dict = tweet_sentiment_analysis(tweet_text_dict)


    recently_played = spotify_client.get_recently_played(limit=50)
    matching_songs = spotify_client.match_tweets_to_songs(tweet_sentiment_dict, recently_played, LYRICS_CACHE_DICT)
    playlist = spotify_client.create_playlist( username + "'s Sentiment Analysis Playlist", username)
    spotify_client.populate_playlist(playlist, matching_songs)
    sql_commands.create_database()
    sql_commands.updateSqliteSpotifyTable(matching_songs, playlist)
    sql_commands.updateSqlitePlaylistTable(playlist)























if __name__ == "__main__":
    if not client_key or not client_secret:
        print("You need to fill in CLIENT_KEY and CLIENT_SECRET in secret_data.py.")
        exit()
    if not access_token or not access_token_secret:
        print("You need to fill in ACCESS_TOKEN and ACCESS_TOKEN_SECRET in secret_data.py.")
        exit()








    spotify_client = Spotify_client(spotify_authorization_token, spotify_user_id)

    CACHE_DICT = open_cache()
    LYRICS_CACHE_DICT = spotify_client.open_lyrics_cache()


    username = input("Enter the handle of a Twitter user whose tweets you'd like to base your playlist off of (include @)  or 'exit' to quit. ")
    if username.lower() == 'exit':
        quit()
    else:
        completesearch(username)

    while True:
        user_input = input('Enter "exit" to quit or "back" to enter another username and create another playlist. ')
        if user_input.lower() == 'exit':
            quit()
        elif user_input.lower() == 'back':
            user_input = input("Enter the handle of a Twitter user whose tweets you'd like to base your playlist off of (include @)  or 'exit' to quit. ")
            if user_input.lower() == 'exit':
                 quit()
            else:
                completesearch(user_input)


    # username = user_input



    # tweet_data = make_request_with_cache(baseurl, username, count)
    # tweet_text_dict = get_tweet_text(tweet_data)
    #
    # tweet_sentiment_dict = tweet_sentiment_analysis(tweet_text_dict)
    # print(tweet_sentiment_dict)
    # recently_played = spotify_client.get_recently_played(limit=50)
    # matching_songs = spotify_client.match_tweets_to_songs(tweet_sentiment_dict, recently_played, LYRICS_CACHE_DICT)
    # print(matching_songs)






