# qBittorrent Auto-Cleanup Script

A Python script that removes torrents from qBittorrent when they meet configurable ratio and seeding-time rules. Use `--dry-run` to review eligible torrents before deleting anything.

## Rules

| Torrent | Deletion condition |
| --- | --- |
| Private | Seeded for at least `MIN_SEED_TIME` days **and** ratio is at least `PRIVATE_RATIO`; **or** seeded for at least `MAX_SEED_TIME` days, regardless of ratio. |
| Public | Ratio is at least `RATIO`, regardless of seeding time. |
| Unknown private status | Skipped; never treated as public. |

The two private-torrent conditions are alternatives: reaching the maximum seeding time does **not** require reaching a minimum ratio. The script uses inclusive thresholds (`>=`). `MIN_SEED_TIME` and `MAX_SEED_TIME` are measured in days.

For example, with the settings below, a private torrent at ratio 0.71 after 30 days qualifies for deletion; after 25 days it does not. A private torrent at ratio 2.0 after 7 days also qualifies. A public torrent at ratio 1.0 qualifies regardless of seeding time.

## Installation

Install the dependencies listed in `requirements.txt`:

```bash
pip install -r requirements.txt
```

The script imports `qbittorrentapi` and `python-dotenv`; include both in `requirements.txt`.

Create a `.env` file alongside `autodel.py`:

```dotenv
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

- `QBIT_HOST`, `PORT`, `USERNAME`, `PASSWORD`: qBittorrent Web API connection details.
- `RATIO`: minimum ratio for deleting a public torrent.
- `PRIVATE_RATIO`: minimum ratio for deleting a private torrent after `MIN_SEED_TIME` days.
- `MIN_SEED_TIME`: minimum seeding days for the private ratio-based rule.
- `MAX_SEED_TIME`: maximum seeding days for private torrents; once reached, delete regardless of ratio.
- `DELETE_FILES`: whether a real deletion also removes downloaded data. Accepted true values are `true`, `1`, and `yes` (case-insensitive); other values are treated as false.

Keep `.env` out of version control because it contains credentials.

## Usage

Preview deletions first:

```bash
python3 autodel.py --dry-run
```

If the candidates look correct, run the deletion:

```bash
python3 autodel.py
```

Dry-run output shows the number of torrents found, **only the eligible torrents** with their private status, ratio, and seeding days, a count of torrents skipped because their private status is unknown, and the total number that would be deleted. It does not print a `KEEP` line for every torrent.

Example output (illustrative):

```text
Found 311 torrents
WOULD DELETE 'Example private torrent': private=True, ratio=0.71, seeding_days=30.2
WOULD DELETE 'Example public torrent': private=False, ratio=1.25, seeding_days=2.0
Skipped 2 torrents with unknown private status
DRY RUN: Would delete 2 torrents
```

A normal run reports the deletion count instead of listing every torrent. With `DELETE_FILES=True`, it removes the downloaded files along with eligible torrents. Set `DELETE_FILES=False` if you want to remove torrent entries without deleting their data.

## Notes

- Enable qBittorrent's Web API and ensure the configured account can delete torrents.
- The script reads the `private` field returned in the torrent list. Torrents whose private status is missing or `None` are skipped for safety.
- Review the dry-run output, especially before running with `DELETE_FILES=True`.
