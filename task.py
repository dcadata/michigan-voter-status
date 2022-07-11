import json
from itertools import zip_longest
from os import environ

import requests
from bs4 import BeautifulSoup


def _read_voter_info() -> dict:
    first_name, last_name = environ['NAME'].split(None, 1)
    birth_month, birth_year = environ['BIRTH_MONTH_AND_YEAR'].split('/', 1)
    voter_info = dict(
        FirstName=first_name,
        LastName=last_name,
        NameBirthMonth=birth_month,
        NameBirthYear=birth_year,
        ZipCode=environ['ZIP'],
    )
    return voter_info


def _get_voter_status(**voter_info) -> None:
    response = requests.post('https://mvic.sos.state.mi.us/Voter/SearchByName', data=voter_info)
    page = BeautifulSoup(response.text, 'lxml')

    status = dict(
        is_registered=bool(page.find(text='Yes, you are registered!')),
        absentee_voter_info=dict(application_received=None),
        upcoming_elections=[],
    )

    upcoming_election_dates = page.find_all('td', {'data-label': 'Election Date'})
    upcoming_election_descriptions = page.find_all('td', {'data-label': lambda x: str(x).strip() == 'Description'})
    ballot_previews = page.find_all('td', {'data-label': lambda x: str(x).strip() == 'Ballot Preview'})
    absentee_voter_info_block = page.find('div', dict(id='lblAbsenteeVoterInformation'))

    av_application_not_received = bool(absentee_voter_info_block.find(text=lambda x: str(x).startswith(
        'Your clerk has not recorded receiving your AV Application.')))
    if not av_application_not_received:
        bolded = absentee_voter_info_block.find_all('b')
        for i in bolded:
            i.extract()
        nonbolded = absentee_voter_info_block.get_text(separator='\n', strip=True).splitlines()
        status['absentee_voter_info'].update(dict(
            zip_longest([i.text.replace(' ', '_').lower() for i in bolded], nonbolded)))

    status['absentee_voter_info']['on_permanent_list'] = bool(page.find('p', text=lambda x: str(x).startswith(
        'You are on the permanent absentee voter list.')))

    status['upcoming_elections'].extend([
        dict(date=date.text, description=desc.text, ballot_preview_available=prev.text == 'View')
        for date, desc, prev in zip(upcoming_election_dates, upcoming_election_descriptions, ballot_previews)
    ])

    json.dump(status, open('status.json', 'w'), indent=2)


if __name__ == '__main__':
    _get_voter_status(**_read_voter_info())
