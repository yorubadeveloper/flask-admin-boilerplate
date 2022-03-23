import requests
import json
import time
import rich
import logging
from rich import print
from rich.logging import RichHandler
FORMAT = "%(message)s"
logging.basicConfig(level=logging.INFO, format=FORMAT,
                    datefmt="[%X]", handlers=[RichHandler()])
formatter = logging.Formatter(f"%(asctime)s - %(levelname)s - %(message)s")
log = logging.getLogger("rich")


global endpointURL, proxies
#endpointURL = 'https://webhook.site/bee475c1-d7e9-46e9-8ad0-ad96102ed56b'
endpointURL = "https://dev99406.service-now.com/api/576929/webhookdemo"
proxies = {
    "http": "http://198.161.14.25:8080",
    "https": "http://198.161.14.25:8080",
}


def createSNOWTicket(payload):

    log.info(f"Sending payload to SNOW to create ticket. {payload}")
    r = requests.post(endpointURL,
                      data=json.dumps(payload),
                      headers={'Content-Type': 'application/json', 'X-Webhook-Signature': 'fakeslug'})
    # , proxies=proxies)
    if r.status_code == 200:
        log.info(f"HTTP {r.status_code} Success!")
        return True, "Created a SNOW ticket! In the future I will return a JSON response with ticket details"
    else:
        log.critical(r.text)
        return False, f"Something wen't wrong! Http Error code: {r.status_code}"


def send_snow(webhook_url, message, edge_id, customer_name):
    company = customer_name
    alertType = 'AIOps Testing'
    product = 'NaaS Classic (Nuage)',
    shortDescription = f'{edge_id} issue reported by AIOps',
    Description = f'{edge_id} issue deccription: {message} ',
    severity = 3  

    payload = {
        "company": company,
        "alertType": alertType,
        "product": product,
        "short_description": shortDescription,
        "description": Description,
        "severity": severity
    }

    result, detail = createSNOWTicket(payload)

    return result, detail

    

if __name__ == '__main__':
    log.info("Starting script")
    examplePayload = {'company': 'ACME North America',
                      'alertType': 'AIOps Testing',
                      'product': 'Velocloud',
                      'shortDescription': 'Short description of the issue',
                      'Description': 'This is a long description of the issue',
                      'severity': 3}
    #ticket = createSNOWTicket(**examplePayload)
    ticket = createSNOWTicket(examplePayload)
    print(ticket)
