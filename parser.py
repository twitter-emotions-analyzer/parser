from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
import sys
if sys.version_info[0] < 3:
    import got
else:
    import got3 as got

from datetime import datetime
driver = webdriver.Chrome()
driver.set_window_size(400, 1000)
driver.get("https://twitter.com/NikolaiBaskov")
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

try:
    for followerName in followerNameTexts:
        #Print persons tweets
        print("Follower Name: " + followerName)
        tweetCriteria = got.manager.TweetCriteria().setUsername(followerName).setMaxTweets(1)
        tweets = got.manager.TweetManager.getTweets(tweetCriteria)
        for tweet in tweets:
            print("user: " + tweet.username + " Tweet: " + tweet.text + "\n")


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
            newTweetCriteria = got.manager.TweetCriteria().setUsername(newFollowerName).setMaxTweets(1)
            newTweets = got.manager.TweetManager.getTweets(newTweetCriteria)
            for newTweet in newTweets:
                print("user: " + newTweet.username + " Tweet: " + newTweet.text + "\n")
except:
    print("------------------------------- An ERROR OCCURED! -----------------------------")
        


# body = driver.find_element_by_tag_name("body")
# counter=0
# while(counter < 10):
#     body.send_keys(Keys.PAGE_DOWN)
#     time.sleep(0.5)
#     counter=counter+1
# tweets = driver.find_elements_by_xpath("//div[@data-testid=\"tweet\"]//div[@lang=\"ru\"]/span")
# for tweet in tweets:
#     tweet_text = driver.execute_script("return arguments[0].textContent", tweet)
#     print(tweet_text + "\n\n")
# driver.close()

# tweetCriteria = got.manager.TweetCriteria().setUsername(userNameText).setMaxTweets(10)
# tweets = got.manager.TweetManager.getTweets(tweetCriteria)
# for tweet in tweets:
#     print("Username : " + tweet.username + " \n")
#     print("Date: " + tweet.date.strftime("%d:%m:%Y") + "\n")
#     print("Tweet : " + tweet.text + " \n")
