from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream
import json
from pymongo import MongoClient

# Defining listener class for getting the streamingclass 

StdOutListener(StreamListener):
	def on_data(self, testdata2):
		tweet=json.loads(testdata2)
		created_at = tweet["created_at"]
		id_str = tweet["id_str"]
		text = tweet["text"]
		obj = {"created_at":created_at,"id_str":id_str,"text":text,}
		tweetind=collection.insert_one(obj).inserted_id
		print obj
		return True

	def on_error(self, status):
		print status

if __name__ == '__main__':
	l = StdOutListener()
	auth = tweepy.OAuthHandler("IcwGFwvhCrnqhVCIZPFmt86KL", "dphQ4g30pQbJ6rlyS5rfsPLkCqbflwTDDNsPi4v7nOuvdj854L")
	auth.set_access_token("14324937-FuxISyvlNUw6tWrWiCAwLOoOpxR8MSP3xsWdeJLhM", "guRlVWY7WRa6SDpUIMm6AWpJVt5zKn4Ssx3kMbisRUJNk")
	stream = Stream(auth,l)

# Below code  is for making connection with mongoDB
client = MongoClient()
client = MongoClient('localhost', 27017)
db = client.test_database
collection = db.test_collection 
stream.filter(track=['India'])


