from datetime import date

from mercury import MarketdataApi
from mercury.utils import Utils
from mercury.api_client import ApiClient, Configuration


def create_api_client():
    # todo: file configuration / environment
    cfg = Configuration()
    cfg.host = "http://54.205.80.219:8080/mercury"
    return ApiClient(configuration=cfg)


class TestUtils:
    def __init__(self):
        self.api = MarketdataApi(api_client=create_api_client())

    def create_single_option_position(self, opening_date):
        from mercury import OptionSingle, Position

        name = "SPX"
        data = {'contract_type': 'CALL',
                'from_strike': 0.3,
                'to_strike': 0.5,
                'date': date(2018, 4, 9),
                'expiration': date(2018, 6, 15)}
        option_chain = self.api.get_vertically_sliced_option_chain_by_delta(
            name, **data)
        option_contract = option_chain.contracts[0]
        option_single = OptionSingle(symbol='SPX',
                                     direction='LONG',
                                     quantity=1,
                                     opening_date=opening_date,
                                     type='single',
                                     option_contract=option_contract)
        position = Position(trades=[option_single])
        return position

    def create_long_put_butterfly_position(self, opening_date):
        from mercury import \
            Butterfly, Position

        name = "SPX"
        data = {'contract_type': 'PUT',
                'from_strike': 0.-0.5,
                'to_strike': -0.4,
                'date': date(2018, 4, 9),
                'expiration': date(2018, 6, 15)}
        option_chain = self.api.get_vertically_sliced_option_chain_by_delta(
            name, **data)
        option_contracts = option_chain.contracts
        short_contract = option_contracts[int(len(option_contracts) / 2)]
        long_lower_leg = Utils.create_option_leg_with_option_contract(
            option_contract=option_contracts[0],
            direction='LONG',
            quantity=1)
        short_leg = Utils.create_option_leg_with_option_contract(
            option_contract=short_contract,
            direction='SHORT',
            quantity=2)
        long_upper_leg = Utils.create_option_leg_with_option_contract(
            option_contract=option_contracts[-1],
            direction='LONG',
            quantity=1)
        butterfly = Butterfly(
            symbol='SPX',
            direction='LONG',
            quantity=10,
            opening_date=opening_date,
            first_leg=long_lower_leg,
            mid_leg=short_leg,
            third_leg=long_upper_leg)
        position = Position(trades=[butterfly])
        return position
