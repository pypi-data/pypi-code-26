class SortBy:

    ID = 'id'
    RANK = 'rank'
    VOLUME = 'volume_24h'
    PERCENT = 'percent_change_24h'

    TYPES = (
        (ID, 'Id'),
        (RANK, 'Rank'),
        (VOLUME, 'Volume 24H'),
        (PERCENT, 'Percent change 24H'),
    )


class SupportedFormats:

    LIST = 'array'
    DICT = 'dictionary'

    TYPES = (
        (LIST, 'list'),
        (DICT, 'dict'),
    )


class Currencies:

    AUD = 'AUD'
    BCH = 'BCH'
    BRL = 'BRL'
    BTC = 'BTC'
    CAD = 'CAD'
    CHF = 'CHF'
    CLP = 'CLP'
    CNY = 'CNY'
    CZK = 'CZK'
    DKK = 'DKK'
    ETH = 'ETH'
    EUR = 'EUR'
    GBP = 'GBP'
    HKD = 'HKD'
    HUF = 'HUF'
    IDR = 'IDR'
    ILS = 'ILS'
    INR = 'INR'
    JPY = 'JPY'
    KRW = 'KRW'
    LTC = 'LTC'
    MXN = 'MXN'
    MYR = 'MYR'
    NOK = 'NOK'
    NZD = 'NZD'
    PHP = 'PHP'
    PKR = 'PKR'
    PLN = 'PLN'
    RUB = 'RUB'
    SEK = 'SEK'
    SGD = 'SGD'
    THB = 'THB'
    TRY = 'TRY'
    TWD = 'TWD'
    XRP = 'XRP'
    ZAR = 'ZAR'

    TYPES = (
        (AUD, 'Australia Dollar'),
        (BCH, 'Bitcoin Cash'),
        (BRL, 'Brazil Real'),
        (BTC, 'Bitcoin'),
        (CAD, 'Canada Dollar'),
        (CHF, 'Switzerland Franc'),
        (CLP, 'Chile Peso'),
        (CNY, 'China Yuan Renminbi'),
        (CZK, 'Czech Republic Koruna'),
        (DKK, 'Denmark Krone'),
        (ETH, 'Ethereum'),
        (EUR, 'Euro Member Countries'),
        (GBP, 'United Kingdom Pound'),
        (HKD, 'Hong Kong Dollar'),
        (HUF, 'Hungary Forint'),
        (IDR, 'Indonesia Rupiah'),
        (ILS, 'Israel Shekel'),
        (INR, 'Indian Rupee'),
        (JPY, 'Japanese Yen'),
        (KRW, 'Korea (South) Won'),
        (LTC, 'Litecoin'),
        (MXN, 'Mexico Peso'),
        (MYR, 'MYR - Malaysian Ringgit'),
        (NOK, 'Norway Krone'),
        (NZD, 'New Zealand Dollar'),
        (PHP, 'Philippines Piso'),
        (PKR, 'Pakistan Rupee'),
        (PLN, 'Poland Zloty'),
        (RUB, 'Russia Ruble'),
        (SEK, 'Sweden Krona'),
        (SGD, 'Singapore Dollar'),
        (THB, 'Thailand Baht'),
        (TRY, 'Turkey Lira'),
        (TWD, 'Taiwan New Dollar'),
        (XRP, 'Ripple'),
        (ZAR, 'South Africa Rand'),
    )
