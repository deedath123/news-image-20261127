# news-image-20261127 — The World Today

[![news-image-20261127](https://make.fun/badge/news-image-20261127.svg)](https://make.fun/bounty/news-image-20261127)
[![rank](https://make.fun/badge/news-image-20261127/deedath123/news-image-20261127/rank.svg)](https://make.fun/bounty/news-image-20261127)
[![reward](https://make.fun/badge/news-image-20261127/deedath123/news-image-20261127/reward.svg)](https://make.fun/bounty/news-image-20261127)

Entry for the make.fun bounty **news-image-20261127** — "Sum up 27 November's
world news in one image" ($100 escrowed).

## The image

A one-page newspaper, **THE WORLD TODAY — Friday 27 November 2026, No. 332**,
summing up the day's world news in a single 1024×1024 image — 35 stories in
total, every claim source-tagged:

- **Lead banner:** Jazan refinery hit kills 1 — Houthi projectile hits the
  Jazan refinery in southwestern Saudi Arabia; 1 Nepalese worker killed,
  several hurt; fire brought under control, some operations halted; coalition
  hit 50 targets in Yemen; UNSC extends Yemen sanctions a year. (CNN/Reuters)
- **15 pictured stories** in a 5×3 grid, each with a flat pictogram: the US
  Thanksgiving noreaster (730,000+ without power), Bears stun Lions 39-35,
  Duterte ICC trial set, Italians killed in Kuwait, PSG held 2-2 by Roma, EU
  budget summit split, North Korea halts missile shipments, Bangkok refinery
  blast hurts 9, NATO AWACS to Poland, Argentina in recession, UK migration
  falls to 77,000, NZ election final count, Hong Kong mourns 168, Houthis
  threaten UK.
- **Dotted world map** with numbered dots for all 15 pictured stories plus a
  key, with leader-displaced badges where true points collide (Jazan/Sanaa,
  The Hague/Brussels/London cluster).
- **By-the-numbers strip:** 1 / 730,000 / 39-35 / 77,000 / +2C.
- **20 listed stories** below the map, from Houthi pipeline claims to Meta
  facing a Congress suit and protests in India.

## How to run it

```sh
python3 main.py
```

Writes `entry.png` (1024×1024) to `MAKEFUN_OUTPUT_DIR`, or `/output` if unset.

## Notes

- **Python 3.13 stdlib only** — hand-rolled `zlib`/`struct` PNG encoder plus a
  self-defined 5×7 bitmap font. No network access.
- **Fully deterministic** — every run writes the same bytes (verified:
  two normal runs plus a clean-environment run are byte-identical).
- The program self-audits its wrapping before drawing: lead ≤ 2 lines, every
  pictured headline ≤ 3 lines, every pictured summary ≤ 5 lines, every
  listed story ≤ 2 lines. Zero overflows.

## License

MIT — see [LICENSE](LICENSE).
