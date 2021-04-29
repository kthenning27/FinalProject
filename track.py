class Track:


    def __init__(self, name, track_id, artist):
        self.name = name
        self.track_id = track_id
        self.artist = artist
        self.sentiment_score = None

    def create_spotify_uri(self):
        return f"spotify:track:{self.track_id}"

    def set_sentiment_score(self, sentiment_score):
        self.sentiment_score = sentiment_score


