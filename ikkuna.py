import paho.mqtt.client as mqtt
import json
import os
from ctrl import Window, RelayCtrl, RelayCfg
from ina3221 import AmpsIntegrator, AmpsReader


def ha_autodiscovery_config():
    return dict(
        name="Kasvihuoneen ikkuna",
        stat_t="kasvihuone/ikkuna/stat",
        avty_t="kasvihuone/ikkuna/avty",
        command_topic="kasvihuone/ikkuna/set",
        position_topic="kasvihuone/ikkuna/pos",
        set_position_topic="kasvihuone/ikkuna/set_pos",
        pl_open="open",
        pl_cls="close",
        pl_stop="stop",
        stat_open="open",
        stat_opening="opening",
        stat_clsd="closed",
        stat_closing="closing",
        stat_stopped="stopped",
        pl_avail="online",
        pl_not_avail="offline",
        dev_cla="window",
        unique_id="khikkuna",
        obj_id="khikkuna",
    )


def register_ha_autodiscovery(client):
    cfg = json.dumps(ha_autodiscovery_config(), separators=(',', ':'))
    client.publish("homeassistant/cover/khikkuna/config", cfg, 0, True)
    print("HA autodiscovery enabled")


def on_connect(client, userdata, flags, rc):
    print("Connected")
    client.subscribe([("kasvihuone/ikkuna/set", 0),
                     ("kasvihuone/ikkuna/set_pos", 0)])
    register_ha_autodiscovery(client)
    client.publish("kasvihuone/ikkuna/stat", window.stat, 0, True)
    # TODO: Should probably only be online if we can talk to the current sensor
    client.publish("kasvihuone/ikkuna/avty", "online", 0, True)
    client.publish("kasvihuone/ikkuna/pos", window.pos, 0, True)


def on_message(client, userdata, msg):
    if msg.topic == "kasvihuone/ikkuna/set":
        pl = msg.payload.decode('UTF-8')
        if pl == "open":
            window.set_target(100)
        elif pl == "close":
            window.set_target(0)
        elif pl == "stop":
            window.stop()

    if msg.topic == "kasvihuone/ikkuna/set_pos":
        pos = int(msg.payload)
        if 0 <= pos <= 100:
            window.set_target(pos)

    print(msg.topic+" "+str(msg.payload))


def publish_stat(stat):
    print("publish stat", stat)
    client.publish("kasvihuone/ikkuna/stat", stat, 0, True)


def publish_pos(pos):
    print("publish pos", int(pos))
    client.publish("kasvihuone/ikkuna/pos", int(pos), 0, True)


# TODO: Should have a configuration file, command line arguments or similar
relay_cfg = RelayCfg([23, 27, 17], [24, 22, 25],
                     60.96426468, 31.64624152, 30.0)
relay_ctrl = RelayCtrl(relay_cfg)
integrator = AmpsIntegrator(AmpsReader())
window = Window(relay_ctrl, integrator)

window.on_stat.append(publish_stat)
window.on_pos.append(publish_pos)

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.username_pw_set(os.getenv("MQTT_USER"), os.getenv("MQTT_PASSWD"))
client.connect(os.getenv("MQTT_HOST"), 1883, 60)

client.loop_forever()
