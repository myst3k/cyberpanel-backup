#!/usr/local/CyberCP/bin/python3
from subprocess import run
import zipfile
import sys
import os
import re
import argparse
from time import strftime, time
from pathlib import Path
from MySQLdb import Connection, connect
from Utils import Utils

home = str(Path.home()) + '/'

db: Connection
website_list = Utils.get_websites_list()
main_backup_location = "/opt/superBkups"
backup_time = strftime("%m.%d.%Y_%H-%M-%S")
backup_location: str
skip_images = True

parser = argparse.ArgumentParser()
parser.add_argument('--foo', help='foo help')


def create_main_backup_dir():
    global backup_location
    os.nice(-20)
    backup_location = os.path.join(main_backup_location, backup_time)
    os.makedirs(backup_location)


def get_timestamp() -> str:
    return strftime("%m.%d.%Y_%H-%M-%S")


def do_db_dump(db_name, filepath):
    cmd = "/usr/bin/mysqldump --defaults-file=/root/.my.cnf %s > %s" % (db_name, filepath)
    print(cmd)
    run(cmd, shell=True)


def start_backups():
    for website in website_list:
        timestamp = get_timestamp()
        # website_id = website[0]
        website_name = website[1]
        db_name = website[2]
        if db_name is None:
            continue
        db_tmp = os.path.join(backup_location, "%s-%s.sql" % (website_name, timestamp))
        filename = "backup-%s-%s.zip" % (website_name, timestamp)
        output_path = os.path.join(backup_location, filename)
        print("Starting backup of: %s ..." % website_name)
        source_location = os.path.join("/home", website_name, "public_html")
        os.nice(-20)

        print("Dumping Database for: %s ..." % website_name)
        do_db_dump(db_name, db_tmp)

        print("Creating Archive for: %s ..." % website_name)
        zf = zipfile.ZipFile(output_path, "w", zipfile.ZIP_DEFLATED)
        for dirname, subdirs, files in os.walk(source_location):
            if skip_images:
                pathname = os.path.relpath(dirname, source_location)
                if re.match("^wp-content/uploads/\\d{4}", pathname):
                    print("Skipping %s ..." % pathname)
                    continue
            zf.write(dirname, os.path.relpath(dirname, source_location))
            for filename in files:
                file_path = os.path.join(dirname, filename)
                zf.write(file_path, os.path.relpath(file_path, source_location))
        zf.write(db_tmp, os.path.relpath(db_tmp, backup_location))
        zf.close()
        # cleanup temp db dump
        os.remove(db_tmp)
        os.nice(0)
        print("Completed: %s ..." % website_name)
        print("~~~~~~~~~~")
        # print("id: %s : vhost: %s : db: %s" % (website_id, website_name, db_name))
        sys.exit()


if __name__ == '__main__':
    t0 = time()
    create_main_backup_dir()
    start_backups()
    total = time() - t0
    print("~~Script Completed in %s" % total)
