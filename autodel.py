import argparse
import os
from datetime import timedelta

import qbittorrentapi
from dotenv import load_dotenv

load_dotenv()

RATIO = float(os.environ["RATIO"])
PRIVATE_RATIO = float(os.environ["PRIVATE_RATIO"])
MIN_SEED_DAYS = int(os.environ["MIN_SEED_TIME"])
MAX_SEED_DAYS = int(os.environ["MAX_SEED_TIME"])
DELETE_FILES = os.getenv("DELETE_FILES", "false").strip().lower() in {"true", "1", "yes"}

MIN_SEED_SECONDS = int(timedelta(days=MIN_SEED_DAYS).total_seconds())
MAX_SEED_SECONDS = int(timedelta(days=MAX_SEED_DAYS).total_seconds())

parser = argparse.ArgumentParser()
parser.add_argument(
    "--dry-run",
    action="store_true",
    help="Preview deletions without removing torrents or files",
)
args = parser.parse_args()

client = qbittorrentapi.Client(
    host=f'{os.environ["QBIT_HOST"]}:{os.environ["PORT"]}',
    username=os.environ["USERNAME"],
    password=os.environ["PASSWORD"],
)

try:
    client.auth_log_in()
except qbittorrentapi.LoginFailed:
    raise SystemExit("Login failed - check credentials")

torrents = client.torrents_info()
print(f"Found {len(torrents)} torrents")

to_delete = []
skipped = 0

for torrent in torrents:
    if "private" not in torrent or torrent.private is None:
        skipped += 1
        continue

    seeding_time = torrent.seeding_time
    current_ratio = torrent.ratio

    if torrent.private:
        eligible = (
            (seeding_time >= MIN_SEED_SECONDS and current_ratio >= PRIVATE_RATIO)
            or seeding_time >= MAX_SEED_SECONDS
        )
    else:
        eligible = current_ratio >= RATIO

    if eligible:
        to_delete.append(torrent.hash)
        if args.dry_run:
            print(
                f"WOULD DELETE {torrent.name!r}: "
                f"private={torrent.private}, ratio={current_ratio:.2f}, "
                f"seeding_days={seeding_time / 86400:.1f}"
            )

if skipped:
    print(f"Skipped {skipped} torrents with unknown private status")

if args.dry_run:
    print(f"DRY RUN: Would delete {len(to_delete)} torrents")
elif to_delete:
    client.torrents_delete(
        torrent_hashes=to_delete,
        delete_files=DELETE_FILES,
    )
    print(f"Deleted {len(to_delete)} torrents (delete_files={DELETE_FILES})")
else:
    print("No torrents meet the deletion rules")
