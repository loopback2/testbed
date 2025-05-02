# Junos BGP Route Snapshot Tool

This Python script automates the collection of BGP peer summaries, received routes, and advertised routes from Juniper devices using NETCONF and PyEZ.

## Features

- 📊 Collects BGP peer summary (state, prefixes, ASN, RIB, etc.)
- 📥 Gathers received routes per peer (with next hops)
- 📤 Gathers advertised routes per peer (with next hops)
- 🧠 Designed for pre/post change snapshots and diff validation
- 🗂 Saves output into organized timestamped files for auditing

## Requirements

- Python 3.6+
- Junos PyEZ (`pip install junos-eznc`)
- jxmlease (`pip install jxmlease`)
- NETCONF enabled on the Junos device

## Usage

1. Update `inventory.yml` with your Junos device info.
2. Run the script:

```bash
python3 main.py