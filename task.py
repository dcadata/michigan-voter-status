import json
from os import environ

import requests
from bs4 import BeautifulSoup


def main() -> None:
    first_name, last_name = environ['NAME'].split(None, 1)
    birth_month, birth_year = environ['BIRTH_MONTH_AND_YEAR'].split('/', 1)
    params = dict(
        FirstName=first_name,
        LastName=last_name,
        NameBirthMonth=birth_month,
        NameBirthYear=birth_year,
        ZipCode=environ['ZIP'],
    )
    response = requests.post('https://mvic.sos.state.mi.us/Voter/SearchByName', data=params)

    page = BeautifulSoup(response.text, 'lxml')
    election_dates = page.find_all('td', {'data-label': 'Election Date'})
    ballot_previews = page.find_all('td', {'data-label': lambda x: str(x).strip() == 'Ballot Preview'})
    absentee_voter_info_block = page.find('div', dict(id='lblAbsenteeVoterInformation'))

    status = dict(
        is_registered=bool(page.find(text='Yes, you are registered!')),
        is_ballot_preview_available=dict((date.text, prev.text == 'View') for date, prev in zip(
            election_dates, ballot_previews)),
        on_absentee_voter_list=bool(page.find('p', text=lambda x: str(x).startswith(
            'You are on the permanent absentee voter list.'))),
        not_av_application_received=(
                bool(absentee_voter_info_block.select('p.maroon')) or bool(absentee_voter_info_block.find(
            'p', text=lambda x: str(x).startswith('Your clerk has not recorded receiving your AV Application.')))
        ),
    )
    json.dump(status, open('status.json', 'w'))


if __name__ == '__main__':
    main()
