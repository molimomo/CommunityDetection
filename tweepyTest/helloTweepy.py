import tweepy

auth = tweepy.OAuthHandler("IcwGFwvhCrnqhVCIZPFmt86KL", "dphQ4g30pQbJ6rlyS5rfsPLkCqbflwTDDNsPi4v7nOuvdj854L")
auth.set_access_token("14324937-FuxISyvlNUw6tWrWiCAwLOoOpxR8MSP3xsWdeJLhM", "guRlVWY7WRa6SDpUIMm6AWpJVt5zKn4Ssx3kMbisRUJNk")

api = tweepy.API(auth)

public_tweets = api.home_timeline()
for tweet in public_tweets:
	print tweet.text
