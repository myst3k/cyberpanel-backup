# **Cyberpanel Incremental Backup Script**

I created this script in order to back up my CyberPanel Websites and Databases to Backblaze B2 since it was unsupported.
I have since added support for Wasabi. I have also had instances where the built-in backups stopped functioning because
the cron job disappeared, so I was a little untrusting of it. Have been running this ever since. I am currently doing
dual backups to Backblaze B2 and Wasabi.

## About

What this script does it go through the database of virtual hosts on cyberpanel, and if there is a virtualhost and a
mysql table associated, it will do a mysqldump to /home/< vhost >/database.sql, then create an encrypted restic
repository on your storage provider, then take a snapshop of the /home/< vhost > directory excluding the log, backup, and
lscache directory. These excludes can be edited in the restic-excludes file. I have also excluded some wordpress plugin
backup files if the end user is doing backups on their own.

## Prerequisites

Make sure the root user has a ~/.my.cnf file configured with a database username/password which can access the sites.

become root (sudo -i)  
edit ~/.my.cnf with these contents, replacing your root password, can be found in /etc/cyberpanel/mysqlPassword

```
[client]
socket=/var/run/mysqld/mysqld.sock
user=root
password=<root password>
```

For Backblaze B2, create an env file: /etc/cyberpanel/.b2_env

```
export B2_ACCOUNT_ID=<account id>
export B2_ACCOUNT_KEY=<account key>
export B2_REPO_NAME=b2:<bucket-name>
```

For Wasabi, create an env file: /etc/cyberpanel/.wasabi_env

```
export WASABI_ACCESS_KEY=<access key>    
export WASABI_SECRET_KEY=<secret key>    
export WASABI_REPO_NAME=s3:<storage region url>/<bucket name>
```

## Usage
```
mkdir /opt/scripts && cd /opt/scripts  
git clone https://github.com/myst3k/cyberpanel-backup.git
```
add a crontab to run every day at 4am using crontab -e
```
0 4 * * * /opt/scripts/cyberpanel_backup/start_cyberpanel_backup.sh
```
if you want to use wasabi, append --wasabi at the end of the cron