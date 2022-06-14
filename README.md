# michigan-voter-status


Notifies specified Michigan voter if their voter registration status changes. Or rather, it assumes you're registered and only notifies you if your status changes to *not*-registered.


To set this up for yourself, fork this repo. Then, go to Settings > Secrets > Actions or (`https://github.com/YOUR_USERNAME/michigan-voter-status/settings/secrets/actions`) and add the following repository secrets:

* `NAME`: your legal first and last name, separated by a space - e.g. "Jane Doe"
* `BIRTH_MONTH_AND_YEAR`: the month and year of your birth, separated by a "/" - e.g. "12/1985"
* `ZIP`: the 5-digit zip code corresponding to your address - e.g. "48001"
* `SENDER`: the gmail address used to send the notification (I would recommend creating a new gmail account)
* `PASSWORD`: the password for `SENDER` (I would recommend using an app-specific password)
* `RECIPIENT`: the recipient email address to receive the notification (any email provider is fine)


`Polls and GCB Notifier` has also been added. If you don't want notifications for polls/GCB, just delete the file `.github/workflows/polls_and_gcb.yml`.
