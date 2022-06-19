from os import environ

import requests
from bs4 import BeautifulSoup

from messaging import send_email


class MIVoterRegistrationChecker:
    def __init__(self, **kwargs):
        self._params = kwargs.copy()
        self.subject = ''
        self.body = ''

    def check(self) -> None:
        self._make_request()
        self._get_subject_and_body()

    def _make_request(self) -> None:
        r = requests.post('https://mvic.sos.state.mi.us/Voter/SearchByName', data=self._params)
        self._soup = BeautifulSoup(r.text, 'lxml')

    def _get_subject_and_body(self) -> None:
        if not self._is_registered:
            self.subject = self._is_registered_text
        if self.subject or self._ballot_preview_available:
            self.body = self._calendar_details

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
        _find_all_endswith = lambda label: calendar.find_all('td', {'data-label': lambda x: x.endswith(label)})
        dates = [i.text for i in _find_all_endswith('Election Date')]
        descriptions = [i.text for i in _find_all_endswith('Description')]
        ballot_previews = [f'Ballot Preview: {i.text}' for i in _find_all_endswith('Ballot Preview')]
        restructured = list(zip(dates, descriptions, ballot_previews))
        return '\n'.join(' - '.join(i) for i in restructured)


def main() -> None:
    first_name, last_name = environ['NAME'].split(None, 1)
    birth_month, birth_year = environ['BIRTH_MONTH_AND_YEAR'].split('/', 1)
    checker = MIVoterRegistrationChecker(
        FirstName=first_name,
        LastName=last_name,
        NameBirthMonth=birth_month,
        NameBirthYear=birth_year,
        ZipCode=environ['ZIP'],
    )
    checker.check()
    if checker.subject:
        send_email(checker.subject, checker.body)


if __name__ == '__main__':
    main()
