#!/usr/local/CyberCP/bin/python3
import logging
import argparse
from time import time

from Backup import Backup
from Utils import Utils

log_format = "%(asctime)s::%(levelname)s::%(name)s::" \
             "%(lineno)d::%(message)s"
logging.basicConfig(level=logging.DEBUG, format=log_format)
log = logging.getLogger("b2_backup")
# [website_id, website_name, database_name]
website_list = Utils.get_websites_list()

parser = argparse.ArgumentParser()
parser.add_argument('--nocheck', action='store_true', help='doesnt run policies and checks')
parser.add_argument('--debug', action='store_true', help='runs only first vhost')
args = parser.parse_args()

debug = False
if args.debug:
    log.info("!!DEBUG MODE!!")
    debug = True

nocheck = False
if args.nocheck:
    log.info("!!NOCHECK MODE!!")
    nocheck = True

if debug:
    website_list = [website_list[0]]
    # single = []
    # for website in website_list:
    #     vhost = website[1]
    #     if "example.com" in vhost:
    #         print("found it!")
    #         website_list = [website]



def start_backups():
    for website in website_list:
        # website_id = website[0]
        vhost = website[1]
        db_name = website[2]
        if db_name is None:
            continue
        log.info("Starting backup of: %s ..." % vhost)
        backup = Backup(vhost, db_name)
        backup.start()
        log.info("Completed Backup of: %s ..." % vhost)
        print("~~~~~~~~~~")
    print()
    print("########### BACKUPS COMPLETE")
    print()


def run_policies_and_checks():
    log.info("Running Policies and Checks...")
    for website in website_list:
        vhost = website[1]
        job = Backup(vhost, skip_init=True)
        job.policies()
        job.check()


if __name__ == '__main__':
    t0 = time()

    start_backups()
    if not nocheck:
        run_policies_and_checks()

    total = time() - t0
    log.info("~~Script Completed in %s" % total)
