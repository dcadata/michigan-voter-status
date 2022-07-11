import json
import os
from itertools import zip_longest

import requests
from bs4 import BeautifulSoup


def _read_voter_info(voter_info) -> dict:
    first_name, last_name = voter_info['NAME'].split(None, 1)
    birth_month, birth_year = voter_info['BIRTH_MONTH_AND_YEAR'].split('/', 1)
    voter_info = dict(
        FirstName=first_name,
        LastName=last_name,
        NameBirthMonth=birth_month,
        NameBirthYear=birth_year,
        ZipCode=voter_info['ZIP'],
    )
    return voter_info


class VoterStatusGetter:
    def __init__(self, voter_params: dict = None, save_status: bool = None):
        self._voter_params = voter_params
        self._save_status = save_status
        self._page = None
        self.status = {}

    def get_voter_status(self) -> None:
        self._get_page()
        self._get_status()

    def _get_page(self) -> None:
        response = requests.post('https://mvic.sos.state.mi.us/Voter/SearchByName', data=self._voter_params)
        self._page = BeautifulSoup(response.text, 'lxml')

    def _get_status(self) -> None:
        self.status.update(is_registered=self._is_registered)
        if self.status['is_registered']:
            self.status.update(
                absentee_voter_info=self._absentee_voter_info,
                upcoming_elections=self._upcoming_elections,
            )
        if self._save_status:
            json.dump(self.status, open('status.json', 'w'), indent=2)

    @property
    def _is_registered(self) -> bool:
        return bool(self._page.find(text='Yes, you are registered!'))

    @property
    def _absentee_voter_info(self) -> dict:
        absentee_voter_info = {}
        absentee_voter_info_block = self._page.find('div', dict(id='lblAbsenteeVoterInformation'))
        av_application_not_received = bool(absentee_voter_info_block.find(text=lambda x: str(x).startswith(
            'Your clerk has not recorded receiving your AV Application.')))

        if not av_application_not_received:
            bolded = absentee_voter_info_block.find_all('b')
            for i in bolded:
                i.extract()
            nonbolded = absentee_voter_info_block.get_text(separator='\n', strip=True).splitlines()
            absentee_voter_info.update(dict(zip_longest([i.text.replace(' ', '_').lower() for i in bolded], nonbolded)))

        absentee_voter_info.update(on_permanent_list=self._on_permanent_list)
        return absentee_voter_info

    @property
    def _on_permanent_list(self) -> bool:
        return bool(self._page.find('p', text=lambda x: str(x).startswith(
            'You are on the permanent absentee voter list.')))

    @property
    def _upcoming_elections(self) -> list:
        return [
            dict(date=dt.text, description=desc.text, ballot_preview_available=bal.text == 'View') for dt, desc, bal in
            zip(self._upcoming_election_dates, self._upcoming_election_descriptions, self._ballot_previews)
        ]

    @property
    def _upcoming_election_dates(self) -> list:
        return self._page.find_all('td', {'data-label': 'Election Date'})

    @property
    def _upcoming_election_descriptions(self) -> list:
        return self._page.find_all('td', {'data-label': lambda x: str(x).strip() == 'Description'})

    @property
    def _ballot_previews(self) -> list:
        return self._page.find_all('td', {'data-label': lambda x: str(x).strip() == 'Ballot Preview'})


if __name__ == '__main__':
    VoterStatusGetter(_read_voter_info(os.environ)).get_voter_status()
