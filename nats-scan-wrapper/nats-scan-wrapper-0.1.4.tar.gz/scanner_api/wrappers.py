import asyncio
import logging
import nats.aio.client
import json
from datetime import datetime
from .errors import *
from ._modes import function_mode_old, process_mode
from ._version import __version__

logging.basicConfig(
    format=u'%(levelname)-8s [%(asctime)s]  %(message)s',
    level=logging.INFO
)


class scanner_wrapper:
    nc = None
    config = {
        # Count packets from queue received at a time
        # "data_pack_size": 1,
        "tls": None,
        "worker_function": None,
        # Return array of args for process. Calling: input_handler(data, meta)
        "input_handler": None,
        # Processing lines from process. Return array with results. Calling: output_handler(line)
        # Line - not decoded
        "output_handler": None,

        # FLAGS --------------
        "send_meta": True,
        # each result from array will be sended directly to NATS
        "send_raw": False,
        # output handler must take array with lines if chunked_send not True
        # collect all output of module and send to your handler function
        "chunked_send": False,
        # result must be DICT! and then its added to previous
        "add_result_to_data": False,
        # Process lines or bytes
        "readline": False,
        # print out stderr from procee or not
        "print_stderr": False,
        # receive only one message or all from NATS queue
        "one_message_receive": True,
        "check_expired": True,
    }
    # when you subscribes to two queues may been created two processes
    # control that with semaphore
    sem = asyncio.Semaphore(1)

    def __init__(self, **kwargs):
        if "name" in kwargs:
            nats.aio.client.__version__ = kwargs["name"]
        else:
            raise ModuleNameError()

        self.nc = nats.aio.client.Client()
        self.config.update(kwargs)

    def configure(self, **kwargs):
        self.config.update(kwargs)

    def decode_msg(self, msg):
        """Decode messages from NATS
        Return json objects with data and meta
        Return cur_pipeline
        """
        cur_pipeline = msg.subject
        task_raw = msg.data.decode()
        task = json.loads(task_raw)
        return task["data"], task["meta"], cur_pipeline

    def make_packages(self, data, meta, result_array):
        """String assembly before send to nats
        """
        packages = []
        for result in result_array:
            if self.config["send_raw"]:
                package = result
            else:
                if self.config["add_result_to_data"]:
                    new_data = data
                    new_data.update(result)
                    package = {"data": new_data, "meta": meta}
                else:
                    package = {"data": result, "meta": meta}

            packages.append(package)
        return packages

    # todo publishers to another files
    async def nats_publisher(self, pipeline, packages):
        """Push scan results to NATS
        Each element in packages has been sended separately
        """
        for package in packages:
            if not self.config["send_raw"]:
                package = json.dumps(package).encode()
            await self.nc.publish(pipeline, package)

    async def nats_report_publisher(self, data, meta, result_array, **kwargs):
        """Send service infromation to special module in NATS network
        All kwargs will be sended in json
        """
        package = {"data": {}, "meta": meta}
        package["meta"]["timestamp"] = datetime.now().timestamp()
        package["meta"]["cur_scanner"] = self.config["name"]

        for key, value in kwargs.items():
            package["meta"][key] = value
        if result_array:
            for result in result_array:
                if self.config["send_raw"]:
                    await self.nc.publish("_reporter", result)
                else:
                    new_data = data
                    new_data.update(result)
                    package["data"] = new_data
                    await self.nc.publish("_reporter", json.dumps(package).encode())
        else:
            await self.nc.publish("_reporter", json.dumps(package).encode())

    async def sub_one_msg(self, name, queue, callback):
        """Subscrbe to NATS for only one message
        """
        sid = await self.nc.subscribe(name, queue, cb=callback, is_async=True)
        await self.nc.auto_unsubscribe(sid, 1)
        return sid

    def task_time_is_expired(self, meta):
        return (datetime.now() - datetime.fromtimestamp(meta["scan_start_time"])).seconds > int(meta["max_scan_time"])

    async def _run(self, loop):
        logging.info("Started nat module wrapper. Version '%s'", __version__)

        @asyncio.coroutine
        def disconnected_cb():
            logging.info("Got disconnected!")

        @asyncio.coroutine
        def reconnected_cb():
            # See who we are connected to on reconnect.
            logging.info("Got reconnected to " +
                         str(self.nc.connected_url.netloc))

        @asyncio.coroutine
        def error_cb(e):
            logging.error("There was an error: " + str(e))

        @asyncio.coroutine
        def closed_cb():
            logging.info("Connection is closed")

        # Configuring nats
        options = {
            # Setup pool of servers from a NATS cluster.
            "servers": self.config['nats'],
            "tls": self.config['tls'],
            "io_loop": loop,
            # Will try to connect to servers in order of configuration,
            # by defaults it connect to one in the pool randomly.
            "dont_randomize": True,
            # Optionally set reconnect wait and max reconnect attempts.
            # This example means 10 seconds total per backend.
            # Next two lines configure client to try to reconnect approximately 7 days ( 8960 * 10 )- 7 days in seconds
            "max_reconnect_attempts": 8960,
            "reconnect_time_wait": 10,
            # Setup callbacks to be notified on disconnects and reconnects
            "disconnected_cb": disconnected_cb,
            "reconnected_cb": reconnected_cb,
            # Setup callbacks to be notified when there is an error
            # or connection is closed.
            "error_cb": error_cb,
            "closed_cb": closed_cb,
        }
        async def connect():
            while not self.nc.is_connected:
                try:
                    await self.nc.connect(**options)
                    logging.info("Connected to NATS.")
                    logging.info("Started module named '{name}'.".format(
                        name=self.config["name"]))
                except nats.aio.client.ErrNoServers as e:
                    # Could not connect to any server in the cluster.
                    logging.error(e)

        await connect()

        @asyncio.coroutine
        async def message_handler(msg):
            """Create another process from args send output to output_handler(output_line)
            and then calling result_publisher
            """
            with (await self.sem):
                try:
                    data, meta, cur_pipeline = self.decode_msg(msg)
                    new_pipeline = ".".join(cur_pipeline.split(".")[1:])
                    status = ""

                    logging.info("Received from '%s':", cur_pipeline)
                    logging.info("Meta: '%s'", meta)
                    logging.info("Data: '%s'", data)

                    # Task begin report
                    if self.config["send_meta"]:
                        await self.nats_report_publisher(
                            data,
                            meta,
                            [],
                            status="begin",
                            new_pipeline=new_pipeline,
                        )
                        logging.info("Begin report has been sended.")
                        # Fix no time for send. Swap context to await.
                        await asyncio.sleep(0)

                    if self.config["check_expired"] and self.task_time_is_expired(meta):
                        raise ExpiredTimeError()

                    try:
                        if self.config["worker_function"]:
                            await function_mode_old(self, data, meta, new_pipeline)
                        elif self.config["input_handler"] and self.config["output_handler"]:
                            await process_mode(self, data, meta, new_pipeline)
                        else:
                            raise NotEnoughArgsError()

                    except BadPackageDataError as e:
                        logging.error("Bad Package")
                        status = "error.data"

                    except Exception as e:
                        logging.error(
                            "Exception in worker! Report will be sended!")
                        logging.error(str(e))
                        status = "error"

                    # Task end report
                    if self.config["send_meta"]:
                        await self.nats_report_publisher(
                            data,
                            meta,
                            [],
                            status="end",
                            new_pipeline=new_pipeline,
                        )
                        logging.info("End report has been sended.")

                except ExpiredTimeError as expired:
                    logging.warning("Received task with expired time!")

                except Exception as e:
                    logging.error("Unexpected exception in main logic!!!")
                    logging.error(str(e))

                if self.config["one_message_receive"]:
                    # resub on one message mechanism
                    if cur_pipeline == str(self.config["name"]):
                        resub_pipeline = str(self.config["name"])
                    else:
                        resub_pipeline = str(self.config["name"]) + ".>"
                    await self.sub_one_msg(
                        resub_pipeline,
                        str(self.config["name"]),
                        message_handler
                    )

        if self.nc.is_connected:
            # Simple publisher and async subscriber via coroutine.
            if self.config["one_message_receive"]:
                await self.sub_one_msg(
                    str(self.config["name"]) + ".>",
                    str(self.config["name"]),
                    message_handler
                )
                await self.sub_one_msg(
                    str(self.config["name"]),
                    str(self.config["name"]),
                    message_handler
                )
            else:
                await self.nc.subscribe(
                    str(self.config["name"]) + ".>",
                    str(self.config["name"]),
                    cb=message_handler,
                    is_async=True
                )
                await self.nc.subscribe(
                    str(self.config["name"]),
                    str(self.config["name"]),
                    cb=message_handler,
                    is_async=True
                )


            while True:
                await asyncio.sleep(5, loop=loop)
                if not self.nc.is_connected:
                    await self.nc.close()
                    await connect()


    def run(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._run(loop))
        loop.close()
