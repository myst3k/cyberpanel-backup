# **Cyberpanel Incremental Backup Script**

I created this script in order to back up my CyberPanel Websites and Databases to Backblaze B2 since it was unsupported.
I have since added support for Wasabi. I have also had instances where the built-in backups stopped functioning in the
cron job, so I was a little untrusting of it. Have been running this ever since.

## Prerequisites
Make sure the root user has a ~/.my.cnf file configured with a database username/password which can access the sites.

For Backblaze B2, create an env file: /etc/cyberpanel/.b2_env
`export B2_ACCOUNT_ID=<account id>
export B2_ACCOUNT_KEY=<account key>
export B2_REPO_NAME=b2:<bucket-name>`

For Wasabi, create an env file: /etc/cyberpanel/.wasabi_env
`export WASABI_ACCESS_KEY=<access key>
export WASABI_SECRET_KEY=<secret key>
export WASABI_REPO_NAME=s3:https://<storage region url>/<bucket name>`



## Usage

mkdir /opt/scripts
git clone 