Reddit images scrapper
======================

**Before usage** make sure to paste your credentials in `reddit_scrapper.py` file, as here:
```
_client_id= "__"
_client_secret= "__"
_user_agent= "__"
```

To check if subreddits to be scraped are still existing use this simple function:
```
def filter_subreddits(filepath:str):
    '''
    Check subreddits in file if they're existing and 
    sending any responses
    
    filepath: path to *.txt file with subreddits
    
    return: cleaned set of existing subreddits
    
    '''
    reddit = praw.Reddit(
        client_id= _client_id,
        client_secret= _client_secret,
        user_agent= _user_agent,
    )
    cleaned_set = set()
    with open(filepath, 'r') as f:
        count = 0
        for line in f.readlines():
            subname = line.rstrip('\n')
            try:
                submissions = reddit.subreddit(subname).top(limit = 3)
                next(submissions)
                cleaned_set.add(subname)
            except Exception as e:
                count += 1
                print("{} / sub: {}".format(e, subname))
        print ('Corrupted: ', count)
    return cleaned_set
```

Example of usage:
-----------------
1. Scrape urls of images with this command, where test_subs.txt - file with listed subreddits you want to scrape:
`python3 Reddit_scrapper.py -i ./Temp_files/test_subs.txt -l 1100 -o ./Temp_files/`
2. Download urls from every {subbreddit_name}.txt file being produced:
`python3 downloader.py -d /home/sandbox/Temp_files/ -uh 1920 -uw 1364`
