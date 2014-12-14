#!/usr/bin/env python
from input.gmail import Gmail
from input.smappee import Smappee
from output.sonos import Sonos

from celery import Celery

import logging
import yaml


class Homification:
    def __init__(self):
        self.log = logging.getLogger('homification')
        self.log.setLevel(logging.INFO)
        with open("homification.yml", 'r') as ymlfile:
            self.cfg = yaml.load(ymlfile)
            sonos_cfg = self.cfg['sonos']
            self.sonos = Sonos(volume=sonos_cfg['volume'],
                               tts_lang=sonos_cfg['tts_lang'],
                               webserver_path=sonos_cfg['webserver_path'],
                               webserver_port=sonos_cfg['webserver_port'])
            gmail_cfg = self.cfg['gmail']
            self.gmail = Gmail(username=gmail_cfg['username'],
                               password=gmail_cfg['password'],
                               label=gmail_cfg['label'])
            smappee_cfg = self.cfg['smappee']
            self.smappee = Smappee(username=smappee_cfg['username'],
                               password=smappee_cfg['password'])



tasks = Celery('tasks')
tasks.config_from_object('tasksconfig')


@tasks.task
def check_gmail_and_play_on_sonos():
    homification = Homification()
    notifications = homification.gmail.check()
    return homification.sonos.play_spoken_notifications(notifications)

@tasks.task
def check_smappee_store_and_play_on_sonos():
    homification = Homification()
    smappee_events = homification.smappee.check_and_store()
    notifications = []
    for event in smappee_events:
        notifications.append(event['label'])
    return homification.sonos.play_spoken_notifications(notifications)

