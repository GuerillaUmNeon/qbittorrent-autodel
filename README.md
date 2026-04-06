
# qBittorrent Auto‑Cleanup Script

A small Python script to automatically delete torrents from qBittorrent that meet certain seeding‑ratio and seeding‑time conditions.

## What it does

- Connects to qBittorrent via the Web API using environment variables.

- Collects all torrents and checks:

  -   If the ratio is above a configured threshold.

    - If the seeding time is above 7 days or 30 days (configurable).

    - Special rules for private vs public torrents.

- Lists torrents that would be deleted with reasons.

- Actually deletes them only when --dry-run is not passed.


## Installation

Install the required package:

```bash
pip install -r requirements.txt
```
    
Create a .env file in the same directory as the script:

```bash
QBIT_HOST=localhost
PORT=8080
USERNAME=your_username
PASSWORD=your_password

RATIO=1.0
PRIVATE_RATIO=2.0

MIN_SEED_TIME=7      
MAX_SEED_TIME=30 
DELETE_FILES=True
```

Values: 
 - DELETE_FILES=True → deletes files with the torrent
 - RATIO → ratio threshold for public torrents.
 - PRIVATE_RATIO → higher ratio threshold for private torrents.
 - MIN_SEED_TIME → 7 days threshold (configurable).
 - MAX_SEED_TIME → 30 days threshold (configurable, for stalled torrents not meeting MIN_SEED_TIME and RATIO requirements).
## Usage

```javascript
# Dry run: show what would be deleted, without removing anything
python3 autodel.py --dry-run

# Real run: actually delete torrents matching the conditions
python3 autodel.py
```

Output:
```bash
DRY RUN: Would delete 3 torrents:
  - Movie XYZ (private): ratio 2.15 > 2 and seeding 12 days
  - Another torrent (public): ratio 1.25 > 1
  - Long seeded torrent (public): seeding 35 days >= 30
```
## Overview
For each torrent:
- If it is private:
    - Delete if:
        - Ratio > PRIVATE_RATIO and seeding ≥ 7 days, or
        - Seeding ≥ 30 days and ratio ≥ RATIO.

- If it is public:
    - Delete if ratio > RATIO.

In all cases:
- The script prints the torrent name, whether it’s private/public, and the reason.
- In --dry-run mode, only prints; in normal mode, calls torrents_delete(delete_files=True).
## Notes

Notes

- Make sure qBittorrent is running and reachable at the configured QBIT_HOST:PORT.

- Always test first with --dry-run to avoid accidental deletions.

- This script assumes:

    - qBittorrent Web API is enabled.

    - You have write/delete permissions for torrents.