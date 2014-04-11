import smbus
import time
from functools import wraps

MAGIC_1   = 0x51
MAGIC_2   = 0x80

DDCCI_COMMAND_READ  = 0x01
DDCCI_REPLY_READ    = 0x02
DDCCI_COMMAND_WRITE = 0x03

DEFAULT_DDCCI_ADDR = 0x37

READ_DELAY = WRITE_DELAY = 0.06

def throttle(delay):
    """usage:
       @throttle
       def func( ... ): ... (defaults to WRITE_DELAY)

       @throttle(3)
       def func( ... ): ... (delay provided explicitly)"""

    def throttle_deco(func):
        @wraps(func)
        def wrapped(*args, **kwargs):
            if hasattr(func, 'last_execution') and time.time() - func.last_execution < delay:
                time.sleep(delay - (time.time() - func.last_execution))

            r = func(*args, **kwargs)
            func.last_execution = time.time()
            return r

        return wrapped

    if callable(delay): # @throttle invocation
        func, delay = delay, WRITE_DELAY
        return throttle_deco(func)
    else: # @throttle(...) invocation
        return throttle_deco

class ReadException(Exception): pass

class DDCCIDevice(object):
    bus = None

    def __init__(self, bus, address=DEFAULT_DDCCI_ADDR):
        if isinstance(bus, smbus.SMBus):
            self.bus = bus
        else:
            self.bus = smbus.SMBus(bus)

        self.address = address

    def write(self, ctrl, value):
        payload = self.prepare_payload(self.address,
                [DDCCI_COMMAND_WRITE, ctrl, (value>>8) & 255, value & 255])

        self.write_payload(payload)

    def read(self, ctrl, extended=False):
        payload = self.prepare_payload(self.address,
                [DDCCI_COMMAND_READ, ctrl])

        self.write_payload(payload)

        time.sleep(READ_DELAY)

        if self.bus.read_byte(self.address) != self.address << 1:
            raise ReadException("ACK invalid")

        data_length = self.bus.read_byte(self.address) & ~MAGIC_2
        data = [self.bus.read_byte(self.address) for n in xrange(data_length)]
        checksum = self.bus.read_byte(self.address)

        xor = (self.address << 1 | 1) ^ MAGIC_1 ^ (MAGIC_2 | len(data))
        for n in data: xor ^= n

        if xor != checksum:
            raise ReadException("Invalid checksum")

        if data[0] != DDCCI_REPLY_READ:
            raise ReadException("Invalid response type")

        if data[2] != ctrl:
            raise ReadException("Received data for unrequested control")

        max_value = data[4] << 8 | data[5]
        value = data[6] << 8 | data[7]

        if extended:
            return value, max_value
        else:
            return value

    def control_property(ctrl):
        """helper for adding control properties (see demo)"""
        return property(lambda s: s.read(ctrl),
                        lambda s, v: s.write(ctrl, v))

    brightness = control_property(0x10)
    contrast = control_property(0x12)

    @throttle
    def write_payload(self, payload):
        self.bus.write_i2c_block_data(self.address, payload[0], payload[1:])

    def prepare_payload(self, addr, data):
        payload = [MAGIC_1, MAGIC_2 | len(data)]

        if data[0] == DDCCI_COMMAND_READ:
            xor = addr << 1 | 1;
        else:
            xor = addr << 1

        payload.extend(data)

        for x in payload: xor ^= x

        payload.append(xor)

        return payload

if __name__ == '__main__':
    # You can obtain your bus id using `i2cdetect -l` or `ddccontrol -p`
    d = DDCCIDevice(8)

    print 'Demo 1 ...'
    d.write(0x10, 42)

    time.sleep(1)

    print 'Demo 2 ...'
    d.brightness = 12
    d.contrast = 34

    time.sleep(1)

    print 'Demo 3 ...'
    d.write(0x12, 69)

    print 'Brightness: %d, Contrast: %d' % (d.brightness, d.contrast)
    print 'Max brightness: %d, Max contrast: %d' % (d.read(0x10, True)[1], d.read(0x12, True)[1])
