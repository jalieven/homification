# Homification

Notifications for home events.

## Prerequisites

### Input

    Smappee energy monitor

### Output

    Sonos equipment
    Siemens Hue lamps
    Raspberry Pi for low energy consumption

### Storage and tasking

    MongoDB
    Redis

### Python libraries

    pip install "celery[redis,msgpack,mongodb]"
    pip install pyyaml
    pip install phue
    pip install soco
    pip install gtts
