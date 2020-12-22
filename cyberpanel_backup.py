#!/usr/local/CyberCP/bin/python3
import logging
import argparse
from time import time

from Backup import Backup
from Utils import Utils

from StorageProvider import StorageProvider

log_format = "%(asctime)s::%(levelname)s::%(name)s::" \
             "%(lineno)d::%(message)s"
logging.basicConfig(level=logging.DEBUG, format=log_format)
log = logging.getLogger("cyberpanel_backup")
# [website_id, website_name, database_name]
website_list = Utils.get_websites_list()

parser = argparse.ArgumentParser()
parser.add_argument('--noPolicy', action='store_true', dest='no_policy', help='doesnt run repo policies')
parser.add_argument('--check', action='store_true', help='runs full repo check')
parser.add_argument('--debug', action='store_true', help='runs only first vhost')
parser.add_argument('--unlock', action='store_true', help='runs unlock on all hosts first before backups')
parser.add_argument('--unlock-all', action='store_true', dest='unlockAll', help='only runs unlock on all vhosts')
parser.add_argument('--cacheCleanup', action='store_true', dest='cache_cleanup', help='runs cache cleanup on all vhosts')
parser.add_argument('--wasabi', action='store_true', help='sets storage provider to Wasabi instead of B2')
args = parser.parse_args()

debug = False
if args.debug:
    log.info("!!DEBUG MODE!!")
    debug = True

check = False
if args.check:
    log.info("!!CHECK MODE!!")
    check = True

no_policy = False
if args.no_policy:
    log.info("!!NO-POLICY MODE!!")
    no_policy = True

unlock = False
if args.unlock:
    log.info("!!UNLOCK MODE!!")
    unlock = True

unlockAll = False
if args.unlockAll:
    log.info("!!UNLOCK ALL MODE!!")
    unlockAll = True

cache_cleanup = False
if args.cache_cleanup:
    log.info("!!CACHE_CLEANUP MODE!!")
    cache_cleanup = True

wasabi = False
if args.wasabi:
    log.info("!!Setting Storage Provider to Wasabi!!")
    storage_provider = StorageProvider.WASABI
else:
    log.info("!!Setting Storage Provider to Backblaze B2!!")
    storage_provider = StorageProvider.B2

if debug:
    website_list = [website_list[0]]


def start_backups():
    for website in website_list:
        # website_id = website[0]
        vhost = website[1]
        db_name = website[2]
        log.info("Starting backup of: %s to %s..." % (vhost, storage_provider.value))
        job = Backup(vhost, storage_provider, db_name)
        job.start()
        log.info("Completed Backup of: %s to %s..." % (vhost, storage_provider.value))
        print("~~~~~~~~~~")
    print()
    print("########### BACKUPS COMPLETE")
    print()


def run_policies():
    log.info("Running Policies...")
    for website in website_list:
        vhost = website[1]
        job = Backup(vhost, storage_provider, skip_init=True)
        job.policies()


def run_checks():
    log.info("Running Checks...")
    for website in website_list:
        vhost = website[1]
        job = Backup(vhost, storage_provider, skip_init=True)
        job.check()


def run_cache_cleanup():
    log.info("Running Cache Cleanup...")
    for website in website_list:
        vhost = website[1]
        job = Backup(vhost, storage_provider, skip_init=True)
        job.cache_cleanup()


def run_unlock():
    log.info("Running Unlock...")
    for website in website_list:
        vhost = website[1]
        job = Backup(vhost, storage_provider, skip_init=True)
        job.unlock()


if __name__ == '__main__':
    t0 = time()

    if unlockAll:
        run_unlock()
    else:
        if unlock:
            run_unlock()
        if cache_cleanup:
            run_cache_cleanup()

        # run main backups
        start_backups()

        if not no_policy:
            run_policies()

        if check:
            run_checks()

    total = time() - t0
    log.info("~~Script Completed in %s" % total)
