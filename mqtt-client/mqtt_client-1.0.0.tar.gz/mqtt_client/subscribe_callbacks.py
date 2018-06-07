import subprocess


def default_subscribe_callback(mqttc, obj, msg):
    print(f'│{msg.topic}│ payload: {msg.payload}')


def subscribe_callback_raw(mqttc, obj, msg):
    print(msg.payload)


def subscribe_callback_command(command):
    def _(mqttc, obj, msg):
        response = subprocess.run(command.append(msg.payload), stdout=subprocess.PIPE)
        if response.stdout:
            print(response.stdout)
        if response.stderr:
            print(response.stderr)

    return _
