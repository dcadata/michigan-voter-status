import re
from time import sleep

import pandas as pd
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


def _get_fte_gcb() -> str:
    data = pd.read_csv('https://projects.fivethirtyeight.com/polls/data/generic_ballot_averages.csv', usecols=[
        'candidate', 'pct_estimate', 'election'])
    data = data[data.election == '2022-11-08'].drop(columns=['election'])
    data = data.iloc[-2:]
    data.candidate = data.candidate.apply(lambda x: x[0])
    data.pct_estimate = data.pct_estimate.apply(lambda x: round(x, 1))
    estimates = data.groupby('candidate').pct_estimate.sum()
    difference = 'R+{}'.format(round(estimates['R'] - estimates['D'], 1))
    output = 'D: {D}\nR: {R}\n{difference}'.format(difference=difference, **estimates)

    if output == open('fte_gcb.txt').read():
        return ''
    open('fte_gcb.txt', 'w').write(output)
    return output


def main() -> None:
    if fte_gcb := _get_fte_gcb():
        send_email('FTE GCB Alert', fte_gcb)
    relevant_tweets = _get_relevant_tweets(_get_soup(), ['#MI'])
    _send_emails(['{title} (PubDate: {pubdate})'.format(**tweet) for tweet in relevant_tweets])


if __name__ == '__main__':
    main()
