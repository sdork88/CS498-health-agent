from datetime import datetime, timedelta, UTC
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import os

API_PATHS = [
    "https://www.googleapis.com/auth/fitness.activity.read",
    "https://www.googleapis.com/auth/fitness.body.read",
]

def save_results(data_types):
    with open("data/data.txt", "w") as f:
        for item in data_types:
            f.write(str(item) + "\n")

results = []
if os.path.exists("token.json"):
    creds = Credentials.from_authorized_user_file("token.json", API_PATHS)
else:
    flow = InstalledAppFlow.from_client_secrets_file("utils/client_secrets.json", API_PATHS)
    creds = flow.run_local_server(port=0)
    open("token.json", "w").write(creds.to_json())

service = build("fitness", "v1", credentials=creds)

end = int(datetime.now(UTC).timestamp() * 1000)
start = int((datetime.now(UTC)- timedelta(days=7)).timestamp() * 1000)

data_types = [
    "com.google.step_count.delta",
    "com.google.distance.delta",
    "com.google.calories.expended",
    "com.google.weight",
    "com.google.height",
    "com.google.heart_rate.bpm",
    "com.google.activity.segment",
]

for data_type in data_types:
    try:
        response = service.users().dataset().aggregate(
            userId="me",
            body={
                "aggregateBy": [{"dataTypeName": data_type}],
                "startTimeMillis": start,
                "endTimeMillis": end,
            },
        ).execute()

        print(f"\n{data_type}")

        for bucket in response.get("bucket", []):
            for dataset in bucket.get("dataset", []):
                for point in dataset.get("point", []):
                    print(point)
                    results.append(point)
    except:
        pass

save_results(results)