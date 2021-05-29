import os
import praw
from multiprocessing import Pool, cpu_count
from tqdm import tqdm
from functools import partial
import time

_client_id= "__"
_client_secret= "__"
_user_agent= "__"

def scrape_subreddit(subname: str, limit: int, dest_path: str):
    """
    Scrape subreddit, provided subname parameter, and write jpg and png files' urls to txt file created on the go in
    dest_path directory with {subname}.txt name.

    :param subname: subreddit name
    :param limit: upper limit number of images to be scrapped (actual amount will depend on scroll line results)
    :param dest_path: dir to store txt file with urls
    :return: None
    """
    def get_submits(cat: str):
        if cat == 'top':
            for period in ['all', 'year', 'month', 'week', 'day', 'hour']:
                time.sleep(1)
                submissions = getattr(reddit.subreddit(subname), cat)(period, limit=None)
                submits_walker(submissions)
                if count >= limit:
                    break
        else:
            submissions = getattr(reddit.subreddit(subname), cat)(limit=None)
            submits_walker(submissions)
        return url_mem

    def submits_walker(submissions):
        nonlocal count
        try:
            for subm in tqdm(submissions, total=limit, desc=f"{subname}/{cat}:"):
                if count >= limit:
                    break
                if subm.url.endswith('.jpg') or subm.url.endswith('.png'):
                    url_mem.append(subm.url)
                    count += 1
        except AttributeError as e:
            print("{} / subname: {}, cat: {}".format(e, subname, cat))
        return

    reddit = praw.Reddit(
        client_id=_client_id,
        client_secret=_client_secret,
        user_agent=_user_agent,
    )

    count = 0
    url_mem = list()
    for cat in ['top', 'hot', 'new']:
        time.sleep(1)
        get_submits(cat)
        if count >= limit:
            break

    if count < limit:
        print("Got only {} urls besides {} / subname: {}".format(count, limit, subname))

    with open(os.path.join(dest_path, subname + '.txt'), 'w') as f:
        for url in url_mem:
            f.write(url + '\n')
    return


def cat_list_scraper(cat_list: list, limit: int, dest_path: str):
    """
    Scrape provided list of subreddits in multiprocessing pool and creates each {subname}.txt file with urls in
    directory with dest_path.
    
    :param cat_list: list of subreddits
    :param limit: limit number of images per each subreddit equally
    :param dest_path: dir to save .txt files
    :return: None
    """
    pool = Pool(cpu_count())
    for _ in tqdm(pool.imap(partial(scrape_subreddit, limit=limit, dest_path=dest_path), cat_list),
                  total=len(cat_list), desc="All subreddits:"):
        pass
    pool.close()
    pool.join()
    return None


def get_subreddits_set(filepath):
    """
    Helper function to return set of subreddits listed in txt file
    :param filepath: full filepath
    :return: set
    """
    subnames = set()
    with open(filepath, 'r') as f:
        for sub in f.readlines():
            subnames.add(sub.rstrip('\n'))
    return subnames


if __name__ == "__main__":
    from argparse import ArgumentParser
    parser = ArgumentParser()
    parser.add_argument("-i", "--input", dest="subs_fpath", type=str, required=True, help="full path to txt file with listed subreddits (should use '/' delimeter in filepath)")
    parser.add_argument("-l", "--limit", type=int, required=True, help="limit number of images per each subreddit equally")
    parser.add_argument("-o", "--output", dest="output_dir", type=str, help="dir to save txt files with urls (be sure to use '/' delimeter)")
    args = parser.parse_args()

    subreddits = get_subreddits_set(args.subs_fpath)
    if args.output_dir:
        cat_list_scraper(subreddits, limit=args.limit, dest_path=args.output_dir)
    else:
        cat_list_scraper(subreddits, limit=args.limit, dest_path="".join(args.subs_fpath.rpartition("/")[:-1]))
    print("Finished successfully!\n")
