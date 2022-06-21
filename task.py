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
    status = 'Registered: ' + ('Yes' if page.find(text='Yes, you are registered!') else 'No')
    open('status.txt', 'w').write(status)


if __name__ == '__main__':
    main()
