import json

from oauth2client import client
from oauth2client.client import GoogleCredentials

from django.core.management.base import BaseCommand, CommandError

from universities.models import University
from videoproviders.models import YoutubeAuth


class Command(BaseCommand):
    args = '<org> <client-secret-path>'
    help = 'Fetch Youtube access tokens'

    def handle(self, *args, **options):
        if len(args) < 2:
            raise CommandError("Not enough arguments")
        org = args[0]
        client_secret_path = args[1]

        # Fail early if the university does not exist
        university = University.objects.get(code=org)

        # is the file a client-secret file or a credentials file?
        with open(client_secret_path) as f:
            json_data = f.read()
            file_data = json.loads(json_data)
            if "scopes" in file_data:
                self.stdout.write("Importing access token...")
                credentials = GoogleCredentials.from_json(json_data)
            else:
                self.stdout.write("Start flow from client secrets...")
                credentials = flow_from_client_secrets(client_secret_path)

        # Save credentials to database
        YoutubeAuth.objects.create(
            university=university,
            client_id=credentials.client_id,
            client_secret=credentials.client_secret,
            access_token=credentials.access_token,
            refresh_token=credentials.refresh_token,
            token_expiry=credentials.token_expiry,
        )
        self.stdout.write("Youtube auth token created")

def flow_from_client_secrets(client_secret_path):
    youtube_scopes = [
        "https://www.googleapis.com/auth/youtube",
        "https://www.googleapis.com/auth/youtube.force-ssl",
        "https://www.googleapis.com/auth/youtubepartner"
    ]

    flow = client.flow_from_clientsecrets(
        client_secret_path,
        scope=" ".join(youtube_scopes),
        redirect_uri='urn:ietf:wg:oauth:2.0:oob'
    )

    # Open webbrowser and ask to authenticate
    auth_uri = flow.step1_get_authorize_url()
    print "Auth url: ", auth_uri

    # Fetch auth code that was produced
    auth_code = raw_input("Open the url above in a browser and paste here here the obtained auth code: ")
    credentials = flow.step2_exchange(auth_code)

    return credentials

