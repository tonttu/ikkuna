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
