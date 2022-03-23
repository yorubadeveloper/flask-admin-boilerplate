from json import dumps
from httplib2 import Http
import yaml
import os

def send_gchat(webhook_url, message):
    """Hangouts Chat incoming webhook quickstart."""
    url = webhook_url
    bot_message = {
        'text' : f'{message}'}

    message_headers = {'Content-Type': 'application/json; charset=UTF-8'}

    http_obj = Http()

    response = http_obj.request(
        uri=url,
        method='POST',
        headers=message_headers,
        body=dumps(bot_message),
    )

    print(response)

def send_slack(webhook_url, message):
    #command = "curl -X POST -H 'Content-type: application/json' --data '{\"text\": \"" + message + "\"}' " + \
    #          config.get("slack-web-hook")
    command = "curl -X POST -H 'Content-type: application/json' --data '{\"text\": \"" + message + "\"}' " + \
               webhook_url

    os.system(command)

if __name__ == '__main__':
    edge_id = "100.100.100.1"

    config = yaml.safe_load(open("config.yml", "r").read())
    webhook_url = config.get("webhook_url_slack2")
    message = f"Test from AIOps with update for {edge_id}"
    #send_gchat(webhook_url, message)
    send_slack(webhook_url, message)
