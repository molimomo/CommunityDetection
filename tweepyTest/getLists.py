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

# Global data
followers = None
friends_ids = None
followerList = []
friendList = []
counter = 0

# Target Database
database = 'TwitterData'

def updateCollection(db, user, data, isFollower):
	original = db.collect1.find_one({'UserID':user})
	if original != None:
		if isFollower == True:
			original['Followers'].append(followerList)
			db.collect1.update_one({'UserID':user}, {'$set':{'Followers':original['Followers']}})
		else:
			original['Followings'].append(friendList)
			db.collect1.update_one({'UserID':user}, {'$set':{'Followings':original['Followings']}})
	else:
		if isFollower == True:
			insertMongoDB(db, user, data, "Followers")
		else:
			insertMongoDB(db, user, data, "Followings")

# Insert data into MongoDB
def insertMongoDB(db, user, data, target):
	data = {"UserID" : user,
			target : data}
	db.collect1.insert_one(data)

# Connect to MongoDB
def connectMongoDB(database):
	client = MongoClient()
	db = client[database]
	return db

# Extract follower information from users
def getFollowers(name):
	#user = api.get_user(name)
	#followers = tweepy.Cursor(api.followers, id=name).items()
	while True:
		try:
			follower = next(followers)
		except tweepy.TweepError:
			updateDocument(db, name, followerList, True)
			del followList[:]
			time.sleep(60 * 15)
			return -1
			#getFollowings(name);
			#follower = next(followers)
		except	StopIteration:
			return 0
			#break
		followerList.append(follower.screen_name)
		print("@ " + follower.screen_name)
	#return followerList

# Extract following information from users
def getFollowings(name):
	#user = api.get_user(name)
	#friends_ids = tweepy.Cursor(api.friends_ids, screen_name=name).items()
	while True:
		try:
			friend_id = next(friends_ids)
			friend = api.get_user(id=friend_id)
		except tweepy.TweepError:
			updateDocument(db, name, friendList, False)
			del friendList[:]
			time.sleep(60 * 15)
			return -1
			#getFollowers(name);
			#friend_id = next(friends_ids)
			#friend = api.get_user(id=friend_id)
		except	StopIteration:
			return 0
			#break
		friendList.append(friend.screen_name)
		print("- " + friend.screen_name)
	#return friendList

# Traverse targets and list their followers and following users
def main():
	# Target List
	ids=['molimomo']
	#ids=['molimomo', 'AngenZheng']
	#ids=['lfc', 'chelseafc','arsenal','spursoffical','ManUtd']
	#ids=['arsenal']	
	
	# Fetch data from Twitter and then store them into Mongo DB
	for name in ids:
		user = api.get_user(name)
		friends_ids = tweepy.Cursor(api.friends_ids, screen_name=name).items()
		followers = tweepy.Cursor(api.followers, id=name).items()
		print("Fetching information of user: " + name)
		while True:
			if(getFollowers(name)!=0):
				if(getFollowings(name)!=0):
					continue
				continue
		#followers = getFollowers(name)
		#getFollowers(name)
		#print("Follower Count: " + str(len(followerList)))
		#for follower in followerList:
		#	print("@"+follower)
		#followings = getFollowings(name)
		#getFollowings(name)
		#print("Following Count: " + str(len(friendList)))
		#for following in friendList:
		#	print("-"+following)
		#insertMongoDB(db, name, followerList, friendList)
		#print("Insertion is completed...")
	print("Data collection is finished...")	


# Call main function
if __name__ == '__main__':
	# Connect to database
	db = connectMongoDB(database)

	main()
	
	#updateCollection(db, 'molimomo', 123)
