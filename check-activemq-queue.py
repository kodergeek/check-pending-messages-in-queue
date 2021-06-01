fom base64 import b64encode
import json
import requests
from datetime import datetime

httpmethod = "GET"
url_to_fetch_total_count = "http://10.2.2.2:8161/api/jolokia/read/org.apache.activemq:type=Broker,brokerName=localhost/TotalMessageCount"
base_url = "http://10.2.2.2:8161/api/jolokia/read/org.apache.activemq:type=Broker,destinationType=Queue,destinationName="
slack_webhook_url = 'https://hooks.slack.com/services/YOUR_API_KEY_HERE'

queueArray = [
"de-info",
"pub-out",
"vh.store.fail",
"vh-store",
"ActiveMQ.DLQ",
"auto-count"]


headers = {
  'Authorization': 'Basic ..ActiceMQ pass in base64...=='
}
payload = {}
output = list()
now = datetime.now()
dt_string = now.strftime("%Y-%m-%d %H:%M")

output.append(str('Status report for ActiveMQ queues (prod) currently having pending messages. ' + str(dt_string) + ' \n\n'))
output.append(str('Pending#  Queue name \n'))
output.append(str('-------   ---------- \n'))


#function to call REST resource for each queue
def call_ActiveMQ_REST(url, destinationQueue):
  
    output = ''

    # Create an HTTP Connection
    response = requests.request("GET", url, headers=headers, data = payload)

    resourceFetched = response.text.encode('utf8')
    #load the object in json format
    data = json.loads(resourceFetched)
    jsonFormatted = json.dumps(data, indent=4, sort_keys=True)

    if data['value'] > 0:
        output =  str(data['value']) + str('\t      ') +  destinationQueue + '\n'

    return output  
#function to send notification to Slack channel
def send_notification_to_Slack(payload):
    #send to slack using proxy config
    http_proxy  = "webfilter.url-here-if-needed"
    https_proxy = "webfilter.url-here-if-needed"
    ftp_proxy   = ""

    proxyDict = { 
                "http"  : http_proxy, 
                "https" : https_proxy, 
                "ftp"   : ftp_proxy
                }

    slack_data = {'text': ''.join(payload)}
    response = requests.post(
        slack_webhook_url, json = slack_data,
        headers={'Content-Type': 'application/json'},
        proxies=proxyDict
    )
    if response.status_code != 200:
        raise ValueError(
            'Request to slack returned an error %s, the response is:\n%s'
            % (response.status_code, response.text)
    )
    else:
        print ("sent report to slack channel team-icc-ops")

#main
for destinationQueue in queueArray:
    url = base_url + destinationQueue + ',brokerName=localhost/QueueSize'
    outputTmp = call_ActiveMQ_REST(url, destinationQueue)
    output.append(outputTmp)

output.append(str('\n'))
    
#now fetch the total # of pending messages in all queues
response = requests.request("GET", url_to_fetch_total_count, headers=headers, data = payload)
resourceFetched = response.text.encode('utf8')

#load in json format
data = json.loads(resourceFetched)

totalCount = data['value']
output.append(str(data['value']) + ' \t' + ' TOTAL')

if totalCount > 10:
    output.append(str('\n') + 'WARNING: Total pending messages is more than 10')


send_notification_to_Slack(output)
