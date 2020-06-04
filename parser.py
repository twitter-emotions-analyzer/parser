from selenium import webdriver
from selenium.webdriver.common.keys import Keys
#from cassandra.cluster import Cluster
import time
import sys
if sys.version_info[0] < 3:
    import got
else:
    import got3 as got

from datetime import datetime
import json
import psycopg2
import pika
end_msg_recieved = False

def message_received(channel, method, properties, body):
   print(body) 
   print("Message recieved")

def ParseTweets(username):

    reload(sys)  
    sys.setdefaultencoding('utf-8')
    allTweetsJson = []
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--window-size=400,100")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    
    driver = webdriver.Chrome(chrome_options=chrome_options)
    print("Started")
    try:
        conn = psycopg2.connect(dbname='gakachu', user='gakachu', password='123123123', host='localhost')
        cursor = conn.cursor()
        cursor.execute('DROP TABLE IF EXISTS tweets')
        cursor.execute('CREATE TABLE tweets (id serial PRIMARY KEY, tweet_text text, username text, emotion text, date timestamp);')
        cursor.execute('DELETE FROM user_rate')
        conn.commit()

        print("Table initialized")
        rabbit_conn = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
        rabbit_channel = rabbit_conn.channel()
        driver.get("https://twitter.com/login")
        time.sleep(2)
        # LOGIN --------------
        print("Login started")
        usernameInput = driver.find_element_by_xpath("//input[@name=\"session[username_or_email]\"]")
        usernameInput.send_keys("annats68680142")
        password = driver.find_element_by_xpath("//input[@name=\"session[password]\"]")
        password.send_keys("gakachu")
        signInButton = driver.find_element_by_xpath("//div[@role=\"button\"]")
        signInButton.click()
        telInput = driver.find_elements_by_xpath("//input[@id=\"challenge_response\"]")
        if (len(telInput) > 0):
            telInput.send_keys("+79117096929")
            telSubmitButton = driver.find_element_by_xpath("//input[@id=\"email_challenge_submit\"]")
            telSubmitButton.click()
        print("Login ended")
        time.sleep(3)
        print(driver.current_url)
    
        # LOGIN END --------------
    
        #Get followers names
        followerLink = "https://twitter.com/" + username + "/followers"
        driver.get(followerLink)
        time.sleep(3)
        print(driver.current_url)
        time.sleep(3)

        followerNameSpans = driver.find_elements_by_xpath("//body//a[@role=\"link\"]//div[@dir=\"ltr\"]/span")
        followerNameTexts = []
        print(len(followerNameSpans))
        for followerNameSpan in followerNameSpans:
            followerNameTexts.append(driver.execute_script("return arguments[0].textContent", followerNameSpan)[1:])
        print("Got follower names")
        for followerName in followerNameTexts:
            print(followerName)
    
        peopleCounter = 0
        for followerName in followerNameTexts:
            print("Running cycle for follower")
            if peopleCounter > 2:
                break
            #Print persons tweets
            print("Follower Name: " + followerName)
            tweetCriteria = got.manager.TweetCriteria().setUsername(followerName).setMaxTweets(1)
            tweets = got.manager.TweetManager.getTweets(tweetCriteria)
            for tweet in tweets:
                print("user: " + tweet.username + " Tweet: " + tweet.text + "\n")
                allTweetsJson.append({'username': tweet.username, 'tweet': tweet.text, 'emotion': ""})
                tweetWithoutDollars = tweet.text.replace("$", " dollars")
                print(tweet.date)
                cursor.execute("INSERT INTO tweets (id, tweet_text, username, emotion, date) values (DEFAULT, $$" + tweetWithoutDollars + "$$, $$" + tweet.username + "$$, NULL, $$" + str(tweet.date) + "$$) RETURNING id;")
                conn.commit()
                user_db_id = cursor.fetchone()[0]
                rabbit_msg = {
                    'id': user_db_id
               }
                rabbit_channel.basic_publish(exchange='rater', routing_key='tweets', body=json.dumps(rabbit_msg))
                peopleCounter = peopleCounter + 1
            rabbit_msg_user = {
                'username': followerName
             }
            rabbit_channel.basic_publish(exchange='rater', routing_key='user', body=json.dumps(rabbit_msg_user))
    
    
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
                newTweetCriteria = got.manager.TweetCriteria().setUsername(newFollowerName).setMaxTweets(1)
                newTweets = got.manager.TweetManager.getTweets(newTweetCriteria)
                for newTweet in newTweets:
                    allTweetsJson.append({'username': newTweet.username, 'tweet': newTweet.text, 'emotion': ""})
                    print("user: " + newTweet.username + " Tweet: " + newTweet.text + "\n")
                    peopleCounter = peopleCounter + 1
                    tweetWithoutDollars = newTweet.text.replace("$", " dollars")
                    cursor.execute("INSERT INTO tweets (id, tweet_text, username, emotion, date) values (DEFAULT, $$" + tweetWithoutDollars + "$$, $$" + newTweet.username + "$$, NULL, $$" + str(newTweet.date) + "$$) RETURNING id;")
                    conn.commit()
                    user_db_id = cursor.fetchone()[0]
                    rabbit_msg = {
                        'id': user_db_id
                    }
                    #rabbit_channel.basic_publish(exchange='rater', routing_key='tweets', body=json.dumps(rabbit_msg))

                rabbit_msg_user = {
                    'username': newFollowerName
                }
                #rabbit_channel.basic_publish(exchange='rater', routing_key='user', body=json.dumps(rabbit_msg_user))
        print("ended")
        driver.close()
        end_msg = {
            'action': "end"
        }
        rabbit_channel.basic_publish(exchange='rater', routing_key='tweets', body=json.dumps(end_msg))
        rabbit_channel.exchange_declare(exchange="rater.out", exchange_type="topic")
        rabbit_channel.queue_declare(queue="rater.out")
        rabbit_channel.queue_bind(exchange="rater.out", queue="rater.out", routing_key="rater.out")
        rabbit_channel.basic_consume(queue="rater.out", on_message_callback=message_received)
        rabbit_channel.start_consuming()
        cursor.close()
        conn.close()
        rabbit_conn.close()
        return allTweetsJson
    except Exception as ex:
        print(ex)
        print("Exception occured")
        driver.close()
        cursor.close()
        conn.close()
        rabbit_conn.close()



#ParseTweets("NikolaiBaskov")
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
#     print("Tweet : " + tweet.text + " \n")index
