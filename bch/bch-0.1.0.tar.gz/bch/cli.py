#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import logging
import click
import click_log
import simplejson as json
from datetime import datetime
import paho.mqtt.client
from paho.mqtt.client import topic_matches_sub
import bch.node
import bch.gateway
from bch.mqtt_client import MqttClient

__version__ = '0.1.0'

CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])

logger = logging.getLogger()
handler = click_log.ClickHandler()
handler.setFormatter(click_log.ColorFormatter('%(asctime)s %(message)s'))
logger.addHandler(handler)


@click.group(context_settings=CONTEXT_SETTINGS)
@click.option('--gateway', type=click.STRING, help="Gateway name [default: usb-dongle].", default="usb-dongle")
@click.option('-H', '--mqtt-host', type=click.STRING, default="127.0.0.1", help="MQTT host to connect to [default: 127.0.0.1].")
@click.option('-P', '--mqtt-port', type=click.IntRange(0, 65535), default=1883, help="MQTT port to connect to [default: 1883].")
@click.option('--mqtt-username', type=click.STRING, help="MQTT username.")
@click.option('--mqtt-password', type=click.STRING, help="MQTT password.")
@click.option('--mqtt-cafile', type=click.Path(exists=True), help="MQTT cafile.")
@click.option('--mqtt-certfile', type=click.Path(exists=True), help="MQTT certfile.")
@click.option('--mqtt-keyfile', type=click.Path(exists=True), help="MQTT keyfile.")
@click_log.simple_verbosity_option(logger, default='WARNING')
@click.pass_context
def cli(ctx, gateway, mqtt_host, mqtt_port, mqtt_username, mqtt_password, mqtt_cafile, mqtt_certfile, mqtt_keyfile):

    ctx.obj['mqttc'] = MqttClient(mqtt_host, mqtt_port, mqtt_username, mqtt_password, mqtt_cafile, mqtt_certfile, mqtt_keyfile)
    ctx.obj['gateway'] = gateway
    # mqttc.reconnect()


@cli.command()
@click.option('--start', 'command', flag_value='start')
@click.option('--stop', 'command', flag_value='stop')
@click.pass_context
def pairing(ctx, command):
    if not command:
        click.echo(pairing.get_help(ctx))
        sys.exit(1)

    mqttc.loop_start()
    msg = mqttc.publish('gateway/' + userdata['gateway'] + '/pairing-mode/' + command, None, qos=1)
    msg.wait_for_publish()


@cli.command()
@click.argument('topic', type=click.STRING)
@click.argument('payload', type=click.STRING, required=False)
@click.pass_context
def pub(ctx, topic, payload):
    if payload:
        try:
            payload = json.loads(payload, use_decimal=True)
        except json.decoder.JSONDecodeError as e:
            pass
    mqttc = ctx.obj['mqttc']
    msg = mqttc.publish(topic, payload, qos=1)
    msg.wait_for_publish()


@cli.command(help="Subscribe topic.", epilog="TOPIC [default: #]")
@click.argument('topic', type=click.STRING, default="#")
@click.option('-n', '--number', type=click.INT, help="Number of messages.")
@click.pass_context
def sub(ctx, topic, number):
    def on_message(client, userdata, message):
        dt = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:22]
        click.echo(dt + ' ' + message.topic + ' ' + message.payload.decode('utf-8'))
        on_message.cnt += 1
        if number and on_message.cnt == number:
            sys.exit(0)

    on_message.cnt = 0

    mqttc = ctx.obj['mqttc']
    mqttc.mqttc.on_message = on_message
    mqttc.subscribe(topic)
    mqttc.loop_forever()


@cli.command(help="Show program's version number and exit.")
def version():
    click.echo(__version__)


cli.add_command(bch.gateway.gw)
cli.add_command(bch.node.node)


def main():
    cli(obj={})


if __name__ == '__main__':
    main()
