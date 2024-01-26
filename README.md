# FinalProject

#Project Description:

The goal of this project is to access the Twitter API, request 10 tweets from a Twitter user (selected by user_input of this program), access the program user's "Recently Played" songs via their Spotify account, and return a playlist populated with songs whose lyrics have the same Sentiment Analysis Score as the 10 tweets originally requested.

#Special Requirements:

This program requires the user's Spotify ID (the number associated with their username which can be found in their "Profile"), as well as an OAuth key from the Spotify for Developer's page "Get Current User's Profile" (https://developer.spotify.com/console/get-current-user/). When the "Get Token" button is selected, the user must then check certain boxes to allow portions of their information to be used. These boxes or scopes are "user-read-private", "user-read-email", and "user-read-recently-played". This OAuth key should be copy-pasted and assigned to the variable "spotify_authorization_token". The user-id should  be copy-pasted and assigned to the variable "spotify_user_id". When running from the command line, the working directory should be changed to where the user wants the SQL database as well as the cache files to appear. 

#Required Packages:
MusixMatch
sqlite3
nltk
spacy
requests_oauthlib
JSON
math
webbrowser
Collections

#Interaction Instructions:
Once all of the required packages have been installed and the imported associated files ("track.py", "playlisy.py", "spotify_client.py", and "sql_commands.py") have been downloaded into the same folder as "FinalProject.py", run "Final_Project.py" from the command line. It will prompt the user for a username to base a playlist off of.

#Considerations:
The Spotify Oauth token entered expires after one hour. A new one will need to be genereated and pasted into the file for it to coninue to function after 1 hour. The error which denotes that this has expired is a KeyError that the items requested from the Spotify API do not exist. (KeyError: 'items')

