import sqlite3
from track import Track
from playlist import Playlist



def create_database():
    try:

        sqliteConnection = sqlite3.connect('FinalProjectDatabase.db')
        cursor = sqliteConnection.cursor()

        cursor.execute("DROP TABLE IF EXISTS Spotify_Data")

        create_spotify_table_sql ='''
        CREATE TABLE "Spotify_Data" (
	    "SongName"	TEXT,
	    "Artist"	TEXT,
	    "SentimentAnalysisScore"	INTEGER,
        "Playlist_ID"	TEXT
        );
        '''
        cursor.execute(create_spotify_table_sql)

        cursor.execute("DROP TABLE IF EXISTS Playlists")
        
        create_playlist_table_sql = '''
        CREATE TABLE "Playlists" (
	    "PlaylistName"	TEXT,
	    "Playlist_ID"	TEXT,
	    "Playlist_URL"	TEXT
        );'''

        cursor.execute(create_playlist_table_sql)
        
        sqliteConnection.commit()
        print("Record Updated successfully ")
        cursor.close()


    except sqlite3.Error as error:
        print("Failed to update sqlite table", error)
    finally:
        if sqliteConnection:
            sqliteConnection.close()
            print("The SQLite connection is closed")






def updateSqliteSpotifyTable(tracks, playlist):
    try:
        sqliteConnection = sqlite3.connect('FinalProjectDatabase.db')
        cursor = sqliteConnection.cursor()
        print("Connected to SQLite")

        playlist_id = playlist.playlist_id

        for track in tracks:
            name = track.name
            artist = track.artist
            sentiment_score = track.sentiment_score


            sql_song_query =  f"""INSERT INTO Spotify_Data (SongName, Artist, SentimentAnalysisScore, Playlist_ID)
            VALUES (?, ?, ?, ?);"""
            cursor.execute(sql_song_query, [name, artist, sentiment_score, playlist_id])

        sqliteConnection.commit()
        print("Record Updated successfully ")
        cursor.close()

    except sqlite3.Error as error:
        print("Failed to update sqlite table", error)
    finally:
        if sqliteConnection:
            sqliteConnection.close()
            print("The SQLite connection is closed")



def updateSqlitePlaylistTable(playlist):
    try:
        sqliteConnection = sqlite3.connect('FinalProjectDatabase.db')
        cursor = sqliteConnection.cursor()
        print("Connected to SQLite")


        playlist_name = playlist.name
        playlist_id = playlist.playlist_id
        playlist_url = playlist.playlist_url

        sql_playlist_query =  f"""INSERT INTO Playlists (PlaylistName, Playlist_ID, Playlist_URL)
        VALUES (?,?,?);"""
        cursor.execute(sql_playlist_query, [playlist_name, playlist_id, playlist_url])


        sqliteConnection.commit()
        print("Record Updated successfully ")
        cursor.close()

    except sqlite3.Error as error:
        print("Failed to update sqlite table", error)
    finally:
        if sqliteConnection:
            sqliteConnection.close()
            print("The SQLite connection is closed")





#playlist id: each song belongs to a playlist 
#tweet table not needed
#create playlist table (each one has a unique id auto incrementing) add songs to the song table. foreign key = playlist id
#





#songs have a foreign key for playlist table, 1st add a row for playlist table (null id)
#use select statment to find row and primary key associated with song 

# SELECT song id from playlist where == to playlist url
#playlist id is the foreign key to the song table 



#select_country_id_sql = '''
        # SELECT Id FROM Countries
        # WHERE playlist = ?
    #fetch 1
    #cur.execute(select_country_id_sql, eng_name
    #Result = cur.fetchone()


#for song in song list curr.execute


# Add result to playlist table
# find id of the playlist (last item)
# for each song add to the song table
# one column is playlist id
#
#query: insert into playlist
#query: select playlist id (to have a value to insert into songs table identifying the playlist)
#query: insert into songs

#homework 5 syntax
#select query where url is == to the playlist url

    

