from django.conf import settings

from google.cloud import tasks_v2
from google.protobuf import timestamp_pb2

import datetime
import json


def create_http_task(url, payload=None, method="POST", headers={"Content-Type": "application/json"}, queue=settings.BOOKS_ETL_SERVICE_QUEUE, in_seconds=None, task_name=None):

    # Create a client.
    client = tasks_v2.CloudTasksClient()

    project = settings.PROJECT_ID
    region = settings.REGION

    # Construct the fully qualified queue name.
    parent = client.queue_path(project, region, queue)

    task = {
        'http_request': {  # Specify the type of request.
            'http_method': method,
            'url': url,  # The full url path that the task will be sent to.
            'oidc_token': {
                'service_account_email': settings.SERVICE_ACCOUNT_EMAIL
            },
            'headers': headers
        }
    }

    if payload is not None and method != "GET":
        if isinstance(payload, dict):
            # Convert dict to JSON string
            payload = json.dumps(payload)

        # The API expects a payload of type bytes.
        converted_payload = payload.encode()

        # Add the payload to the request.
        task["http_request"]["body"] = converted_payload

    if in_seconds is not None:
        # Convert "seconds from now" into an rfc3339 datetime string.
        d = datetime.datetime.utcnow() + datetime.timedelta(seconds=in_seconds)

        # Create Timestamp protobuf.
        timestamp = timestamp_pb2.Timestamp()
        timestamp.FromDatetime(d)

        # Add the timestamp to the tasks.
        task["schedule_time"] = timestamp

    if task_name is not None:
        # Add the name to tasks.
        task["name"] = task_name

    # Use the client to build and send the task.
    response = client.create_task(request={"parent": parent, "task": task})

    print("Created task {}".format(response.name))

    # print('Created task {}'.format(response.name))
    return response
