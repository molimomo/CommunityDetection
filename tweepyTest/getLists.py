import json
import tweepy
import time
import pymongo
from pymongo import MongoClient

# Authentication 
CONSUMER_KEY = ""
CONSUMER_SECRET = ""
ACCESS_KEY = ""
ACCESS_SECRET = ""
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


def updateList(db, targetDoc, name, targetField, updateData):
	db.collect1.update({targetDoc:name},{'$push':{targetField:{'$each':updateData}}})
	
def updateCollection(db, user, data, isFollower):
	original = db.collect1.find_one({'UserID':user})
	if original != None:
		if isFollower == True:
			if "Followers" in original:
				print("Update Followers!")
				updateList(db,'UserID', user, 'Followers', followerList)
				#original['Followers'].append(followerList)
				#db.collect1.update_one({'UserID':user}, {'$set':{'Followers':original['Followers']}})
			else:
				db.collect1.update_one({'UserID':user}, {'$set':{'Followers':data}})
		else:
			if "Followings" in original:
				print("Update Followings!")
				updateList(db,'UserID', user, 'Followings', friendList)
				#original['Followings'].append(friendList)
				#db.collect1.update_one({'UserID':user}, {'$set':{'Followings':original['Followings']}})
			else:
				print("insert new following")
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

# Get followers / followings from a given user ID
def getInfo(name):
	
	# Get user information
	user = api.get_user(name)

	# Get user's following list (ID) 
	friends_ids = tweepy.Cursor(api.friends_ids, screen_name=name).items()

	# Get user's follower list
	followers = tweepy.Cursor(api.followers, id=name).items()

	isFollower = True
	endFollower = False
	endFollowing = False
	global followerList
	global friendList
	while True:
		# Get next follower/following from user's list
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

		# (Exception) Reach the twitter rate limit
		except tweepy.TweepError:
			# insert current user list into Database	
			if(isFollower == True):
				updateCollection(db, name, followerList, isFollower)
				del followerList[:]
			else:
				print("Hello?")
				updateCollection(db, name, friendList, isFollower)
				del friendList[:]
			print("Waiting for rate limit...")

			# Switch collection target
			isFollower = ~isFollower

			# Wait for 15 minutes
			time.sleep(60 * 15)
			continue

		# (Exception) Reach the end of followers or followings
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
		
		# If there is no exception, add userId into list
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
	#ids=['lfc', 'chelseafc','arsenal','spursoffical','ManUtd']
	ids=['lfc']	
	
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
