import re
from time import sleep

import requests
from bs4 import BeautifulSoup

from checker import send_email


def _get_soup() -> BeautifulSoup:
    response = requests.get('https://nitter.net/PollTrackerUSA/rss')
    soup = BeautifulSoup(response.text, 'xml')
    return soup


def _get_relevant_tweets(soup: BeautifulSoup, include: list) -> list:
    relevant_tweets = []
    tweets = soup.select('item')
    for tweet in tweets:
        if tweet.find('link').text == open('poll_notifier_last_seen_link.txt').read():
            return []
        title, pubdate = map(lambda x: tweet.find(x).text.strip(), ('title', 'pubDate'))
        if re.search('|'.join(include), title):
            relevant_tweets.append(dict(title=title, pubdate=pubdate))
    open('poll_notifier_last_seen_link.txt', 'w').write(tweets[0].find('link').text)
    return relevant_tweets


def _send_emails(email_bodies: list) -> None:
    length = len(email_bodies)
    for n, body in enumerate(email_bodies):
        send_email(f'Poll Alert ({n + 1}/{length})', body)
        sleep(1)


def main() -> None:
    relevant_tweets = _get_relevant_tweets(_get_soup(), ['#MI'])
    _send_emails(['{title} (PubDate: {pubdate})'.format(**tweet) for tweet in relevant_tweets])


if __name__ == '__main__':
    main()
