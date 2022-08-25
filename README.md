## About

This is a small script for private use for controlling and monitoring
a large greenhouse roof window with MQTT and Home Assistant. The window is
moved by three linear actuators which are energized by six SPDT relays in
a H-bridge configuration and monitored by a three-channel DC current sensor.

The current sensor is used to approximiate the window position, detect when
the window is fully closed and stop the actuators at the same time when the
window is in open position - otherwise the three actuators slightly twist
the window.

SMBus communication with INA3221 uses slightly modified code from
https://github.com/switchdoclabs/SDL_Pi_INA3221.

Setup:

```
sudo apt install docker.io
sudo adduser pi docker
newgrp docker
docker build -t ikkuna:latest .
```

Run:

```
docker run -e MQTT_HOST=hostname -e MQTT_USER=user -e MQTT_PASSWD=password -d \
  --restart=always --device /dev/gpiomem --device /dev/i2c-1 ikkuna:latest
```
