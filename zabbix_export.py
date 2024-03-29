#!/usr/bin/env python3

from zabbix_utils import ZabbixAPI
from zipfile import ZipFile as zip
import logging as log
import sys, os, argparse, time, atexit


ZBX_OBJS = {
    'hosts': {
        'zbx_obj': 'host',
        'zbx_obj_id': 'hostid',
        'zbx_exp_opt': 'hosts'
    },
    'hostgroups': {
        'zbx_obj': 'hostgroup',
        'zbx_obj_id': 'groupid',
        'zbx_exp_opt': 'host_groups'
    },
    'maps': {
        'zbx_obj': 'map',
        'zbx_obj_id': 'sysmapid',
        'zbx_exp_opt': 'maps'
    },
    'images': {
        'zbx_obj': 'image',
        'zbx_obj_id': 'imageid',
        'zbx_exp_opt': 'images'
    },
    'mediatypes': {
        'zbx_obj': 'mediatype',
        'zbx_obj_id': 'mediatypeid',
        'zbx_exp_opt': 'mediaTypes'
    },
    'templategroups': {
        'zbx_obj': 'templategroup',
        'zbx_obj_id': 'groupid',
        'zbx_exp_opt': 'template_groups'
    },
    'templates': {
        'zbx_obj': 'template',
        'zbx_obj_id': 'templateid',
        'zbx_exp_opt': 'templates'
    },
}

zip_files = []

@atexit.register
def deleteItermFiles():
    for _file in zip_files:
        if os.path.exists(_file):
            os.remove(_file)


def full_path (relative_path: str) -> str:
    P_WD = os.path.dirname(__file__)
    return os.path.join(P_WD, relative_path)

def mkdir(path: str) -> None:
    if not os.path.isdir(path):
        os.makedirs(path)
        log.info(f"Created directory '{path}'")


def readConfig(filepath: str, delim: str = '=') -> dict:
    try:
        with open(filepath) as f:
            l = [line.split(delim) for ln in f.readlines() \
                 if (line := ln.strip()) and not line.startswith('#')]
            return {key.strip().strip('"'): value.strip().strip('"') for key, value in l}
    except FileNotFoundError as e:
        log.error(e)
        sys.exit(1)


def export(zbx_api: object,
           zbx_obj: str,
           zbx_obj_id: str,
           zbx_exp_opt,
           format: str = 'yaml') -> str:
    """
    Export configuration data as a serialized string.

    Args:
       zbx_api:     the ZabbixAPI object
       zbx_obj:     the zabbix objects type
       zbx_obj_id:  the zabbix object's id name
       zbx_exp_opt: the zabbix object's output option
       format:      the serialized output format; possible values: yaml, json, xml

    Returns:
       The serialized string, or None in case of errors

    """

    try:
       # Retrieve the objects
       obj_api = eval('api.' + zbx_obj)
       obj_ids = obj_api.get( output=[zbx_obj_id] )
       # flatten the ids in a list
       list_ids = [ i[zbx_obj_id] for i in obj_ids ]

       return api.configuration.export(
           options={
             zbx_exp_opt: list_ids
           },
           format=format, prettyprint=True )
    except Exception as e:
       log.error(f"Failed to export '{zbx_obj}' objects")
       log.error(e)


def parse_args():
    lTypes = ['all'] + list(ZBX_OBJS.keys())
    types = ', '.join(lTypes)

    parser = argparse.ArgumentParser(description =
        """
        Export configurations from Zabbix server.
        """)
    parser.add_argument('-d', '--dir', action = "store",
        help = "Directory where to save the exported configuration (default: current dir)",
        default = '.')
    parser.add_argument('-c', '--config', action = "store",
        help = "The configuration file, relative to the program's location (default: %(default)s)",
        default = 'zbx_config.ini')
    parser.add_argument('-t', '--types', nargs = '+', choices = lTypes,
        help = f"Which type(s) of configuration to export. Possible values: {types}. Default: %(default)s",
        default = ['hosts'])
    parser.add_argument('-f', '--format', choices = ['yaml', 'xml', 'json'],
        help = "The output format. Default: %(default)s",
        default = 'yaml')
    parser.add_argument('-z', '--zip', action = 'store_true',
        help = "Compress the exported configutation data")
    parser.add_argument('-v', '--verbose', action = 'store_true',
        help = "Enable debug mode")

    return parser.parse_args()



# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#           ~~+~~ MAIN ~~+~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
if __name__ == "__main__":


    args = parse_args()

    log_lvl = log.DEBUG if args.verbose else log.INFO

    log.basicConfig(level=log_lvl, format='%(asctime)s :: %(levelname)s :: %(message)s')

    ZABBIX_AUTH = readConfig(full_path(args.config))
    # Create an instance of the ZabbixAPI class with the specified authentication details
    if 'token' not in ZABBIX_AUTH:
        log.error("No authentication token is provided in configuration file")
        sys.exit(1)
    api = ZabbixAPI(**ZABBIX_AUTH)

    mkdir(args.dir)

    if 'all' in args.types:
        args.types = list(ZBX_OBJS.keys())

    # Collect the exported configuration data
    timestamp = time.strftime("%y%m%d%H%M")
    tmstmp = '_' + timestamp if not args.zip else ''
    for _type in args.types:
        data = export(api, **ZBX_OBJS[_type], format = args.format)
        if data is not None:
            output_file = os.path.join(args.dir, f"zbx_{_type}{tmstmp}.{args.format}")
            with open(output_file, 'w') as f:
                f.write(data)
            if args.zip:
                zip_files.append(output_file)
            else:
                log.info(f"Written configuration file: {output_file}")

    # Compress the exported files
    if len(zip_files):
        zipfile = os.path.join(args.dir, f"zbx_export_{timestamp}.zip")
        with zip(zipfile, mode='w') as archive:
            for f in zip_files:
                archive.write(f)
        log.info(f"Compressed configuration file: {zipfile}")



