from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from cassandra.cluster import Cluster
import time
import sys
if sys.version_info[0] < 3:
    import got
else:
    import got3 as got

from datetime import datetime
import json

def ParseTweets(username):
    # export PATH=$PATH:"/Users/daniil/Downloads/parser/"
    allTweetsJson = []
    cluster = Cluster()
    session = cluster.connect('dev')
    session.execute('DROP TABLE tweets;')
    session.execute('CREATE TABLE dev.tweets (id UUID PRIMARY KEY, tweet_text text, user text, emotion text);')
    driver = webdriver.Chrome()
    # TRY TO PARSE WHOLE TWEET
    driver.set_window_size(400, 1000)
    driver.get("https://twitter.com/" + username)
    time.sleep(2)


    # GET USER NAME
    userNameSpan = driver.find_element_by_xpath("//div[@dir=\"ltr\"]/span")
    userNameText = driver.execute_script("return arguments[0].textContent", userNameSpan)[1:]

    # LOGIN --------------
    linkToFollowers = "/" + userNameText + "/followers"
    followersElement = driver.find_element_by_xpath("//a[@href=\"" + linkToFollowers + "\"]")
    followersElement.click()
    time.sleep(1)
    loginLink = "/login"
    loginButton = driver.find_element_by_xpath("//a[@href=\"" + loginLink + "\"]")
    loginButton.click()
    time.sleep(1)

    username = driver.find_element_by_xpath("//input[@name=\"session[username_or_email]\"]")
    username.send_keys("annats68680142")
    password = driver.find_element_by_xpath("//input[@name=\"session[password]\"]")
    password.send_keys("gakachu")
    signInButton = driver.find_element_by_xpath("//div[@role=\"button\"]")
    signInButton.click()
    time.sleep(3)

    # LOGIN END --------------

    #Get followers names
    linkToFollowers = "/" + userNameText + "/followers"
    followersElement = driver.find_element_by_xpath("//a[@href=\"" + linkToFollowers + "\"]")
    followersElement.click()
    time.sleep(3)
    followerNameSpans = driver.find_elements_by_xpath("//body//a[@role=\"link\"]//div[@dir=\"ltr\"]/span")
    followerNameTexts = []
    for followerNameSpan in followerNameSpans:
        followerNameTexts.append(driver.execute_script("return arguments[0].textContent", followerNameSpan)[1:])

    peopleCounter = 0
    for followerName in followerNameTexts:
        if peopleCounter > 3:
            break
        #Print persons tweets
        print("Follower Name: " + followerName)
        tweetCriteria = got.manager.TweetCriteria().setUsername(followerName).setMaxTweets(5)
        tweets = got.manager.TweetManager.getTweets(tweetCriteria)
        for tweet in tweets:
            print("user: " + tweet.username + " Tweet: " + tweet.text + "\n")
            allTweetsJson.append({'username': tweet.username, 'tweet': tweet.text, 'emotion': ""})
            tweetWithoutDollars = tweet.text.replace("$", " dollars")
            session.execute("insert into tweets (id, tweet_text, user, emotion) values (now(), $$" + tweetWithoutDollars + "$$, $$" + tweet.username + "$$, NULL) ;")
            peopleCounter = peopleCounter + 1


        #Go to persons page
        followerLink = "https://twitter.com/" + followerName + "/followers"
        driver.get(followerLink)
        time.sleep(3)

        #Get persons followers
        newFollowerNameSpans = driver.find_elements_by_xpath("//body//a[@role=\"link\"]//div[@dir=\"ltr\"]/span")
        newFollowerNameTexts = []
        for newFollowerNameSpan in newFollowerNameSpans:
            newFollowerNameTexts.append(driver.execute_script("return arguments[0].textContent", newFollowerNameSpan)[1:])
        for newFollowerName in newFollowerNameTexts:
            print("!!!!!!! NEW FOLLOWER CYCLE FOR USER " + newFollowerName)
            newTweetCriteria = got.manager.TweetCriteria().setUsername(newFollowerName).setMaxTweets(5)
            newTweets = got.manager.TweetManager.getTweets(newTweetCriteria)
            for newTweet in newTweets:
                allTweetsJson.append({'username': newTweet.username, 'tweet': newTweet.text, 'emotion': ""})
                print("user: " + newTweet.username + " Tweet: " + newTweet.text + "\n")
                peopleCounter = peopleCounter + 1
                tweetWithoutDollars = newTweet.text.replace("$", " dollars")
                session.execute("insert into tweets (id, tweet_text, user, emotion) values (now(), $$" + tweetWithoutDollars + "$$, $$" + newTweet.username + "$$, NULL) ;")
    driver.close()
    return allTweetsJson