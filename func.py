import io
import json
import logging
import traceback

import oci
from fdk import response
import os
from pytz import timezone
from datetime import datetime


def handler(ctx, data: io.BytesIO = None):
    try:
        logging.getLogger().info("Inside Python function to process Alarm Message")
        body = json.loads(data.getvalue())
        body['title'] = body['title'] + ' Processed Message By Fn Function'

        pacific_tz = timezone('US/Pacific')
        pacific_ts = datetime.now(pacific_tz)
        body['fn_timestamp'] = pacific_ts.strftime('%Y-%m-%dT%H:%M:%S')+"-07:00"

        new_msg = json.dumps(body, indent=2)

        logging.getLogger().info("about to send ONS")
        send_notification(new_msg)
        logging.getLogger().info("sent ONS")

        return response.Response(
            ctx, response_data=json.dumps(
                {"message": "Message Processed {0}".format(body['dedupeKey'])}),
            headers={"Content-Type": "application/json"})
    except (Exception, ValueError) as ex:
        logging.getLogger().info('error parsing json payload: ' + str(ex))
        track = traceback.format_exc()
        logging.getLogger().info('Stacktrace:\n ' + track)
        return response.Response(
            ctx, response_data=json.dumps(
                {"message": "Message Processing failed {0}".format(body['dedupeKey'])}),
            headers={"Content-Type": "application/json"}, status_code=500)


def send_notification(json_msg):
    signer = oci.auth.signers.get_resource_principals_signer()
    logging.getLogger().info("got signer")

    # Initialize service client with default config file
    config = {'region': 'us-sanjose-1'}
    ons_client = oci.ons.NotificationDataPlaneClient(signer=signer, config=config)
    logging.getLogger().info("ons client created")

    # Send the request to service, some parameters are not required, see API
    # doc for more info
    publish_message_response = ons_client.publish_message(
        topic_id=os.environ['ONS_TOPIC_OCID'],
        message_details=oci.ons.models.MessageDetails(
            body=json_msg,
            title="Custom Formatted and/or Processed Alarm Notification by Fn"))

    # Get the data from response
    print(publish_message_response.data)
    return True
