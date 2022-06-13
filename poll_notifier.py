import re
from time import sleep

import pandas as pd
import requests
from bs4 import BeautifulSoup

from voter_status_checker import send_email


def _get_polls(keywords: list) -> list:
    response = requests.get('https://nitter.net/PollTrackerUSA/rss')
    soup = BeautifulSoup(response.text, 'xml')

    polls = []
    tweets = soup.select('item')
    previous_link = open('data/poll_notifier.txt').read()
    for tweet in tweets:
        if tweet.find('link').text == previous_link:
            return []
        title, pubdate = map(lambda x: tweet.find(x).text.strip(), ('title', 'pubDate'))
        if re.search('|'.join(keywords), title):
            polls.append(dict(title=title, pubdate=pubdate))

    open('data/poll_notifier.txt', 'w').write(tweets[0].find('link').text)

    return ['{title} (PubDate: {pubdate})'.format(**i) for i in polls]


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

    if output == open('data/fte_gcb.txt').read():
        return ''
    open('data/fte_gcb.txt', 'w').write(output)
    return output


def main() -> None:
    if poll_bodies := _get_polls(['#MI']):
        length = len(poll_bodies)
        for n, body in enumerate(poll_bodies):
            send_email(f'Poll Alert ({n + 1}/{length})', body)
            sleep(1)

    if fte_gcb := _get_fte_gcb():
        send_email('FTE GCB Alert', fte_gcb)


if __name__ == '__main__':
    main()
