import datetime
import sys
from apiclient import discovery
import httplib2
from oauth2client.service_account import ServiceAccountCredentials
from logging import Logger


class GoogleApi:
    logger: Logger

    # A single auth scope is used for the zero-touch enrollment customer API.
    SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]
    SERVICE_ACCOUNT_KEY_FILE = "service_account_key.json"

    def get_credential(self):
        """Creates a Credential object with the correct OAuth2 authorization.

        Uses the service account key stored in SERVICE_ACCOUNT_KEY_FILE.

        Returns:
          Credentials, the user's credential.
        """
        credential = ServiceAccountCredentials.from_json_keyfile_name(
            self.SERVICE_ACCOUNT_KEY_FILE, self.SCOPES
        )

        if not credential or credential.invalid:
            self.logger.info("Unable to authenticate using service account key.")
            sys.exit()
        return credential

    def get_service(self):
        http_auth = self.get_credential()  # .authorize(httplib2.Http())
        return discovery.build("calendar", "v3", credentials=http_auth)
        # return discovery.build("androiddeviceprovisioning", "v1", http=http_auth)

    def get_events(self):
        # Create a zero-touch enrollment API service endpoint.
        service = self.get_service()

        # Call the Calendar API
        now = datetime.datetime.now(tz=datetime.timezone.utc).isoformat()
        self.logger.info("Getting the upcoming 10 events")
        try:
            events_result = (
                service.events()
                .list(
                    calendarId="hejare.se_jp7m0s7indk7f68rlotj5s9lg0@group.calendar.google.com",
                    timeMin=now,
                    maxResults=10,
                    singleEvents=True,
                    orderBy="startTime",
                )
                .execute()
            )
            events = events_result.get("items", [])

            if not events:
                self.logger.info("No upcoming events found.")
                return []

            # Prints the start and name of the next 10 events
            for event in events:
                start = event["start"].get("dateTime", event["start"].get("date"))
                self.logger.info(start, event["summary"])

            return events
        except Exception as e:
            dir(e)
            self.logger.error(e)
            return []

    def __init__(self, logger: Logger):
        self.logger = logger
