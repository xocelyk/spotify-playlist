import spotipy
import spotipy.util as util
import time
import datetime
from threading import Timer
import time
import csv

your_client_id = ''# your client id
your_client_secret = ''# your client secret

__all__ = ['Spotiwhy']

class Spotiwhy(object):

# could make these private
	__slots__ = ['username', 'scope', 'token', 'spotify', 'monthly_tracker_on', 'last_monthly_update', 'month']

	def __init__(self):
		self.username = str()
		self.scope = 'user-top-read, playlist-modify-public, playlist-read-private, user-read-currently-playing, user-read-private, user-library-read, user-read-recently-played'
		self.token = util.prompt_for_user_token(self.username, self.scope, client_id=your_client_id, client_secret=your_client_secret, redirect_uri='http://localhost:8888/callback')
		self.spotify = spotipy.Spotify(auth=self.token)
		self.monthly_tracker_on = False
		self.last_monthly_update = str()
		self.month = datetime.timedelta(days=30)


	def find_artist_id(self, artist):
		# artist = input('search artist: ')
		results = self.spotify.search(q=artist, limit=1, type='artist')
		artist_id = results['artists']['items'][0]['uri']
		return artist_id

	def find_playlist_id(self, playlist):
		results = spotify.search(q=playlist, limit=1, type='playlist')
		print(results['playlists'])
		print(results['playlists']['items'])
		playlist_id = results['playlists']['items'][0]['uri']
		return playlist_id


	def generate_playlist(self, name, duration='short_term', limit=50):
		results = self.spotify.current_user_top_tracks(limit=limit, time_range=duration)
		top_track_ids = [item['uri'] for item in results['items']]
		self.spotify.user_playlist_create(self.username, name)
		playlists = self.spotify.user_playlists(self.username)
		for playlist in playlists['items']:
			if playlist['name'] == name:
				self.spotify.user_playlist_add_tracks(self.username, playlist['uri'], top_track_ids)


	def generate_custom_playlist(self):
		while True:
			number_songs = int(input("How many songs would you like to display? (max 50) "))
			if number_songs < 51 and number_songs > 0:
				break
			print('Please enter a valid number.')
		while True:
			duration = int(input("Select (1) 30 days, (2) 90 days, or (3) all time. Type 1, 2, or 3. "))
			if duration > 0 and duration < 4:
				break
			print("Please enter a valid number.")
		if duration == 1:
			duration = 'short_term'
		elif duration == 2:
			duration = 'medium_term'
		elif duration == 3:
			duration = 'long_term'

		results = self.spotify.current_user_top_tracks(limit=number_songs,time_range=duration)

		top_tracks = []
		for item in results['items']:
			track = item['name']
			top_tracks.append(track)

		top_track_ids = [item['uri'] for item in results['items']]
		name = "Top " + str(number_songs) + " Songs"
		if duration == 'short_term':
			name += ': Past 30 days'
		elif duration == 'medium_term':
			name += ': Past 90 days'
		elif duration == 'long_term':
			name += ': All Time'
		playlists = self.spotify.user_playlists(self.username)
		self.spotify.user_playlist_create(self.username, name)
		playlists = self.spotify.user_playlists(self.username)
		for playlist in playlists['items']:
			if playlist['name'] == name:
				self.spotify.user_playlist_add_tracks(self.username, playlist['uri'], top_track_ids)

		print('\n')
		print(name)
		for track in range(len(top_tracks)):
			print(str((track+1)) + '. ' + str(top_tracks[track]))

		print('Check Spotify! Your custom playlist has been created.')

	def monthly_tracker(self):
		date_name = str(datetime.datetime.today())[5:10]
		date = datetime.datetime.today()
		durations = ['short_term', 'medium_term', 'long_term']		
		if self.monthly_tracker_on:
			date2 = self.last_monthly_update + self.month
			if date2 > date:
				self.last_monthly_update = date
				for duration in durations:
					if duration == 'short_term':
						name = '30-Day Top Songs - ' + date_name
					elif duration == 'medium_term':
						name = '90-Day Top Songs - ' + date_name
					else:
						name = 'All Time Top Songs - ' + date_name
					self.generate_playlist(name)
		else:
			self.monthly_tracker_on = True
			self.last_monthly_update = date
			for duration in durations:
				if duration == 'short_term':
					name = '30-Day Top Songs - ' + date_name
				elif duration == 'medium_term':
					name = '90-Day Top Songs - ' + date_name
				else:
					name = 'All Time Top Songs - ' + date_name
				self.generate_playlist(name, duration=duration)
			# create new playlist, add to csv?

	def generate_track_length(self, track_name):
		results = self.spotify.search(q=track_name, limit=1)
		duration = results['tracks']['items'][0]['duration_ms']
		return duration

	def scrobbler(self):
		song_uri = ''
		write_csv = False
		HEADERS	= ['Time', 'Song', 'Artists']

		while True:
			try:
				new_song_info = self.spotify.current_user_playing_track()
				new_song_uri = new_song_info['item']['uri']
				new_song_name = new_song_info['item']['name']
				new_song_artist = [new_song_info['item']['artists'][0]['name']]
				if '(feat. ' in new_song_name:
					i1 = new_song_name.find('(feat. ')
					i2 = new_song_name.find(')')
					feat_artists = new_song_name[i1+7:i2].split(' & ')
					new_song_artist.extend(feat_artists)
					artists = ', '.join(new_song_artist)
				else:
					artists = new_song_artist[0]
				if new_song_uri != song_uri:
					song_uri = new_song_uri
					print('{0} - {1}'.format(new_song_name, artists))
					write_info = [str(datetime.datetime.now()), new_song_name]
					write_info.extend(new_song_artist)
					write_csv = True

			except:
				pass

			if write_csv:
				with open('spotiwhy-scrobbler.csv', 'a') as writeFile:
					writer = csv.writer(writeFile)
					writer.writerow(write_info)
					writeFile.flush()
			time.sleep(30)

	def recs(self):
		top_tracks = self.spotify.current_user_top_tracks(limit=50, time_range = 'short_term')
		top_track_ids = [item['uri'] for item in top_tracks['items']]
		results = self.spotify.recommendations(seed_tracks=top_track_ids)
		rec = []
		for item in results['items']:
			track = item['name']
			rec.append(track)

	def test(self):
		results = self.spotify.current_user_top_tracks(limit=1,time_range='long_term')
		top_tracks = []
		for item in results['items']:
			track = item['name']
			print(item)


if __name__ == "__main__":
	# Optional username from the Terminal
	from sys import argv
	s = Spotiwhy()
	if len(argv) > 1:
		s.username = argv[1]
	else:
		s.username = input('username: ')
	s.generate_custom_playlist()
 

