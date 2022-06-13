import re

import requests
from bs4 import BeautifulSoup

from voter_status import send_email


def _get_polls(pattern: str) -> list:
    previous_latest_link = open('data/polls.txt').read()
    response = requests.get('https://nitter.net/PollTrackerUSA/rss')
    soup = BeautifulSoup(response.text, 'xml')
    tweets = soup.select('item')

    polls = []
    for tweet in tweets:
        if tweet.find('link').text == previous_latest_link:
            open('data/polls.txt', 'w').write(tweets[0].find('link').text)
            return polls
        title, pubdate = map(lambda x: tweet.find(x).text.strip(), ('title', 'pubDate'))
        if re.search(pattern, title):
            polls.append(dict(title=title, pubdate=pubdate))

    open('data/poll_notifier.txt', 'w').write(tweets[0].find('link').text)
    return polls


def main() -> None:
    if polls := _get_polls('#MI'):
        send_email('Poll Alert', '\n\n___\n\n'.join('{title} (PubDate: {pubdate})'.format(**poll) for poll in polls))


if __name__ == '__main__':
    main()
