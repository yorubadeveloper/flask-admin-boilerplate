#!/usr/bin/python3

import os
from google.cloud import pubsub
import time

#
# Settings
#
ENABLE_LOG = True
LOG_FILE = "/tmp/sli_pubsub.log"

def log(msg):
    """
    Send log line to stdout and to LOG_FILE if logging is enabled
    """
    msg = "[%s] %s" % (logTimeStamp(), msg)

    # Print to stdout
    print(msg)

    # Output to logfile
    if ENABLE_LOG:
        try:
            lf = open(LOG_FILE, 'a')
            lf.write("%s\n" % (msg))

        except (OSError) as exc:
            print("Error while trying to log event: %s" % rlb(str(exc)))
            return False
        
        lf.close()    

    return True

def rlb(thing):
  """
  Return thing with line breaks replaced by spaces
  """
  return thing.replace("\r", " ").replace("\n", " ")


def logTimeStamp():
    """
    Return current date/time formatted for log output
    """
    return  time.strftime('%a %b %d %H:%M:%S %Y')

def pub_alert(pub_topic, subject, dict_attr):
    
    if ENABLE_LOG:
        log("Platform is  %s" % (pub_topic))
        log("Subject is  %s" % (subject))
        log("Host is  %s" % (dict_attr['Host']))
        log("Problem is  %s" % (dict_attr['Problem name']))

    publisher = pubsub.PublisherClient()
    topic_name = 'projects/{project_id}/topics/{topic}'.format(
        project_id="dashboard-293900",
        #project_id = os.getenv('dashboard-293900'),
        topic=pub_topic,  
    )
    
    #publisher.publish(topic_name, b'Triaged Zabbix Alert!', subject=subject, message=message)
    publisher.publish(topic_name, subject.encode('UTF-8'), edge_id=dict_attr['Host'], problem=dict_attr['Problem name'])

def pub_ticket(pub_topic, subject, dict_attr):
    
    if ENABLE_LOG:
        log("edge_id is  %s" % (dict_attr['edge_id']))
        log("Problem is  %s" % (dict_attr['problem']))

    publisher = pubsub.PublisherClient()
    topic_name = 'projects/{project_id}/topics/{topic}'.format(
        project_id="dashboard-293900",
        #project_id = os.getenv('dashboard-293900'),
        topic=pub_topic,  
    )
    
    #publisher.publish(topic_name, b'Triaged Zabbix Alert!', subject=subject, message=message)
    publisher.publish(topic_name, subject.encode('UTF-8'), edge_id=dict_attr['edge_id'], problem=dict_attr['problem'])
