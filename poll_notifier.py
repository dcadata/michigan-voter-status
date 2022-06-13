import re
from time import sleep

import requests
from bs4 import BeautifulSoup

from voter_status_checker import has_changes, send_email


def _get_polls(keywords: list) -> list:
    response = requests.get('https://nitter.net/PollTrackerUSA/rss')
    soup = BeautifulSoup(response.text, 'xml')

    tweets = soup.select('item')
    open('data/poll_notifier.txt', 'w').write(tweets[0].find('link').text)

    if has_changes():
        polls = []
        for tweet in tweets:
            title, pubdate = map(lambda x: tweet.find(x).text.strip(), ('title', 'pubDate'))
            if re.search('|'.join(keywords), title):
                polls.append(dict(title=title, pubdate=pubdate))
        return ['{title} (PubDate: {pubdate})'.format(**i) for i in polls]

    return []


def main() -> None:
    polls = _get_polls(['#MI'])
    length = len(polls)
    for n, body in enumerate(polls):
        send_email(f'Poll Alert ({n + 1}/{length})', body)
        sleep(1)


if __name__ == '__main__':
    main()
