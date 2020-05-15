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
