#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Simple CLI interface to python-ddcci
"""

import ddcci
import sys
import argparse

#@TODO: store global controls table in ddcci module
controls = {'brightness': 0x10, 'contrast': 0x12}

class Actions: GET, SET, SET_RELATIVE = range(3)

def attr_change(value):
    """Special argparse type used for relative value store"""
    v = value.strip()

    if v.startswith('+'):
        return [Actions.SET_RELATIVE,  int(v[1:])]
    if v.strip().startswith('-'):
        return [Actions.SET_RELATIVE, -int(v[1:])]

    return [Actions.SET, int(v)]

def main(argv):
    parser = argparse.ArgumentParser(description=__doc__, epilog="""example usage:
    increase brightness by 10:
        %(prog)s --brightness +10

    set contrast to 50:
        %(prog)s --contrast 50

    get brightness and process it in shell script:
        echo "Your current brightness is: $(%(prog)s --raw --brightness)" """,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    
    parser.add_argument('-b', '--bus', type=int, default=7, help='bus number')
    parser.add_argument('-d', '--device', metavar='DEV', type=int, default=ddcci.DEFAULT_DDCCI_ADDR, help='device address')

    for p in controls.keys():
        parser.add_argument('--%s' % p, metavar='VALUE', nargs='?', type=attr_change, const=[Actions.GET], help='fetch or change "%s" control' % p)

    parser.add_argument('--raw', action='store_true', default=False, help='return raw values to stdout when fetching controls (default: disabled)')
    args = parser.parse_args(argv[1:])

    props = dict((p, getattr(args, p)) for p in controls.keys() if getattr(args, p))
    
    if not props:
        parser.print_usage()
        return

    device = ddcci.DDCCIDevice(args.bus, args.device)

    for p, v in props.items():
        control_id = controls[p]

        if v[0] is Actions.GET:
            if args.raw:
                print device.read(control_id)
            else:
                print '%s=%d' % (p, device.read(control_id))
        elif v[0] is Actions.SET:
            device.write(control_id, v[1])
        elif v[0] is Actions.SET_RELATIVE:
            device.write(control_id, device.read(control_id) + v[1])

if __name__ == '__main__':
    main(sys.argv)
