# ObituariesNotifier
A Python script deployed on Google Cloud Platform as a Cloud Function, using Cloud Scheduler to run daily. Parses local webpage obituaries with BeautifulSoup and checks for matches against a user-defined list. Matches are logged in Google Sheets and texted to the user with Twilio.

# Requirements
1) Deploy the script as a Google Cloud Function with a topic 'topic-trigger-for-obituaries'
2) To schedule the script to run at 11am daily, create a scheduler job 'obituaries-pubsub'
which writes to the topic at the interval specified. The Cloud Function is subscribed to the topic. Once a message is sent to the topic from the scheduler, the Cloud Function runs.

![0](https://user-images.githubusercontent.com/65370643/82011326-e94e2d00-9631-11ea-9714-6db886bdde26.jpeg)

**1) Deploy script to a Cloud Function:**

```gcloud functions deploy obituaries-notifier --entry-point main --runtime=python37 --trigger-resource topic-trigger-for-obituaries --trigger-event google.pubsub.topic.publish```

**2) Deploy Google Cloud Scheduler to publish messages to the topic at the interval specified by a Cron time string (e.g. '0 11 \* \* \*' runs daily at 11am):**

```gcloud scheduler jobs create pubsub obituaries-pubsub --schedule "0 11 * * *" --topic topic-trigger-for-obituaries --message-body "This runs at 11am daily"```

[Read more in the Google Cloud Python Quickstart to deploy an app from scratch.](https://cloud.google.com/appengine/docs/standard/python3/quickstart)

# Result
Sheet1 showing how matched names are logged
![Screen Shot 2020-05-14 at 10 42 00 PM](https://user-images.githubusercontent.com/65370643/82012193-6f6b7300-9634-11ea-8a05-e0edbc241401.png)

Sheet2 showing the list of user-defined names to search.
`* NAME` format searches all last name matches,
`FIRST LAST` format searches full exact name match
![Screen Shot 2020-05-14 at 10 42 58 PM](https://user-images.githubusercontent.com/65370643/82012192-6ed2dc80-9634-11ea-88dd-53ffd9b6295c.png)
