#!/usr/bin/env python
import praw
import configparser
import datetime
import traceback
import os
import re
from collections import deque
from os.path import sys 
from time import sleep

SLEEP_TIME      = 30
CACHE_SIZE      = 10

def main():
    print('reallygoodbot v1.0 by /u/thetrny')
    
    #Check for config file
    if not os.path.exists('config.cfg'):
        print('No config file.')
        sys.exit()

    #Fetch config settings
    config = configparser.ConfigParser()
    config.read('config.cfg')
    USERNAME  = config.get('Configuration', 'Username')
    PASSWORD  = config.get('Configuration', 'Password')
    USERAGENT = config.get('Configuration', 'Useragent')
    SUBREDDITS = config.get('Configuration', 'Subreddit').split(',')

    #login to reddit
    r = praw.Reddit(USERAGENT)
    r.login(USERNAME,PASSWORD)

    thing_limit = int(input("Number of comments to look back: "))
    user_name = "reallygoodbot"
    user = r.get_redditor(user_name)
    gen = user.get_comments(limit=thing_limit)
    karma_by_subreddit = {}
    for thing in gen:
        subreddit = thing.subreddit.display_name
        karma_by_subreddit[subreddit] = (karma_by_subreddit.get(subreddit, 0)
                                         + thing.score)
    import pprint
    pprint.pprint(karma_by_subreddit)

    cache = deque(maxlen=CACHE_SIZE) # double-ended queue
    already_done = set()

    #Setup subreddits
    if str(SUBREDDITS[0]) != 'all':
        combined_subs = ('%s') % '+'.join(SUBREDDITS)
        print('Looking at the following subreddits: "' + combined_subs + '".')
    else:
        comments = praw.helpers.comment_stream(r, 'all', limit=None)
        print('Looking at /r/all.')

    running = True
    while running:    
        try:
            if str(SUBREDDITS[0]) != 'all':
                subs = r.get_subreddit(combined_subs)
                comments = subs.get_comments(limit=None)

            #Check comments 
            for c in comments:
                
                #Did we recently check it? If so fetch new comments
                if c.id in cache:
                    break
                
                #Add this to our cache
                cache.append(c.id)
                
                #Check if we need to reply
                if check_comment(c):
                    
                    #Check if we already replied
                    for reply in c.replies:
                        if reply.author.name == USERNAME:
                            already_done.add(c.id)
                    
                    if c.id not in already_done:
                        text = "Wow, that's a really good bot. \n\n"
                        text = add_signature(text)
                        replyto(c, text, already_done)

        except KeyboardInterrupt:
            running = False
        except Exception as e:
            now = datetime.datetime.now()
            print (now.strftime("%m-%d-%Y %H:%M"))
            print (traceback.format_exc())
            print ('ERROR:', e)
            print ('Going to sleep for 30 seconds...\n')
            sleep(SLEEP_TIME)
            continue

#checks a comment for bot, needs to more robust in detection
def check_comment(text):
    author = str(text.author) 
    if 'reallygoodbot' in author:
        return False
    if 'havoc_bot' in author:
        return False
    if 'raddit_bot' in author:
        return False
    elif 'bot' in author:
        return True
    return False

def add_signature(text):
    text += "PM for Feedback | [Source Code](https://github.com/tsitu/reallygoodbot) | *I am a bot.*"
    return text

#replies to given comment
def replyto(c, text, done):
    now = datetime.datetime.now()
    print ((len(done) + 1), 'ID:', c.id, 'Author:', c.author.name, 'r/' + str(c.subreddit.display_name), 'Title:', c.submission.title)
    print (now.strftime("%m-%d-%Y %H:%M"), '\n')
    c.reply(text)
    print (text)
    done.add(c.id)
    
#call main function
main()