import os
import seaborn as sns
import numpy as np
import pandas as pd
import json
import matplotlib.pyplot as plt

def analyze_data(**kwargs):
    '''
    main steps for analyzing the twitter data by looping over each tweet content.
    '''
    source, outdir = kwargs['source'], kwargs['outdir']

    # perform analysis on the test data
    test = False
    if not os.path.exists(source):
        source = kwargs['source-test']
        test = True

    # check whether the target directory exists
    if not os.path.exists(outdir):
        os.mkdir(outdir)

    # initialize
    ids,hashtags,dates = [],[],[]

    # loop over saved tweet contents
    for i in os.listdir(source):
        if 'tweet-content' in i:
            with open(source+'/'+i, 'r', encoding='utf-8') as f:
                lst = list(f)
                for json_str in lst:
                    result = json.loads(json_str)
                    # append user id to the list
                    ids.append(result['user']['id'])
                    # append date and hashtags for this tweet to the list
                    for tag in result['entities']['hashtags']:
                        hashtags.append(tag['text'].lower())
                        dates.append(result['created_at'][4:10])

    plot_hashtag(hashtags, dates, kwargs['outdir_csv'], kwargs['outdir_plot'], kwargs['scientific_tags'], kwargs['conspiracy_tags'])
    plot_user_hist(ids, kwargs['outdir_dist'], test)
    print('analysis completed! plots and data saved in `data/report`')
    return
   

def plot_hashtag(hashtags, dates, outdirCsv, outdirPlot, sTags, cTags):
    '''
    get the top-50 list and plot each selected hashtag
    '''
    print('start analyzing for hashtags...')
    df = pd.DataFrame({'hashtag':hashtags, 'date':dates})

    if len(df) >= 50:
        # get the top-50-most-used hashtags in the COVID dataset
        df['hashtag'].value_counts().head(50).to_csv(outdirCsv, header=False)
    else:
        df['hashtag'].value_counts().to_csv(outdirCsv, header=False)

    # draw the frequency bar plot for each selected hashtag
    for t in sTags+cTags:
        draw_num_hashtags_keywords_by_date(df, t, outdirPlot)
    return


def draw_num_hashtags_keywords_by_date(df, word, outdirPlot):
    '''
    function for drawing the barplot for a specific hashtag
    '''
    # get the number of counts for each hashtag
    df = df[df['hashtag']==word]
    count = df['date'].value_counts().sort_index()
    x, y = list(count.index), list(count.values)
    # plot the occurences
    plt.plot(x,y)
    plt.suptitle('Occurrences of Hashtag "{}" over Dates'.format(word))
    plt.xticks(rotation='50')
    plt.xlabel('date')
    plt.savefig(outdirPlot+'_{}.png'.format(word),dpi=150)
    plt.close()
    return


def plot_user_hist(ids, filename, test):
    '''
    draw the density plot for number of posts per user
    '''
    print('start analyzing for users...')
    # get a list for number of posts per user
    counts = pd.Series(ids).value_counts()

    # plot the distribution
    if not test:
        # filter out those only posted once
        counts = (counts[counts>1]).to_numpy()
        ax = sns.distplot(counts, hist=True)
    else :
        ax = sns.distplot(counts, kde=False)
    ax.set(xlabel='number of posts per user', ylabel='density')
    plt.suptitle('Distribution of Number of Posts per User')
    ax.figure.savefig(filename, dpi=150)
    plt.close()
    return