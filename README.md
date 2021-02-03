videosdownloader
================

Simple wrapper script around youtube-dl. All the new videos will be downloaded
to the folder of your choice.


Installation
------------

Clone this repo (ideally in a virtualenv), then install the dependencies :

```
pip install youtube-dl toml
```

If you're on a systemd-based system, and you would like to log to journald,
also install [systemd](https://pypi.org/project/systemd/) (kind of a pain to
install, I installed it through my os package manager and then symlinked the
virtualenv systemd to my system one)

Configuration
-------------

Edit the `vids_directory` in the toml config file, and add all the
channels/playlists/whatever you want to subscribe to in the channels section.
You might need to adjust the code a little bit depending on the websites you
plan to use.

By default, it will create one cache file per channel, keeping the id of all
the previously downloaded videos. Then it will download videos from the very
first one of the channel. Unless that's what you want, you should create that
cache file yourself and put the id of the first video :
* go to the vids directory you configured
* create `.nameofchannel` file, `nameofchannel` being the name you configured
  for one channel
* put the id of the last video you watched (for a youtube video for instance,
  that would be the id right after the `watch?v=`
Then it will start downloading from that video

Scheduling the script to run
----------------------------

Those instructions are for systemd-based systems.

Add a .service and a .timer file in ~/.config/systemd/user, examples :

vids.service file
```
[Unit]
Description=Download videos from the internet

[Service]
ExecStart=/path/to/virtualenv/python /path/to/vids.py
Type=oneshot
```

vids.timer file
```
[Unit]
Description=Schedule the videos downloader

[Timer]
# start 20 seconds after boot
OnStartupSec=20

[Install]
WantedBy=timers.target
```

Then run `systemctl --user daemon-reload` and you're done. To trigger it
manually, run : `systemctl --user start vids.service`, otherwise it will run
once after each boot.
