from base58 import Base58
from binascii import hexlify, unhexlify

def hex_to_string(hex_string):
    return bytearray.fromhex(hex_string).decode('utf-8')


def hex_to_int(hex_string):
    return int(hex_string, 16)


def getSolStrByDataSlot(hex_string, slot):
    return hex_string[64 * slot: 64 * (slot + 1)]


def getInt(hex_string, slot=0):
    return hex_to_int(getSolStrByDataSlot(hex_string, slot))


def getString(hex_string, slot=0):
    return hex_to_string(getSolStrByDataSlot(hex_string, slot))


def address_to_bytes32(address):
    return "000000000000000000000000" + Base58(address, prefix=0x41).decode()


def bytes32_to_address(bytes32):
    return Base58(bytes32[24:], prefix=0x41).encode()


def int_to_bytes32_str(num):
    return hexlify((num).to_bytes(32, byteorder='big')).decode('ascii')