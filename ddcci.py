import smbus

MAGIC_1   = 0x51
MAGIC_2   = 0x80
#MAGIC_XOR = 0x50

#DDCCI_COMMAND_READ  = 0x01 # @TODO: not implemented
#DDCCI_REPLY_READ    = 0x02 # @TODO: not implemented
DDCCI_COMMAND_WRITE  = 0x03

DEFAULT_DDCCI_ADDR = 0x37

def ddcci_payload(addr, data):
    payload = [MAGIC_1, MAGIC_2 | len(data)]
    xor = addr << 1
    payload.extend(data)

    for x in payload: xor ^= x

    payload.append(xor)

    return payload

def ddcci_writectrl(bus, addr, ctrl, value):
    payload = ddcci_payload(addr, [DDCCI_COMMAND_WRITE, ctrl, (value >> 8) & 255, value & 255])
    bus.write_i2c_block_data(addr, payload[0], payload[1:])

def ddcci_set_brightness(bus, value, addr=DEFAULT_DDCCI_ADDR):
    if isinstance(bus, int):
        bus = smbus.SMBus(bus)

    ddcci_writectrl(bus, addr, 0x10, value)

def ddcci_set_contrast(bus, value, addr=DEFAULT_DDCCI_ADDR):
    if isinstance(bus, int):
        bus = smbus.SMBus(bus)

    ddcci_writectrl(bus, addr, 0x12, value)

if __name__ == '__main__':
    import time
    # You can obtain your bus id using `i2cdetect -l` or `ddccontrol -p`
    ddcci_set_brightness(8, 69)
    time.sleep(0.08) # A little bit of delay between writes (80ms is known to be enough)
    ddcci_set_contrast(8, 42)
