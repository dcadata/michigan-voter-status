from os import environ

import requests
from bs4 import BeautifulSoup


def get_voter_status(**params) -> None:
    response = requests.post('https://mvic.sos.state.mi.us/Voter/SearchByName', data=params)
    page = BeautifulSoup(response.text, 'lxml')
    status = 'Registered: ' + ('Yes' if page.find(text='Yes, you are registered!') else 'No')
    open('status.txt', 'w').write(status)


def main() -> None:
    first_name, last_name = environ['NAME'].split(None, 1)
    birth_month, birth_year = environ['BIRTH_MONTH_AND_YEAR'].split('/', 1)
    get_voter_status(
        FirstName=first_name,
        LastName=last_name,
        NameBirthMonth=birth_month,
        NameBirthYear=birth_year,
        ZipCode=environ['ZIP'],
    )


if __name__ == '__main__':
    main()
