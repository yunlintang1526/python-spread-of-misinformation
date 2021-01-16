from dotenv import load_dotenv, find_dotenv
import sys
import os
from os import path
import urllib.request
import pandas as pd
import numpy as np
import gzip
from twarc import Twarc
import json

# get the keys for configurations of the Twitter Developer API
dotenv_path = find_dotenv()
load_dotenv(dotenv_path)
CONSUMER_KEY = os.environ.get("CONSUMER_KEY")
CONSUMER_SECRET = os.environ.get('CONSUMER_SECRET')
ACCESS_TOKEN = os.environ.get('ACCESS_TOKEN')
ACCESS_TOKEN_SECRET = os.environ.get('ACCESS_TOKEN_SECRET')

def get_data(**kwargs):
    '''
    main steps to get the twitter COVID data.
    '''

    if kwargs['test']:
        print("testing on the test data...")
        return

    # initialize params to dowanload data from 03-22(inclusive) to 08-01(exclusive)
    year = kwargs['years'][0]
    months, days = kwargs['months'], kwargs['days']
    dates = []

    # compute a list of valid dates
    for m in months:
        for d in days:
            if m == 3 and d < 22:
                continue
            elif (m == 4 or m == 6) and d == 31:
                continue
            else:
                if d < 10:
                    d = '0{}'.format(d)
                dates.append('{}-0{}-{}'.format(year,m,d))

    download_tweets(kwargs['outpath'][0], kwargs['source'], dates)
    save_tweet_ids(kwargs['outpath'][1], kwargs['outpath'][0])
    hydrate_tweet(kwargs['outpath'][1], kwargs['outpath'][1])
    return



def download_tweets(outpath, source, dates):
    '''
    download tweet data from GitHub.
    '''
    print('start downloading raw data...')

    if not path.exists(outpath):
        os.mkdir(outpath)

    for d in dates:
        # data souce url
        url = source + '{}/{}-dataset.tsv.gz'.format(d, d)

        # path to save data
        filename = '{}/{}.tsv.gz'.format(outpath, d)
        if not path.exists(filename):
            urllib.request.urlretrieve(url, filename=filename)

    print('download completed!')
    return 



def save_tweet_ids(outpath, source):
    '''
    Exteact ids for each tweet by using downloaded GitHub data.
    '''
    print("start extracting tweet ids...")

    if not path.exists(outpath):
        os.mkdir(outpath)

    # loop over the downloaded tweets saved in `data/raw`
    for f in os.listdir(source):
        # extract the date for that file
        date = f[:10]
        # initialize the name of txt file
        filename = outpath + '/' + 'tweet-ids-{}.txt'.format(date)

        if not path.exists(filename):
            with gzip.open(source + "/" + f) as data:
                df = pd.read_csv(data, sep='\t')
            # extract the tweet ids for this data file
            ids = df['tweet_id'].to_numpy()
            # subsample 1/360 from these ids
            size = int(len(ids) / 360)
            ids = np.random.choice(ids,size=size,replace=False)

            # save the ids to a txt file in `data/interim`
            with open(filename, 'w') as data:
                for i in ids:
                    data.write("%s\n" % i)

    print("extraction completed!")
    return 


def hydrate_tweet(outpath, source):
    '''
    rehydrate the tweet ids from saved txt files.
    '''
    # initialize the twitter api
    t = Twarc(CONSUMER_KEY, CONSUMER_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET)

    print("start rehydrating tweets...")

    # loop over saved tweet-ids files
    for f in os.listdir(source):
        if 'tweet-ids' in f:
            # get the names for source and the output files
            source_file = source + '/' + f
            date = f[10:20]
            output_file = outpath + '/tweet-content-{}.jsonl'.format(date)

            if not path.exists(output_file):
                # write the rehydrated contents to output file
                with open(output_file, 'w', encoding='utf-8') as data:
                    for tweet in t.hydrate(open(source_file)):
                        data.write(json.dumps(tweet)+'\n')

    print("rehydration completed!")
    return