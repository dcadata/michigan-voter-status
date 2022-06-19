# michigan-voter-status

Uses GitHub's own "email on push" to notify specified Michigan voter of registration status changes

To set this up for yourself, fork this repo. Then, go to Settings > Secrets > Actions (`https://github.com/YOUR_USERNAME/michigan-voter-status/settings/secrets/actions`) and add the following repository secrets:

* `NAME`: your legal first and last name, separated by a space - e.g. "Jane Doe"
* `BIRTH_MONTH_AND_YEAR`: the month and year of your birth, separated by a "/" - e.g. "12/1985"
* `ZIP`: the 5-digit zip code corresponding to your address - e.g. "48001"

Then, go to Settings > Notifications (`https://github.com/YOUR_USERNAME/michigan-voter-status/settings/notifications/edit`) and add your email address and (optionally) approved header.
