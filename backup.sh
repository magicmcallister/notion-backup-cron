#!/bin/bash

set -a
. /home/sr/magicmcallister/notion-backup-cron/.env
set +a
python3 /home/sr/magicmcallister/notion-backup-cron/notion_backup.py
