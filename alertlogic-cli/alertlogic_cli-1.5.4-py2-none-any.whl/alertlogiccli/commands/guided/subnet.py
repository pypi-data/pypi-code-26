import alertlogiccli.command

import requests
import json


class SetSubnet():
    """Command to set subnet in otis"""

    def configure_parser(self, subparsers):
        parser = subparsers.add_parser("set_subnet", help="Sets a security subnet in otis")
        parser.set_defaults(command=self)

    def execute(self, context):
        args = context.get_final_args()
        otis = context.get_services().otis
        try:
            new_option = {
                "name": "predefined_security_subnet",
                "scope": {
                    "provider_id": args["provider_id"],
                    "provider_type": args["provider_type"],
                    "vpc_id": args["vpc"]
                },
                "value": args["subnet"]
            }
            response = otis.write_an_option(
                account_id=args["account_id"],
                json=new_option
            )
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            raise alertlogiccli.command.InvalidHTTPResponse("set_subnet", e.message)
        return "ok"

class GetConfiguration():
    """Command to get current configuration in otis"""

    def configure_parser(self, subparsers):
        parser = subparsers.add_parser("get_configuration", help="Gets a list of options for a scope")
        parser.set_defaults(command=self)

    def execute(self, context):
        args = context.get_final_args()
        otis = context.get_services().otis
        try:
            new_option = {
                "name": "predefined_security_subnet",
                "scope": {
                    "provider_id": args["provider_id"],
                    "provider_type": args["provider_type"],
                    "vpc_id": args["vpc"]
                },
                "value": args["subnet"]
            }
            response = otis.write_an_option(
                account_id=args["account_id"],
                json=new_option
            )
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            raise alertlogiccli.command.InvalidHTTPResponse("set_subnet", e.message)
        return "ok"
