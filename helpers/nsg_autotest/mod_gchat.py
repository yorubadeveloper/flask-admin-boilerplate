from json import dumps

from httplib2 import Http

edge_id = "100.100.100.1"

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

if __name__ == '__main__':
    webhook_url = "https://chat.googleapis.com/v1/spaces/AAAAuwtQdFk/messages?key=AIzaSyDdI0hCZtE6vySjMm-WEfRq3CPzqKqqsHI&token=ANa88kSkOk-6mebYdu1nOZyoGJDIVpTyX90-zjlLi-o%3D"
    message = f"AIOps Update for {edge_id}"
    send_gchat(webhook_url, message)
