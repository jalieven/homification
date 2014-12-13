#!/usr/bin/env python
from input.gmail import Gmail
from output.sonos import Sonos
from apscheduler.schedulers.blocking import BlockingScheduler

import logging
import yaml
import time
import multiprocessing


logging.basicConfig(filename='./homification.log',
                    format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                    level=logging.WARN)


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
                               password=gmail_cfg['password'])

    def init_scheduler(self):
        sched = BlockingScheduler()
        sched.add_job(self.check_and_play(), 'cron', minute='*', hour='6-23', max_instances=2)
        #sched.add_job(smappee.sync_with_smappee, 'cron', second='*/15', hour='6-23')
        sched.start()

    def check_and_play(self):
        notifications = self.gmail.check_gmail()
        self.sonos.play_spoken_notifications(notifications)

    def check_and_play_notifications(self):
        p = multiprocessing.Process(target=self.check_and_play, name="Check and Play")
        p.start()
        # Wait 55 seconds for foo
        time.sleep(55)
        # Terminate check_and_play
        p.terminate()
        # Cleanup
        p.join()


Homification().init_scheduler()


