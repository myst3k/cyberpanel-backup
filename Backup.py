import logging
import os
import shlex
import shutil
import subprocess
import sys
from pathlib import Path
from subprocess import run, CalledProcessError
from typing import Optional

from Utils import Utils
from StorageProvider import StorageProvider


class Backup:
    def __init__(self, vhost: str, storageProvider: StorageProvider, db_name: Optional[str] = None, skip_init: Optional[bool] = False):
        self.log = logging.getLogger("cyberpanel_backup.Backup")
        self.vhost = vhost
        self.backup_path = Path("/home", vhost)
        self.__init_repository_url()
        self.incremental_config_dir = Path("/home/cyberpanel/incremental_config")
        self.restic_excludes_file = "/opt/scripts/restic-excludes"
        self.restic_retention_options = "--prune --keep-daily 30 --keep-weekly 5 --keep-monthly 12 --keep-yearly 1"
        self.repo_passwd_file = Path(self.incremental_config_dir, "%s_pwd" % vhost)
        if not skip_init:
            self.db_name = db_name
            self.db_backup_path = Path(self.backup_path, "db_backup")
            self.db_backup_filename = "database.sql"
            self.db_backup_file = Path(self.backup_path, self.db_backup_filename)
            self.__init_config_dir()
            self.__init_password()
            self.__init_repo()
            self.__init_db_backup_path()

    def start(self):
        self.backup_db()
        self.backup_files()

    def __init_repository_url(self):
        if os.getenv("B2_REPO_NAME") is not None:
            b2_repo_name = os.getenv("B2_REPO_NAME")
            self.b2_path = f"{b2_repo_name}:{self.vhost}"
        else:
            self.log.error("Please set env variable B2_REPO_NAME with restic b2 url and bucket e.g. b2:<bucket_name>")
            sys.exit(1)

    def __init_config_dir(self):
        if not self.incremental_config_dir.exists():
            self.log.info(f"{self.incremental_config_dir} doesn't exist, creating...")
            self.incremental_config_dir.mkdir()
            shutil.chown(self.incremental_config_dir, "cyberpanel", "cyberpanel")

    def __init_password(self):
        if not self.repo_passwd_file.exists():
            self.log.info("Password file doesn't exist, creating...")
            fd = open(self.repo_passwd_file, "w")
            fd.write(Utils.generate_repo_password())
            fd.close()

    def __init_repo(self):
        cmd = f"/usr/bin/restic -q --repo {self.b2_path} --password-file {self.repo_passwd_file} cat config"
        cmd_split = shlex.split(cmd)
        try:
            run(cmd_split, check=True, stdout=subprocess.DEVNULL)
        except CalledProcessError:
            self.log.warning("Repository Not Found or Does Not Exist, attempting to create repository...")
            cmd = f"/usr/bin/restic -q --repo {self.b2_path} --password-file {self.repo_passwd_file} init"
            cmd_split = shlex.split(cmd)
            try:
                run(cmd_split, check=True)
            except CalledProcessError as e:
                self.log.error("Unable to create repository...")
                self.log.error(e)
                # TODO: add moar error handling

    def __init_db_backup_path(self):
        if not self.db_backup_path.exists():
            self.db_backup_path.mkdir()

    def backup_db(self):
        cmd = f"/usr/bin/mysqldump --defaults-file=/root/.my.cnf {self.db_name} > {self.db_backup_file}"
        try:
            self.log.info(f"Backing up database to: {self.db_backup_file}")
            run(cmd, check=True, shell=True)
        except CalledProcessError as e:
            self.log.error("Backup up DB didnt work")
            self.log.error(e)
            # TODO: add moar error handling

    def backup_files(self):
        cmd = "/usr/bin/restic --repo %s --password-file %s backup %s --exclude-file=%s" % (
            self.b2_path, self.repo_passwd_file, self.backup_path, self.restic_excludes_file)
        cmd_split = shlex.split(cmd)
        try:
            self.log.info(f"Backing up files: {self.backup_path}")
            run(cmd_split, check=True)
        except CalledProcessError as e:
            self.log.error("Backing up files didnt work!")
            self.log.error(e)
            # TODO: add moar error handling

    def policies(self):
        self.log.info("Running Repo Retention Policies...")
        cmd = f"/usr/bin/restic --repo {self.b2_path} --password-file {self.repo_passwd_file} forget {self.restic_retention_options} "
        cmd_split = shlex.split(cmd)
        try:
            run(cmd_split, check=True)
        except CalledProcessError as e:
            self.log.error("Error running retention policies...")
            self.log.error(e)
            # TODO: add moar error handling

    def check(self):
        self.log.info("Running Repo Check...")
        cmd = f"/usr/bin/restic --repo {self.b2_path} --password-file {self.repo_passwd_file} check"
        cmd_split = shlex.split(cmd)
        try:
            run(cmd_split, check=True)
        except CalledProcessError as e:
            self.log.error("Error running check...")
            self.log.error(e)
            # TODO: add moar error handling

    def cache_cleanup(self):
        self.log.info("Running Cache Cleanup...")
        cmd = f"/usr/bin/restic --repo {self.b2_path} --password-file {self.repo_passwd_file} cache --cleanup"
        cmd_split = shlex.split(cmd)
        try:
            run(cmd_split, check=True)
        except CalledProcessError as e:
            self.log.error("Error Cache Cleanup...")
            self.log.error(e)
            # TODO: add moar error handling

    def cleanup(self):
        self.log.info("Running Cleanup...")
        if self.vhost is not None:
            if self.db_backup_path.exists() and self.db_backup_path.is_dir():
                self.log.info(f"Cleaning up database backup: {self.db_backup_path}")
                shutil.rmtree(self.db_backup_path)

    def unlock(self):
        self.log.info("Running Unlock...")
        cmd = f"/usr/bin/restic --repo {self.b2_path} --password-file {self.repo_passwd_file} unlock"
        cmd_split = shlex.split(cmd)
        try:
            run(cmd_split, check=True)
        except CalledProcessError as e:
            self.log.error("Error unlock...")
            self.log.error(e)
            # TODO: add moar error handling
