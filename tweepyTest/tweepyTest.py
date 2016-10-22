import json
import tweepy
import time
import pymongo
from pymongo import MongoClient

# Authentication 
CONSUMER_KEY = "IcwGFwvhCrnqhVCIZPFmt86KL"
CONSUMER_SECRET = "dphQ4g30pQbJ6rlyS5rfsPLkCqbflwTDDNsPi4v7nOuvdj854L"
ACCESS_KEY = "14324937-FuxISyvlNUw6tWrWiCAwLOoOpxR8MSP3xsWdeJLhM"
ACCESS_SECRET = "guRlVWY7WRa6SDpUIMm6AWpJVt5zKn4Ssx3kMbisRUJNk"
authid = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
authid.set_access_token(ACCESS_KEY, ACCESS_SECRET)
api = tweepy.API(authid)

# Insert data into MongoDB
def insertMongoDB(db, user, followers, followings):
	data = {"UserID" : user,
			"Followers" : followers,
			"Followings" : followings}
	db.collect1.insert_one(data)

# Connect to MongoDB
def connectMongoDB(database):
	client = MongoClient()
	db = client[database]
	return db

# Extract follower information from users
def getFollowers(name):
	followerList = []
	user = api.get_user(name)
	followers = tweepy.Cursor(api.followers, id=name).items()
	while True:
		try:
			follower = next(followers)
		except tweepy.TweepError:
			time.sleep(60 * 15)
			follower = next(followers)
		except	StopIteration:
			break
		followerList.append(follower.screen_name)
	return followerList

# Extract following information from users
def getFollowings(name):
	friendList = []
	user = api.get_user(name)
	friends_ids = tweepy.Cursor(api.friends_ids, screen_name=name).items()
	while True:
		try:
			friend_id = next(friends_ids)
			friend = api.get_user(id=friend_id)
		except tweepy.TweepError:
			time.sleep(60 *  15)
			friend_id = next(friends_ids)
			friend = api.get_user(id=friend_id)
		except	StopIteration:
			break
		friendList.append(friend.screen_name)
	return friendList

# Traverse targets and list their followers and following users
def main():
	# Target Database
	database = 'TwitterData'

	# Target List
	#ids=['molimomo', 'AngenZheng']
	ids=['lfc', 'chelseafc','arsenal','spursoffical','ManUtd']
	#ids=['lfc']	

	# Connect to database
	db = connectMongoDB(database)

	# Fetch data from Twitter and then store them into Mongo DB
	for name in ids:
		print("Fetching information of user: " + name)
		followers = getFollowers(name)
		print("Follower Count: " + str(len(followers)))
		for follower in followers:
			print("@"+follower)
		followings = getFollowings(name)
		print("Following Count: " + str(len(followings)))
		for following in followings:
			print("-"+following)
		insertMongoDB(db, name, followers, followings)
		print("Insertion is completed...")
	print("Data collection is finished...")	


# Call main function
if __name__ == '__main__':
	main()
