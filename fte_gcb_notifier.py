import os

import pandas as pd
import requests

from voter_status_checker import send_email


def _download_fte_gcb() -> None:
    response = requests.get('https://projects.fivethirtyeight.com/polls/data/generic_ballot_averages.csv')
    open('data/generic_ballot_averages.csv', 'wb').write(response.content)


def _format_fte_gcb() -> str:
    data = pd.read_csv('data/generic_ballot_averages.csv', usecols=['candidate', 'pct_estimate', 'election'])
    data = data[data.election == '2022-11-08'].drop(columns=['election'])
    data = data.iloc[-2:]
    data.candidate = data.candidate.apply(lambda x: x[0])
    data.pct_estimate = data.pct_estimate.apply(lambda x: round(x, 1))
    estimates = data.groupby('candidate').pct_estimate.sum()
    output = 'D: {D}\nR: {R}\n{difference}'.format(difference='R+{}'.format(
        round(estimates['R'] - estimates['D'], 1)), **estimates)
    return output


def _send_fte_gcb() -> None:
    _download_fte_gcb()
    if os.popen('git status').read().splitlines()[-1] != 'nothing to commit, working tree clean':
        send_email('FTE GCB Alert', _format_fte_gcb())


if __name__ == '__main__':
    _send_fte_gcb()
