from os import environ

import requests
from bs4 import BeautifulSoup

import mailer


class MIVoterRegistrationChecker:
    def __init__(self, **kwargs):
        self._params = kwargs.copy()
        self._soup = None

    def make_request(self):
        r = requests.post('https://mvic.sos.state.mi.us/Voter/SearchByName', data=self._params)
        self._soup = BeautifulSoup(r.text, 'lxml')

    def get_messages(self) -> str:
        messages = []
        if not self._is_registered:
            messages.append(self._is_registered_text)
        if messages or self._ballot_preview_available:
            messages.append(self._calendar_details)
        return '\n'.join(messages)

    @property
    def _is_registered(self) -> bool:
        return bool(self._soup.find(text='Yes, you are registered!'))

    @property
    def _is_registered_text(self) -> str:
        return 'Registered: ' + ('Yes' if self._is_registered else 'No')

    @property
    def _ballot_preview_available(self) -> int:
        return len(self._soup.find_all(text='Not Available')) < 2

    @property
    def _calendar_details(self) -> str:
        calendar = self._soup.find('div', dict(id='lblElectionCalendar'))
        _get_text = lambda label: calendar.find_all('td', {'data-label': lambda x: x.endswith(label)})
        dates = [i.text for i in _get_text('Election Date')]
        descriptions = [i.text for i in _get_text('Description')]
        ballot_previews = [f'Ballot Preview: {i.text}' for i in _get_text('Ballot Preview')]
        restructured = list(zip(dates, descriptions, ballot_previews))
        return '\n'.join(' - '.join(i) for i in restructured)


def main():
    first_name, last_name = environ['NAME'].split(None, 1)
    birth_month, birth_year = environ['BIRTH_MONTH_AND_YEAR'].split('/', 1)
    checker = MIVoterRegistrationChecker(
        FirstName=first_name,
        LastName=last_name,
        NameBirthMonth=birth_month,
        NameBirthYear=birth_year,
        ZipCode=environ['ZIP'],
    )
    checker.make_request()
    if body := checker.get_messages():
        mailer.send_email('Voter Status Update', body)


if __name__ == '__main__':
    main()
