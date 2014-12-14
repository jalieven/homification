from util.nic import Nic

import soco
import time
import datetime
import logging

from soco.snapshot import Snapshot
from gtts import gTTS


class Sonos:
    def __init__(self, volume=None,
                 tts_lang=None,
                 max_notification_seconds=10,
                 webserver_path='/usr/share/nginx/www/',
                 webserver_port='8000'):
        self.volume = volume
        self.tts_lang = tts_lang
        self.max_notification_seconds = max_notification_seconds
        self.webserver_path = webserver_path
        self.webserver_port = webserver_port
        self.log = logging.getLogger('sonos')
        self.log.setLevel(logging.INFO)

    def play_spoken_notifications(self, notifications=None):
        notification_mp3s = []
        for notification in notifications:
            tts = gTTS(text=notification, lang=self.tts_lang)
            now = datetime.datetime.now()
            filename = now.strftime('%Y-%m-%d_%H-%M-%S-%f') + ".mp3"
            notification_mp3s.append(filename)
            tts.save(self.webserver_path + filename)

        if notification_mp3s:
            group_coordinator = None
            for zone in list(soco.discover()):
                if zone.group.coordinator.player_name == zone.player_name:
                    group_coordinator = zone

                zone_snapshot = Snapshot(zone)
                zone_snapshot.snapshot()
                time.sleep(1)
                zone.volume = int(self.volume)
                for mp3 in notification_mp3s:
                    self.log.info('Playing notification ' + mp3 + ' on ' + zone.player_name)
                    zone.play_uri(uri='http://' + Nic().get_current_address() + ':' + self.webserver_port + '/' + mp3)
                    time.sleep(self.max_notification_seconds)
                zone_snapshot.restore()

            if group_coordinator is not None:
                for zone in list(soco.discover()):
                    if zone.group.coordinator.player_name != zone.player_name:
                        print zone.player_name + ' joining ' + zone.group.coordinator.player_name
                        zone.join(group_coordinator)
        return notifications
