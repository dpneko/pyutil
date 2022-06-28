from binascii import hexlify, unhexlify
import hashlib
import string
import logging

log = logging.getLogger(__name__)


class Base58(object):
    """Base58 base class

    This class serves as an abstraction layer to deal with base58 encoded
    strings and their corresponding hex and binary representation
    throughout the library.

    :param data: Data to initialize object, e.g. pubkey data, address data,
    ...

    :type data: hex, base58 string

    :param str prefix: Prefix to use for Address/PubKey strings (defaults
    to ``0x41``)

    :return: Base58 object initialized with ``data``

    :rtype: Base58

    :raises ValueError: if data cannot be decoded

    * ``bytes(Base58)``: Returns the raw data
    * ``str(Base58)``:   Returns the readable ``Base58CheckEncoded`` data.
    * ``repr(Base58)``:  Gives the hex representation of the data.

    *  ``format(Base58,_format)`` Formats the instance according to
    ``_format``:

        * ``"btc"``: prefixed with ``0x80``. Yields a valid btc address
        * ``"wif"``: prefixed with ``0x00``. Yields a valid wif key
        * ``"bts"``: prefixed with ``BTS``
        * etc.

    """

    def __init__(self, data, prefix=0x41):
        self._prefix = prefix
        if isinstance(data, str) and data[0:2].lower() == '0x':
            data = data[2:]
        if isinstance(data, str) and all(c in string.hexdigits for c in data):  # if is hex string
            if len(data) == 42 and data[0:2].lower() == '41':
                self._hex = data[2:]
                self._prefix = 0x41
            elif len(data) == 42 and data[0:2].lower() == 'a0':
                self._hex = data[2:]
                self._prefix = 0xa0
            else:
                self._hex = data[-40:]
        elif isinstance(data, str):  # if is base58 string
            if data[0] == "T":
                self._hex = base58CheckDecode(data)
                self._prefix = 0x41
            elif data[0:2] == "27":
                self._hex = base58CheckDecode(data)
                self._prefix = 0xa0
            else:
                raise ValueError("Error loading Base58 object")
        elif isinstance(data, bytes):  # if is bytes
            if len(data) == 21 and data[0] == b'\x41':
                self._hex = hexlify(data[1:]).decode('ascii')
                self._prefix = 0x41
            elif len(data) == 21 and data[0] == b'\xa0':
                self._hex = hexlify(data[1:]).decode('ascii')
                self._prefix = 0xa0
            elif len(data) == 20:
                self._hex = hexlify(data).decode('ascii')
        else:
            raise ValueError("Error loading Base58 object")
        

    def __format__(self, _format="TRON"):
        """ Format output according to argument _format (wif,btc,...)

            :param str _format: Format to use
            :return: formatted data according to _format
            :rtype: str

        """
        if _format.upper() == "WIF":
            return base58CheckEncode(0x80, self._hex)
        elif _format.upper() == "ENCWIF":
            return base58encode(self._hex)
        elif _format.upper() == "BTC":
            return base58CheckEncode(0x00, self._hex)
        elif _format.upper() == "TRON":
            return base58CheckEncode(self._prefix, self._hex)
        else:
            log.warn("Format %s unkown. You've been warned!\n" % _format)
            return _format.upper() + str(self)

    def __repr__(self):
        """ Returns hex value of object

            :return: Hex string of instance's data
            :rtype: hex string
        """
        return self._hex

    def __str__(self):
        """ Return base58CheckEncoded string of data

            :return: Base58 encoded data
            :rtype: str
        """
        return self.__format__()

    def __bytes__(self):
        """ Return raw bytes

            :return: Raw bytes of instance
            :rtype: bytes

        """
        return unhexlify(self._hex)

    def encode(self):
        return self.__format__()

    def decodeWithPrefix(self):
        return format(self._prefix, 'x') + self._hex

    def decode(self):
        return self._hex


# https://github.com/tochev/python3-cryptocoins/raw/master/cryptocoins/base58.py
BASE58_ALPHABET = b"123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"


def base58decode(base58_str):
    base58_text = base58_str.encode('ascii')
    n = 0
    leading_zeroes_count = 0
    for b in base58_text:
        n = n * 58 + BASE58_ALPHABET.find(b)
        if n == 0:
            leading_zeroes_count += 1
    res = bytearray()
    while n >= 256:
        div, mod = divmod(n, 256)
        res.insert(0, mod)
        n = div
    else:
        res.insert(0, n)
    return hexlify(bytearray(1) * leading_zeroes_count + res).decode('ascii')


def base58encode(hexstring):
    byteseq = compat_bytes(hexstring, 'ascii')
    byteseq = unhexlify(byteseq)
    byteseq = compat_bytes(byteseq)

    n = 0
    leading_zeroes_count = 0
    for c in byteseq:
        n = n * 256 + c
        if n == 0:
            leading_zeroes_count += 1
    res = bytearray()
    while n >= 58:
        div, mod = divmod(n, 58)
        res.insert(0, BASE58_ALPHABET[mod])
        n = div
    else:
        res.insert(0, BASE58_ALPHABET[n])

    return (BASE58_ALPHABET[0:1] * leading_zeroes_count + res).decode('ascii')


def ripemd160(s):
    ripemd160 = hashlib.new('ripemd160')
    ripemd160.update(unhexlify(s))
    return ripemd160.digest()


def doublesha256(s):
    return hashlib.sha256(hashlib.sha256(unhexlify(s)).digest()).digest()


def b58encode(v):
    return base58encode(v)


def b58decode(v):
    return base58decode(v)


def base58CheckEncode(version, payload):
    s = ('%.2x' % version) + payload
    checksum = doublesha256(s)[:4]
    result = s + hexlify(checksum).decode('ascii')
    return base58encode(result)


def base58CheckDecode(s):
    s = unhexlify(base58decode(s))
    dec = hexlify(s[:-4]).decode('ascii')
    checksum = doublesha256(dec)[:4]
    assert (s[-4:] == checksum)
    return dec[2:]


def gphBase58CheckEncode(s):
    checksum = ripemd160(s)[:4]
    result = s + hexlify(checksum).decode('ascii')
    return base58encode(result)


def gphBase58CheckDecode(s):
    s = unhexlify(base58decode(s))
    dec = hexlify(s[:-4]).decode('ascii')
    checksum = ripemd160(dec)[:4]
    assert (s[-4:] == checksum)
    return dec


# copy from https://github.com/steemit/steem-python/blob/master/steem/utils.py
def compat_bytes(item, encoding=None):
    """
    This method is required because Python 2.7 `bytes` is simply an alias for `str`. Without this method,
    code execution would look something like:
    class clazz(object):
        def __bytes__(self):
            return bytes(5)
    Python 2.7:
    c = clazz()
    bytes(c)
    >>'<__main__.clazz object at 0x105171a90>'
    In this example, when `bytes(c)` is invoked, the interpreter then calls `str(c)`, and prints the above string.
    the method `__bytes__` is never invoked.
    Python 3.6:
    c = clazz()
    bytes(c)
    >>b'\x00\x00\x00\x00\x00'
    This is the expected and necessary behavior across both platforms.
    w/ compat_bytes method, we will ensure that the correct bytes method is always invoked, avoiding the `str` alias in
    2.7.
    :param item: this is the object who's bytes method needs to be invoked
    :param encoding: optional encoding parameter to handle the Python 3.6 two argument 'bytes' method.
    :return: a bytes object that functions the same across 3.6 and 2.7
    """
    if hasattr(item, '__bytes__'):
        return item.__bytes__()
    else:
        if encoding:
            return bytes(item, encoding)
        else:
            return bytes(item)

