# check-pending-messages-in-queue
This is a small python script I wrote for a client.
The main reason for this is to be able to get a daily report on a dev-ops slack channel about the status of different queues and the pending messages, so that the ops team can discover quickly if messages are being accumulated in the queues. 

To check pending messages in activeMQ queues the scruot is using activeMQ's REST API called jolokia. To send report to the predetermined slack channel, the script uses slack webhooks API and sends a simple HTTP Get call to the slack API.

In order to use the script you need to make some modifications so that the hardcoded base64 password for activeMQ, the slack webhook API key, and the name of the queues are included.

To run the script it's easiest to put it as an scheduled Cron job, to be executed on the desired internals, like:

0 5 * * * nice -n 10 python /ops/scripts/check-activemq-queue.py >/dev/null 2>&1
