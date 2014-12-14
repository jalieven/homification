import httplib2
import datetime
import logging

from urllib import urlencode
from json import loads
from pymongo import MongoClient

MY_SMAPPEE_ENDPOINT = 'https://my.smappee.com/api/v1'
MY_SMAPPEE_LOGIN_CONTEXT = '/login'
MY_SMAPPEE_SERVICELOCATION_CONTEXT = '/servicelocation'
MY_SMAPPEE_EVENTS_CONTEXT = '/recentevents'


class Smappee:
    def __init__(self, username=None, password=None,
                 smappee_token_file='smappee.token',
                 smappee_service_location_file='smappee.servicelocation'):
        self.log = logging.getLogger('smappee')
        self.log.setLevel(logging.INFO)
        self.username = username
        self.password = password
        self.smappee_token_file = smappee_token_file
        self.smappee_service_location_file = smappee_service_location_file
        open(smappee_token_file, 'a').close()
        open(smappee_service_location_file, 'a').close()
        mongo = MongoClient()
        db = mongo.homification
        self.smappee_events = db.smappee_events

    def check_and_store(self):
        token = self.get_smappee_token()
        servicelocation = self.get_my_servicelocation(token=token)
        events = self.get_appliance_events(token=token, servicelocation=servicelocation)
        fresh_events = []
        if events:
            for event in events:
                timestamp = event['timestamp']
                parsed_stamp = datetime.datetime.fromtimestamp(int(str(timestamp)[0:-3]))
                event['timestamp'] = parsed_stamp
                stamp = parsed_stamp.strftime('%Y-%m-%d %H:%M:%S')
                state = 'OFF' if event['power'] <= 0 else 'ON'
                appliance = event['label']
                self.log.info(stamp + ' - ' + appliance + ' - ' + state)
                if self.smappee_events.find_one({'timestamp': event['timestamp']}) is None:
                    self.smappee_events.insert(event)
                    fresh_events.append(event)
        return fresh_events

    def get_cached_smappee_token(self):
        with open(self.smappee_token_file) as myfile:
            return "".join(line.rstrip() for line in myfile)

    def set_cached_smappee_token(self, token=None):
        if token:
            with open(self.smappee_token_file, "w+") as f:
                return f.write(token)

    def get_cached_smappee_servicelocation_id(self):
        with open(self.smappee_service_location_file) as myfile:
            return "".join(line.rstrip() for line in myfile)

    def set_cached_smappee_servicelocation_id(self, servicelocation=None):
        with open(self.smappee_service_location_file, "w+") as f:
            return f.write(str(servicelocation))

    def smappee_login(self, username=None, password=None, locale='nl'):
        h = httplib2.Http()
        data = dict(userName=username, password=password, locale=locale)
        resp, content = h.request(uri=MY_SMAPPEE_ENDPOINT + MY_SMAPPEE_LOGIN_CONTEXT,
                                  method='POST',
                                  body=urlencode(data))
        self.log.info("Login: " + str(resp) + " | " + str(content))
        if resp.status == 200:
            fresh_token = loads(content.decode("utf-8"))['token']
            self.set_cached_smappee_token(fresh_token)
            return fresh_token
        else:
            return None

    def get_smappee_token(self, do_login=False):
        cached_token = self.get_cached_smappee_token()
        if not cached_token or do_login:
            return self.smappee_login(username=self.username, password=self.password)
        else:
            return cached_token

    def get_my_servicelocation(self, token=None):
        if token:
            cached_servicelocation_id = self.get_cached_smappee_servicelocation_id()
            if not cached_servicelocation_id:
                h = httplib2.Http()
                headers = {'token': token}
                resp, content = h.request(uri=MY_SMAPPEE_ENDPOINT + MY_SMAPPEE_SERVICELOCATION_CONTEXT,
                                          method='GET',
                                          headers=headers)
                self.log.info('ServiceLocation: ' + str(resp) + " | " + str(content))
                if resp.status == 200:
                    service_location_id = loads(content.decode("utf-8"))[0]['id']
                    self.set_cached_smappee_servicelocation_id(servicelocation=service_location_id)
                    return service_location_id
                elif resp.status == 401:
                    return self.get_my_servicelocation(self.get_smappee_token(True))
                else:
                    return None
            else:
                return cached_servicelocation_id
        else:
            return None

    def get_appliance_events(self, token=None, servicelocation=None, maxNumber='5', maxAge='0'):
        h = httplib2.Http()
        headers = {'token': token}
        resp, content = h.request(uri=MY_SMAPPEE_ENDPOINT + MY_SMAPPEE_SERVICELOCATION_CONTEXT + '/' +
                                      str(servicelocation) + MY_SMAPPEE_EVENTS_CONTEXT +
                                      '?maxNumber=' + maxNumber + '&maxAge=' + maxAge,
                                  method='GET',
                                  headers=headers)
        self.log.info('Events: ' + str(resp) + " | " + str(content))
        if resp.status == 200:
            return loads(content.decode("utf-8"))
        elif resp.status == 401:
            fresh_token = self.get_smappee_token(True)
            return self.get_appliance_events(token=fresh_token, servicelocation=self.get_my_servicelocation(fresh_token))
        elif resp.status == 500:
            self.log.error('Error while retrieving events: ' + str(resp))
            return None
        else:
            return None



