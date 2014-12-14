from celery.schedules import crontab
from datetime import timedelta

BROKER_URL = 'redis://localhost'

CELERY_ACCEPT_CONTENT = ['json']

CELERY_RESULT_BACKEND = 'mongodb://localhost:27017/'
CELERY_MONGODB_BACKEND_SETTINGS = {
    'database': 'homification',
    'taskmeta_collection': 'meta_tasks'
}
CELERY_TASK_SERIALIZER = 'json'

CELERYBEAT_SCHEDULE_FILENAME = 'homification-beat'
CELERYBEAT_SCHEDULE = {
    'gmail-every-minute-daytime': {
        'task': 'homification.check_gmail_and_play_on_sonos',
        'schedule': crontab(minute='*/1', hour='7-22')
    },
    'smappee-every-30-seconds': {
        'task': 'homification.check_smappee_store_and_play_on_sonos',
        'schedule': timedelta(seconds=30)
    }
}