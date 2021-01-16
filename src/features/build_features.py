import os
from os import path
import numpy as np
import pandas as pd
import json
from dotenv import load_dotenv, find_dotenv
import datetime
import tweepy
from collections import defaultdict
import seaborn as sns
import matplotlib.pyplot as plt

# get the keys for configurations of the Twitter Developer API
dotenv_path = find_dotenv()
load_dotenv(dotenv_path)
CONSUMER_KEY = os.environ.get("CONSUMER_KEY")
CONSUMER_SECRET = os.environ.get('CONSUMER_SECRET')

def extract_features(**kwargs):

    # read the params from json
    source,outdir,outdir_csv = kwargs['source'], kwargs['outdir'], kwargs['outdirCsv']
    outdirPlot = kwargs['outdirPlot']
    markers = kwargs['markerHashtags']
    popularTweetID, startDate, endDate, maxTweets = kwargs['popularTweetID'], kwargs['startDate'], kwargs['endDate'], kwargs['maxTweets']

    # check if perform on test data
    test = False
    if not os.path.exists(outdir[1]):
        test = True
        source = kwargs['source-test']
    else:
        # check whether the target directory exists
        for f in outdir:
            if not os.path.exists(f):
                os.mkdir(f)

    # set up variables
    hashtags, hashtags_marker = [], []
    data_cnt, marker_cnt = 0, 0
    tweets, tweet_ids, retweet_cnt = [], [], []

    # loop over all the tweet contents
    for i in os.listdir(source):
        if 'tweet-content' in i:
            with open(source+'/'+i, 'r', encoding='utf-8') as f:
                lst = list(f)
                for json_str in lst:
                    result = json.loads(json_str)

                    # save tweets that had been retweeted
                    if 'retweeted_status' not in result.keys():
                        tweet_ids.append(result['id_str'])
                        tweets.append(result['full_text'])
                        retweet_cnt.append(result['retweet_count'])

                    # append tags to list
                    tags = []
                    for tag in result['entities']['hashtags']:
                        tags.append(tag['text'].lower())
                    for m in markers:
                        if m in tags:
                            hashtags_marker+=tags
                            marker_cnt+=1
                            break
                    hashtags+=tags
                    data_cnt+=1


    # save the popular tweets
    df_retweets = pd.DataFrame({'id':tweet_ids, 'tweets': tweets, 'retweet_count':retweet_cnt})
    df_retweets.sort_values(by=['retweet_count'], ascending=False, inplace=True)
    df_retweets.head(100).to_csv(outdir_csv[1], index=False)

      
    hashtag_polarity(hashtags, hashtags_marker, data_cnt, marker_cnt, outdir_csv[0])
    if test:
        users_cons, users_sci = kwargs["cons_users_test"], kwargs["sci_users_test"]
        user_polarity(outdir_csv[0], source, users_cons, users_sci, outdirPlot)
    else:
        users_cons, users_sci = get_users(popularTweetID, startDate, endDate, maxTweets, outdir_csv[2])
        user_polarity(outdir_csv[0], outdir[1], users_cons, users_sci, outdirPlot)

    return


def hashtag_polarity(hashtags, hashtags_marker, data_cnt, marker_cnt, outdir):
    print('start calculating the hashtag polarity...')

    # determine the top 200 hashtags by frequency
    top200 = pd.Series(hashtags).value_counts(ascending=False).head(200)

    # calculate the "baseline rate of occurrence"
    rate_baseline = (top200/data_cnt).sort_index()

    # calculate the "marker rate of occurrence"
    rate_marker = dict.fromkeys(list(top200.index), 0)
    for tag in hashtags_marker:
        if tag in list(top200.index):
            rate_marker[tag] += 1
    rate_marker = (pd.Series(rate_marker) / marker_cnt).sort_index()

    # report the hashtag polarity
    result = (rate_marker - rate_baseline)/rate_baseline
    (result.sort_values(ascending=False)).to_csv(outdir, header=False)

    print('calculation finished! result is saved in {}.'.format(outdir))

    return


def get_users(tweetID, startDate, endDate, maxTweets, outdir):

    print("start downloading users' acitivity...")

    # initialize api
    auth = tweepy.AppAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
    api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)
    
    # find user IDs
    users_cons, users_sci = [], []
    for status in api.retweets(tweetID[0], count=100):
        users_cons.append(str(status.user.id))
    for status in api.retweets(tweetID[1], count=100):
        users_sci.append(str(status.user.id))
    
    # set dates
    startDate = datetime.datetime.strptime(startDate, "%m %d %Y")
    endDate = datetime.datetime.strptime(endDate, "%m %d %Y")

    for userID in users_cons+users_sci:
        if path.exists(outdir.format(userID)):
            continue

        print("downloading {}...".format(userID))
        page, stop_loop, lst = 1, False, []
        # loop over the users' tweets based on page
        while not stop_loop:
            tweets = api.user_timeline(userID, page=page)
            if not tweets:
                break
            for tweet in tweets:
                if (len(lst)) >= maxTweets:
                    stop_loop = True
                    break
                # get the tweets between the date frame
                if (endDate > tweet.created_at) and (startDate <= tweet.created_at):
                    lst.append(tweet)
            page += 1
        
        # save the user data
        if len(lst) > 0:
            data = []
            for i in lst:
                data.append(i._json)
            (pd.DataFrame(data)).to_csv(outdir.format(userID),index=False)

    print("download completed!")

    return [users_cons, users_sci]


def user_polarity(hashtagPolarityPath, source, users_cons, users_sci, outdirPlot):

    print('start calculating user polarity...')

    # read the hashtag polarity
    df_tag = pd.read_csv(hashtagPolarityPath, index_col=0, header=None, squeeze=True)

    # initialize the user polarity dicts
    cons_user_polarity = defaultdict(int)
    sci_user_polarity = defaultdict(int)

    # loop over the users' acitivity
    for i in os.listdir(source):
        if 'user' in i:
            userID = i[5:-4]
            # for test data
            if 'test' in userID:
                userID = userID[:-5]
            # read the hashtags from user
            df = pd.read_csv(source+'/'+i)
            tags = df['entities'].apply(lambda x: [i['text'].lower() for i in eval(x)['hashtags']])
            tags = tags[tags.apply(len) > 0].tolist()
            # calculate the user polarity
            tweet_cnt, polarity = 0,0
            for tweet in tags:
                contained = False
                for tag in tweet:
                    if tag in df_tag.index:
                        polarity += df_tag[tag]
                        contained = True
                if contained:
                    tweet_cnt += 1
            if userID in users_cons:
                if tweet_cnt == 0:
                    cons_user_polarity[userID] = 0
                else:
                    cons_user_polarity[userID] = polarity/tweet_cnt
            else:
                if tweet_cnt == 0:
                    sci_user_polarity[userID] = 0
                else:
                    sci_user_polarity[userID] = polarity/tweet_cnt

    # remove outliers
    cons_user_polarity = remove_outliers(list(cons_user_polarity.values()))
    sci_user_polarity = remove_outliers(list(sci_user_polarity.values()))

    # plotting the histogram
    sns.distplot(cons_user_polarity, kde=False)
    plt.xlabel('User Polarity')
    plt.savefig(outdirPlot[0])
    plt.close()

    sns.distplot(sci_user_polarity, kde=False)
    plt.xlabel('User Polarity')
    plt.savefig(outdirPlot[1])
    plt.close()

    print('calculation completed!')

    return

def remove_outliers(lst):
    q1 = np.quantile(lst, 0.25)
    q3 = np.quantile(lst, 0.75)
    iqr = q3 - q1
    low_bound = q1-1.5*iqr
    up_bound = q3+1.5*iqr
    lst = np.array(lst)
    return lst[(lst >= low_bound) & (lst <= up_bound)]