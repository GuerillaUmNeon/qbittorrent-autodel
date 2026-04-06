import qbittorrentapi
from datetime import timedelta
from dotenv import load_dotenv
import argparse
import os

load_dotenv()

QBIT_HOST = os.getenv("QBIT_HOST")
PORT = os.getenv("PORT")
USERNAME = os.getenv("USERNAME")
PASSWORD = os.getenv("PASSWORD")
RATIO = float(os.getenv("RATIO"))
PRIVATE_RATIO = float(os.getenv("PRIVATE_RATIO"))
MIN_SEED_TIME=int(os.getenv("MIN_SEED_TIME"))
MAX_SEED_TIME=int(os.getenv("MAX_SEED_TIME"))

# 7 et 30 jours en secondes
SEEDING_7_DAYS  = int(timedelta(days=MIN_SEED_TIME).total_seconds())
SEEDING_30_DAYS = int(timedelta(days=MAX_SEED_TIME).total_seconds())

parser = argparse.ArgumentParser()
parser.add_argument('--dry-run', action='store_true', help='Preview deletions without removing torrents')
args = parser.parse_args()

client = qbittorrentapi.Client(
    host=f'{QBIT_HOST}:{PORT}',
    username=USERNAME,
    password=PASSWORD
)

try:
    client.auth_log_in()
except qbittorrentapi.LoginFailed:
    print("Login failed - check credentials")
    exit(1)

torrents = client.torrents_info()
to_delete = []
details = []

for torrent in torrents:
    seeding_time = getattr(torrent, "seeding_time", 0)  # 0 si absent
    private = getattr(torrent, "private", False)  # suppose une version ≥5.0
    reason = []

    if private:
        if torrent.ratio > PRIVATE_RATIO and seeding_time >= SEEDING_7_DAYS:
            reason.append(f"ratio {torrent.ratio:.2f} > 2 and seeding {seeding_time // 86400} days")
        elif seeding_time >= SEEDING_30_DAYS and ratio >= RATIO:
            reason.append(f"seeding {seeding_time // 86400} days >= 30")
    else:
        if torrent.ratio > RATIO:
            reason.append(f"ratio {torrent.ratio:.2f} > 1")

    if reason:
        to_delete.append(torrent.hash)
        details.append(f"{torrent.name} ({'private' if private else 'public'}): {', '.join(reason)}")

if to_delete:
    if args.dry_run:
        print(f"DRY RUN: Would delete {len(details)} torrents:")
        for detail in details:
            print(f"  - {detail}")
    else:
        client.torrents_delete(delete_files=True, torrent_hashes=to_delete)
        print(f"Deleted {len(to_delete)} torrents")
else:
    print("No torrents to delete")
