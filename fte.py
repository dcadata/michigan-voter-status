import pandas as pd
import requests

from messaging import send_email


def _get_gcb() -> None:
    existing_content = open('data/generic_ballot_averages.csv', 'rb').read()
    new_content = requests.get('https://projects.fivethirtyeight.com/polls/data/generic_ballot_averages.csv').content
    if existing_content == new_content:
        return
    open('data/generic_ballot_averages.csv', 'wb').write(new_content)

    data = pd.read_csv('data/generic_ballot_averages.csv', usecols=['candidate', 'pct_estimate', 'election'])
    data = data[data.election == '2022-11-08'].drop(columns=['election'])
    data = data.iloc[-2:]
    data.candidate = data.candidate.apply(lambda x: x[0])
    estimates = data.groupby('candidate').pct_estimate.sum()
    difference = round(estimates['R'] - estimates['D'], 2)
    data.pct_estimate = data.pct_estimate.apply(lambda x: round(x, 2))
    estimates = data.groupby('candidate').pct_estimate.sum()

    gcb_summary = 'D: {D}\nR: {R}\nR+{difference}'.format(difference=difference, **estimates)
    if gcb_summary != open('data/gcb_summary.txt').read():
        send_email('FTE GCB Alert', gcb_summary)
        open('data/gcb_summary.txt', 'w').write(gcb_summary)


if __name__ == '__main__':
    _get_gcb()
