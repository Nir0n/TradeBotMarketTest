import hashlib
import hmac
from operator import itemgetter

from hyperquant.api import Platform, Sorting, Interval, Direction, OrderType
from hyperquant.clients import WSClient, Endpoint, Trade, Error, ErrorCode, \
    ParamName, WSConverter, RESTConverter, PlatformRESTClient, Candle

class OkexRESTConverterV1(RESTConverter):
    # Main params:
    base_url = "https://www.okex.com/api/v{version}/"
    # const_for_endpoints=".do"

    endpoint_lookup = {
        Endpoint.TRADE_HISTORY: "trades.do",
        Endpoint.CANDLE: "kline.do",
    }

    param_name_lookup = {
        ParamName.TIMESTAMP: "timestamp",
        ParamName.SYMBOL: "symbol",
        ParamName.FROM_ITEM: "fromId",
        ParamName.INTERVAL: "type",
        ParamName.LIMIT:"size",
        ParamName.FROM_TIME:"since"

    }
    param_value_lookup = {
        Sorting.DEFAULT_SORTING: Sorting.ASCENDING,

        Interval.MIN_1: "1min",
        Interval.MIN_3: "3min",
        Interval.MIN_5: "5min",
        Interval.MIN_15: "15min",
        Interval.MIN_30: "30min",
        Interval.HRS_1: "1hour",
        Interval.HRS_2: "2hour",
        Interval.HRS_4: "4hour",
        Interval.HRS_6: "6hour",
        Interval.HRS_12: "12hour",
        Interval.DAY_1: "1day",
        Interval.WEEK_1: "1week",

        # By properties:
        ParamName.DIRECTION: {
            Direction.SELL: "sell",
            Direction.BUY: "buy",
        },
    }

    endpoint_by_event_type = {
        "trades.do": Endpoint.TRADE_HISTORY,
        "kline.do": Endpoint.CANDLE,
    }

    param_lookup_by_class = {
        # Error
        Error: {
            "code": "code",
            "msg": "message",
        },
        # Data
        Trade: {
            "date": ParamName.TIMESTAMP,
            "price": ParamName.PRICE,
            "amount": ParamName.AMOUNT,
            "tid": ParamName.ITEM_ID,
            "type":ParamName.DIRECTION
        },
        Candle: [
            ParamName.TIMESTAMP,
            ParamName.PRICE_OPEN,
            ParamName.PRICE_HIGH,
            ParamName.PRICE_LOW,
            ParamName.PRICE_CLOSE,
            ParamName.AMOUNT,
        ],
    }

    # For converting time
    is_source_in_milliseconds = True

class OkexRESTClient(PlatformRESTClient):

    platform_id = Platform.OKEX
    version = "1"

    _converter_class_by_version = {
        "1": OkexRESTConverterV1,
    }

    def fetch_trades_history(self, symbol,from_item=None, **kwargs):
        return super().fetch_trades_history(symbol, from_item, **kwargs)


    def fetch_candles(self, symbol, interval, limit=None, from_time=None,  **kwargs):
        return super().fetch_candles(symbol, interval, limit, from_time,  **kwargs)


class OkexWSConverterV1(WSConverter):
    # Main params:
    base_url ="wss://real.okex.com:10440/ws/v{version}/"

    IS_SUBSCRIPTION_COMMAND_SUPPORTED = True

    # Settings:

    # Converting info:
    # For converting to platform

    endpoint_lookup = {
        Endpoint.TRADE: "ok_sub_spot_{symbol}_deals",
        Endpoint.CANDLE: "ok_sub_spot_{symbol}_kline_{interval}",
    }
    param_name_lookup = {
        ParamName.SYMBOL: "symbol",
        ParamName.INTERVAL: "type",
    }
    param_value_lookup = {
        Sorting.DEFAULT_SORTING: Sorting.ASCENDING,

        Interval.MIN_1: "1min",
        Interval.MIN_3: "3min",
        Interval.MIN_5: "5min",
        Interval.MIN_15: "15min",
        Interval.MIN_30: "30min",
        Interval.HRS_1: "1hour",
        Interval.HRS_2: "2hour",
        Interval.HRS_4: "4hour",
        Interval.HRS_6: "6hour",
        Interval.HRS_12: "12hour",
        Interval.DAY_1: "1day",
        Interval.WEEK_1: "1week",
    }
    # For parsing
    param_lookup_by_class = {
        # Error
        Error: {
            "code": "code",
            "msg": "message",
        },
        Trade: [
            ParamName.ITEM_ID,
            ParamName.PRICE,
            ParamName.AMOUNT,
            ParamName.TIMESTAMP,
            ParamName.DIRECTION
        ],
        Candle: [
            ParamName.TIMESTAMP,
            ParamName.PRICE_OPEN,
            ParamName.PRICE_HIGH,
            ParamName.PRICE_LOW,
            ParamName.PRICE_CLOSE,
            ParamName.AMOUNT,
        ],

    }

    endpoint_by_event_type = {
        "ok_sub_spot_{symbol}_deals": Endpoint.TRADE,
        "ok_sub_spot_{symbol}_kline_{interval}": Endpoint.CANDLE,
    }

    # For converting time
    is_source_in_milliseconds = True

    def __init__(self, platform_id=None, version=None):
        super().__init__(platform_id, version)

    def _generate_subscription(self, endpoint, symbol=None, **params):
        return super()._generate_subscription(endpoint, symbol if symbol else symbol, **params)

class OkexWSClient(WSClient):

    # Settings:
    platform_id = Platform.OKEX
    version = "1"

    _converter_class_by_version = {
        "1": OkexWSConverterV1,
    }

    def _send_subscribe(self,subscriptions):
        for subscription in subscriptions:
            params = {"event": "addChannel","channel": subscription}
            self._send(params)

    def subscribe(self, endpoints=None, symbols=None, **params):
        super().subscribe(endpoints, symbols, **params)

    def unsubscribe(self, endpoints=None, symbols=None, **params):
        super().unsubscribe(endpoints, symbols, **params)

