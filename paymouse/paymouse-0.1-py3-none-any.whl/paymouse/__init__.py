from .models.card import Card
from .models.account import Account
from .models.money import Money

from .gateways.authorizenet import AuthorizeNet
from .gateways.braintree import Braintree
from .gateways.paypal import PayPal
from .gateways.stripe import Stripe

from .models.exceptions import InvalidGatewayException

GATEWAY = None


def setup(options: dict) -> None:
    global GATEWAY  # pylint: disable=W0603

    gateways = {
        'AuthorizeNet': AuthorizeNet,
        'Braintree': Braintree,
        'PayPal': PayPal,
        'Stripe': Stripe,
    }

    # Verify the user entered a gateway
    if 'gateway' not in options or options['gateway'] not in gateways:
        raise InvalidGatewayException

    GATEWAY = gateways[options['gateway']](options)


def charge(money, token, account: Account = None, card: Card = None, options: dict = None) -> dict:
    if options is None:
        options = {}

    return GATEWAY.charge(money, token, account, card, options)


def authorize(money, token, account: Account = None, card: Card = None, options: dict = None) -> dict:
    if options is None:
        options = {}

    return GATEWAY.authorize(money, token, account, card, options)


def void(charge_id: str, options: dict = None) -> dict:
    if options is None:
        options = {}

    return GATEWAY.void(charge_id, options)


def refund(charge_id: str, money: Money, options: dict = None) -> dict:
    if options is None:
        options = {}

    return GATEWAY.refund(charge_id, money, options)
