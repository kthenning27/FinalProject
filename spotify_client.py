import requests
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import json
from musixmatch import Musixmatch
from track import Track
from playlist import Playlist
import secrets
import numpy
import math
import webbrowser

LYRICS_CACHE_FILENAME = "final_project_lyrics_cache.json"
LYRICS_CACHE_DICT = {}


EPSILON = 0.1

musix_match_api_key = secrets.MUSIX_MATCH_API_KEY



class Spotify_client:

    def __init__(self, authorization_token, user_id):
        self.authorization_token = authorization_token
        self.user_id = user_id

    def open_lyrics_cache(self):
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
            cache_file = open(LYRICS_CACHE_FILENAME, 'r')
            cache_contents = cache_file.read()
            cache_dict = json.loads(cache_contents)
            cache_file.close()
        except:
            cache_dict = {}
        return cache_dict


    def save_lryics_cache(self, cache_dict):
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
        fw = open(LYRICS_CACHE_FILENAME,"w")
        fw.write(dumped_json_cache)
        fw.close()

    def construct_unique_key(self, track_name, track_artist):
        ''' constructs a key that is guaranteed to uniquely and
        repeatably identify an API request by its baseurl and params

        AUTOGRADER NOTES: To correctly test this using the autograder, use an underscore ("_")
        to join your baseurl with the params and all the key-value pairs from params
        E.g., baseurl_key1_value1

        Parameters
        ----------
        baseurl: string
            The URL for the API endpoint
        params: dict
            A dictionary of param:value pairs

        Returns
        -------
        string
            the unique key as a string

            make url from base and params
        '''
        unique_key = track_name + track_artist
        return unique_key

    def make_musixmatch_request_using_cache(self, track_name, track_artist, LYRICS_CACHE_DICT):
        ''''makes use of the cache_dict to check if the URL
        has been searched for before


        Parameters
        ----------
        url: sting
            the url searched for in the cahe dict
        CACHE_DICT: dict
            the json file with cached information
        -------
        dict key
            the key in the CAHE_DICT corresponsing to the URL in json format

        '''
        musixmatch = Musixmatch(musix_match_api_key)

        unique_key = self.construct_unique_key(track_name, track_artist)

        if unique_key in LYRICS_CACHE_DICT.keys():
            print("using cache")
            return LYRICS_CACHE_DICT[unique_key]
        else:
            print ("Fetching")
            song = musixmatch.matcher_lyrics_get(track_name, track_artist)
            LYRICS_CACHE_DICT[unique_key] = song
            self.save_lryics_cache(LYRICS_CACHE_DICT)
            return LYRICS_CACHE_DICT[unique_key]


    def get_api_requests(self, url):
        response = requests.get(
            url,
            headers = { "Content-Type": "application/json", "Authorization": f"Bearer {self.authorization_token}"}
        )
        return response

    def post_api_request(self, url, data):
        response = requests.post(
            url,
            data=data,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.authorization_token}"
            }
        )
        return response

    def get_recently_played(self, limit = 50):
        url = f"https://api.spotify.com/v1/me/player/recently-played?limit={limit}"
        response = self.get_api_requests(url)
        response_json = response.json()
        #print(response_json)
        tracks = [Track(track["track"]["name"], track["track"]["id"], track["track"]["artists"][0]["name"]) for track in response_json["items"]]
        return tracks

    def match_tweets_to_songs(self, tweet_sentiment_dict, tracks, LYRICS_CACHE_DICT):
        sent_analyzer = SentimentIntensityAnalyzer()
        #print(f"Sentiment dict: {tweet_sentiment_dict}")
        matching_songs = []
        sentiment_score_list = []
        sentiment_score_dict = {}
        s_key = 0
        song_list =[]


        # Get sentiment analysis for all tracks
        for track in tracks:
            song = self.make_musixmatch_request_using_cache(track.name, track.artist, LYRICS_CACHE_DICT)
            song_lyrics = song['message']['body']['lyrics']['lyrics_body']
            sentiment_score = sent_analyzer.polarity_scores(song_lyrics)
            track.set_sentiment_score(sentiment_score["compound"])
            #print(f"Track {track.name} sentiment score: {track.sentiment_score}")

        # Iterate through each tweet you'd like to find a song for.
        for tweet_key, tweet_sent_score in tweet_sentiment_dict.items():
            #print(f"Matching tweet {tweet_key} with sent score {tweet_sent_score}")
            for track in tracks:
                min_sent_value = tweet_sent_score - EPSILON
                max_sent_value = tweet_sent_score + EPSILON
                if track.sentiment_score > min_sent_value and track.sentiment_score < max_sent_value:
                    if track not in matching_songs:
                        matching_songs.append(track)
                        break

        return  matching_songs


    def create_playlist(self, name, username):
        data = json.dumps({
            "name": name,
            "description": "Playlist based on the sentiment analysis of tweets by " + username,
            "public": True
        })
        url = f"https://api.spotify.com/v1/users/{self.user_id}/playlists"
        response = self.post_api_request(url, data)
        response_json = response.json()
        playlist_id = response_json["id"]
        playlist_url = response_json["external_urls"]["spotify"]
        playlist = Playlist(name, playlist_id, playlist_url)
        return playlist

    def populate_playlist(self, playlist, matching_songs):
        #track_ids = [track.track_id for track in matching_songs]
        track_uris = [track.create_spotify_uri() for track in matching_songs]
        data = json.dumps(track_uris)
        url = f"https://api.spotify.com/v1/playlists/{playlist.playlist_id}/tracks"
        response = self.post_api_request(url, data)
        response_json = response.json()
        webbrowser.open(playlist.playlist_url)
        return response_json