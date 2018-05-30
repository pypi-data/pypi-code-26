#!/usr/bin/env python3
# vim: ai ts=4 sts=4 et sw=4 nu

import requests
import click
import sys
import ast
import time

s = requests.Session()


class FutureTimestampParamType(click.ParamType):
    name = "futuretimestamp"

    def convert(self, value, param, ctx):
        now = int(time.time())

        # If timestamp starts with a +, we add the value to "now".
        if value.startswith("+"):
            try:
                inc = int(value)
                timestamp = now + inc
                return timestamp
            except:
                self.fail("%s is not a value integer." % value, param, ctx)
        else:
            try:
                timestamp = int(value)
                if timestamp > now:
                    return timestamp
                else:
                    self.fail(
                        "%s is in the past (now = %s)." % (value, now), param, ctx
                    )
            except ValueError:
                self.fail("%s is not a value integer." % value, param, ctx)


FUTURE_TIMESTAMP = FutureTimestampParamType()


@click.group()
@click.option("--baseurl", prompt=True)
@click.option("--username", prompt=True)
@click.option("--password", prompt=True, hide_input=True)
@click.pass_context
def cli(ctx, baseurl, username, password):
    ctx.obj["BASEURL"] = baseurl
    ctx.obj["USERNAME"] = username
    ctx.obj["PASSWORD"] = password

    r = s.post(baseurl + "/user/auth", data={"login": username, "password": password})

    r.raise_for_status()

    if (
        r.history[0].status_code == 302
        and "Invalid user or Password" in r.history[0].headers["Location"]
    ):
        print("Error: Wrong user or password")
        sys.exit(1)


def run_shinken_command(url):
    print("Running %s" % url)
    r = s.get(url)

    r.raise_for_status()

    response = ast.literal_eval(r.content.decode())

    if response["status"] != 200 or response["text"] != "Command launched":
        print("Error: command did not launched")
        sys.exit(1)

    print("Command launched")


@cli.command()
@click.option("--host", required=True)
@click.option("--service")
@click.option("--message", required=True)
@click.pass_context
def add_comment(ctx, host, service, message):
    baseurl = ctx.obj["BASEURL"]
    username = ctx.obj["USERNAME"]

    if service:
        elt = host + "/" + service
        action = "ADD_SVC_COMMENT"
    else:
        elt = host
        action = "ADD_HOST_COMMENT"

    run_shinken_command(
        "%s/action/%s/%s/1/%s/%s" % (baseurl, action, elt, username, message)
    )


@cli.command()
@click.option("--host", required=True)
@click.option("--service")
@click.option("--message")
@click.option("--expire", type=FUTURE_TIMESTAMP)
@click.option("--sticky/--no-sticky", default=True)
@click.option("--notify/--no-notify", default=True)
@click.option("--persistent/--no-persistent", default=True)
@click.pass_context
def ack(ctx, host, service, message, expire, sticky, notify, persistent):
    baseurl = ctx.obj["BASEURL"]
    username = ctx.obj["USERNAME"]

    if message is None:
        message = "Acknowledged from CLI by %s" % username

    if service:
        elt = host + "/" + service
        action = "ACKNOWLEDGE_SVC_PROBLEM"
    else:
        elt = host
        action = "ACKNOWLEDGE_HOST_PROBLEM"

    options = "%s/%s/%s" % (int(sticky) + 1, int(notify), int(persistent))

    print(expire)

    if expire:
        options += "/%s" % expire
        action += "_EXPIRE"

    run_shinken_command(
        "%s/action/%s/%s/%s/%s/%s" % (baseurl, action, elt, options, username, message)
    )


@cli.command()
@click.option("--host", required=True)
@click.option("--service")
@click.pass_context
def recheck(ctx, host, service):
    baseurl = ctx.obj["BASEURL"]

    if service:
        elt = host + "/" + service
        action = "SCHEDULE_FORCED_SVC_CHECK"
    else:
        elt = host
        action = "SCHEDULE_FORCED_HOST_CHECK"

    run_shinken_command("%s/action/%s/%s/$NOW$" % (baseurl, action, elt))


if __name__ == "__main__":
    cli(auto_envvar_prefix="SHINKEN", obj={})
