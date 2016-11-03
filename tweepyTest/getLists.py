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
followerCnt = 0
followingCnt = 0

# Target Database
database = 'TwitterData'

def updateCollection(db, user, data, isFollower):
	original = db.collect1.find_one({'UserID':user})
	if original != None:
		if isFollower == True:
			if "Followers" in original:
				print("Update Followers!")
				original['Followers'].append(followerList)
				db.collect1.update_one({'UserID':user}, {'$set':{'Followers':original['Followers']}})
			else:
				db.collect1.update_one({'UserID':user}, {'$set':{'Followers':data}})
		else:
			if "Followings" in original:
				print("Update Followings!")
				original['Followings'].append(friendList)
				db.collect1.update_one({'UserID':user}, {'$set':{'Followings':original['Followings']}})
			else:
				db.collect1.update_one({'UserID':user}, {'$set':{'Followings':data}})
	else:
		print("Insert New Document!")
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

def getInfo(name):
	user = api.get_user(name)
	friends_ids = tweepy.Cursor(api.friends_ids, screen_name=name).items()
	followers = tweepy.Cursor(api.followers, id=name).items()
	isFollower = True
	endFollower = False
	endFollowing = False

	while True:
		try:
			if(isFollower == True):
				if(endFollower == True and endFollowing == False):
					friend_id = next(friends_ids)
					friend = api.get_user(id=friend_id)
				elif(endFollower == True and endFollowing == True):
					break
				else:
					follower = next(followers)
			else:
				if(endFollowing == True and endFollower == False):
					follower = next(followers)
				elif(endFollowing == True and endFollower == True):
					break
				else:
					friend_id = next(friends_ids)
					friend = api.get_user(id=friend_id)

		except tweepy.TweepError:
			if(isFollower == True):
				updateCollection(db, name, followerList, isFollower)
				del followerList[:]
			else:
				updateCollection(db, name, friendList, isFollower)
				del friendList[:]
			print("Waiting for rate limit...")
			isFollower = ~isFollower
			time.sleep(60 * 15)

		except StopIteration:
			if(isFollower == True):
				updateCollection(db, name, followerList, isFollower)
				del followerList[:]
				endFollower = True
			else:
				updateCollection(db, name, friendList, isFollower)
				del friendList[:]
				endFollowing = True
			isFollower = ~isFollower
			if(endFollower == True and endFollowing == True):
				print("Bye!")
				break
			else:
				continue

		if(isFollower == True):
			global followerCnt
			global followingCnt
			followerCnt = followerCnt + 1
			print("Appending follower data @ " + str(follower.screen_name)+" ("+str(followerCnt)+")")
			followerList.append(follower.screen_name)
		else:
			followingCnt = followingCnt + 1
			print("Appending following data - " + str(friend.screen_name)+" ("+str(followingCnt)+")")	
			friendList.append(friend.screen_name)

# Traverse targets and list their followers and following users
def main():
	# Target List
	#ids=['molimomo']
	ids=['molimomo', 'AngenZheng']
	#ids=['lfc', 'chelseafc','arsenal','spursoffical','ManUtd']
	#ids=['arsenal']	
	
	# Fetch data from Twitter and then store them into Mongo DB
	for name in ids:
		global followerCnt
		global followingCnt
		folllowerCnt = 0
		followingCnt = 0
		print("Fetching information of user: " + name)
		getInfo(name)
	print("Data collection is finished...")	

# Call main function
if __name__ == '__main__':
	# Connect to database
	db = connectMongoDB(database)
	main()
