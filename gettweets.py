import time
import argparse
import tweepy
import smtplib
from yattag import Doc

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)

api = tweepy.API(auth)

def handleLimit(cursor):
    while True:
        try:
            yield cursor.next()
        except tweepy.RateLimitError:
            time.sleep(15 * 60)
        except StopIteration:
            break

if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument('--searchfor', required=True, help='What pattern: hashtag or text to search for in latest tweets')
    parser.add_argument('--number', type = int, default = 10, help='How many tweets to output')
    parser.add_argument('--limit', type = int, default = 100, help='How many tweets to search from')
    parser.add_argument('--filter_retweets', type = bool, default= True, help= 'To include Retweeted tweets or not')
    parser.add_argument('--genHTML', type = bool, default= False, help= 'Generates a HTML file if true else prints tweets on console')

    args = parser.parse_args()

    query = args.searchfor
    num_tweets = args.number
    limit = args.limit
    filter = args.filter_retweets
    genHTML = args.genHTML

    if filter:
        q = query + ' -filter:retweets'
    else:
        q = query

    if genHTML:
        doc, tag, text = Doc().tagtext()
        doc.asis('<!DOCTYPE html>')
        with tag('html'):
            with tag('body'):
                text(f'Results for {query}')
                with tag('div'):
                    for i, tweet in enumerate(handleLimit(tweepy.Cursor(api.search, q=q, rpp=limit).items(num_tweets))):
                        with tag('div'):
                            with tag('p'):
                                text(f'{i} ---> {tweet.user.name.encode("utf-8")} : {tweet.text.encode("utf-8")}')
                                for url in tweet.entities['urls']:
                                    with tag('p'):
                                        text(f'     URL : {url["expanded_url"]}')
        content = doc.getvalue()
        with open('Outputs.html', 'w') as file:
            file.write(content)

    else:
        for tweet in handleLimit(tweepy.Cursor(api.search, q=q, rpp=limit).items(num_tweets)):
            print(tweet.user.name)
            print(tweet.text)
            for url in tweet.entities['urls']:
                 print(url['expanded_url'])
