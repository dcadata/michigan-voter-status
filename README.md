# michigan-voter-status


Notifies Michigan voters if their registration status changes.


To set this up for yourself, fork this repo and add repository secrets as follows. Go to [Settings > Secrets > Actions](https://github.com/YOUR_USERNAME/michigan-voter-status/settings/secrets/actions) and add the following repository secrets:

* `NAME`: your legal first and last name, separated by a space - e.g. "Jane Doe"
* `BIRTH_MONTH_AND_YEAR`: the month and year of your birth, separated by a "/" - e.g. "12/1985"
* `ZIP`: the 5-digit zip code corresponding to your address - e.g. "48001"
* `SENDER`: the email address used to send the notification
* `PASSWORD`: the password for `SENDER`
* `RECIPIENT`: the recipient email address to receive the notification
