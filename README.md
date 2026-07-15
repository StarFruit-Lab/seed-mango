# Seed Mango (FC-30): Open-Source 30:1 Metal Cycloidal Actuator

**The first "Seed" from [StarFruit Lab](https://github.com/StarFruit-Lab). A metal cycloidal actuator for embodied AI, humanoids, and legged robots — Berkeley Humanoid Lite 6512-class joints and beyond.**

👉 [Join the Waitlist](https://starfruit-actuator.subscribepage.io) · 👉 [YouTube](https://www.youtube.com/@StarFruitRobotics)

[![Stage](https://img.shields.io/badge/Stage-Alpha-orange)](#project-status)
[![Reduction](https://img.shields.io/badge/Reduction-30%3A1-blue)]()
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)

---

## Why Seed Mango?

Most open humanoid joints are either **fragile 3D-printed gearboxes** or **$500+ industrial servos**. Seed Mango (model **FC-30**) targets the middle: a **factory-built, full-metal 30:1 cycloidal drive** with an integrated FOC driver and a Python SDK — priced for researchers and makers.

> **Honest positioning:** This is a **30:1 cycloidal position actuator**, not a bare quasi-direct-drive module. It is designed as a **6512-class drop-in upgrade path** for Berkeley Humanoid Lite kinematics.

---

## Project status

| Milestone | State | Notes |
|-----------|-------|-------|
| USB connect + diagnose | ✅ Available | `bringup.py`, `SeedMangoSDK.py` |
| Auto calibration | ✅ Available | `auto_calibrate()` |
| Encoder verification | ✅ Available | `monitor()`, manual back-drive |
| Torque / efficiency bench data | 🔄 In progress | See [test results](docs/test_results_v1.0.md) _(coming)_ |
| STEP / mechanical CAD | ⏳ Planned | `mechanical/` |
| Datasheet PDF | ⏳ Planned | |

**Current stage: Alpha** — safe to connect, calibrate, and run low-angle bench motion. Spec numbers below marked **TBD** will be updated from bench logs before Beta / v1.0.

---

## Specifications (engineering truth)

> Do **not** treat marketing estimates as tested specs. Values marked **(calc)** are theoretical. Values marked **TBD** are awaiting bench sign-off.

| Parameter | Value | Notes |
|-----------|-------|-------|
| Model name | **Seed Mango** / **FC-30** | Same product, marketing vs engineering ID |
| Gearbox | **30:1 metal cycloidal** | 30 teeth / 31 pins |
| Motor | **Steadywin 55BM24** (7 pole pairs) | |
| Driver (today) | **MW6010-class FOC**, ODrive **0.5.x** firmware | USB debug + CAN |
| Encoder (today) | **14-bit absolute magnetic (MA732)** | **Single** output-side absolute encoder |
| Continuous torque | **TBD N·m** | Bench test pending |
| Peak torque (~2 s) | **TBD N·m** _(calc ~35)_ | Intermittent; thermal limited |
| Impact torque (<50 ms) | **TBD N·m** _(calc ~45–55)_ | **Not verified** — do not spec until tested |
| Supply voltage | **12–36 V** (rec. **24–36 V**) | See driver limits |
| Weight | **~590 g** | As-built with driver |
| Hollow shaft ID | **6 mm** | Motor through-hole |
| Brake resistor | **2 Ω / ≥50 W** on **EMG–GND** | Required before regen / fast motion |
| Debug | **USB Type-C** (WinUSB, Interface 2) | `odrive==0.5.4` |
| Field bus | **CAN** 500 kbps (default) | Multi-actuator setups |
| Target price | **~$149 USD** | Actuator only, excl. shipping |
| Berkeley Lite 6512 fit | **Target** | STEP + fit check in progress |

### What we do **not** claim (yet)

| Claim | Status |
|-------|--------|
| **75+ Nm peak** | ❌ Not verified — removed from spec until bench signed |
| **12 Nm continuous** | ❌ Not verified — TBD from thermal hold test |
| **Dual absolute encoders** | ❌ Current hardware: **one MA732** |
| **RP2350 custom FOC board** | 🔮 **Roadmap** — today ships with ODrive-compatible MW6010 stack |
| **Quasi-direct-drive (QDD)** | ❌ Use **30:1 cycloidal** — different trade-off than low-ratio QDD |

Full bench log template: [docs/test_results_v1.0.md](docs/test_results_v1.0.md) _(coming)_

---

## Quick start

### Requirements

- Python **3.10+**
- `pip install -r requirements.txt` → pins `odrive==0.5.4`
- [Zadig](https://zadig.akeo.ie): **WinUSB** on **CyberBeast Motor Driver Device (Interface 2)**
- DC supply **24–36 V**, ≥15 A
- USB **data** Type-C cable
- Brake resistor **2 Ω / ≥50 W** on EMG–GND _(before closed-loop / regen tests)_

### Wiring order

1. Power **OFF** → connect XT30 (**verify polarity** — no reverse-polarity protection)
2. Connect brake resistor (EMG–GND)
3. Power **ON**
4. Plug Type-C → run:

```powershell
git clone https://github.com/StarFruit-Lab/seed-mango.git
cd seed-mango
pip install -r requirements.txt
python bringup.py
```

Or in Python:

```python
from SeedMangoSDK import SeedMangoSDK

actuator = SeedMangoSDK(reduction_ratio=-30.0)
actuator.connect()
actuator.diagnose()
actuator.get_encoder_status()
```

📖 **Full guide:** [docs/quickstart.md](docs/quickstart.md) · [docs/wiring.md](docs/wiring.md)

---

## Repository layout

```
seed-mango/
├── README.md
├── LICENSE
├── requirements.txt
├── SeedMangoSDK.py       # Python SDK (ODrive 0.5.x)
├── bringup.py            # Guided connect / diagnose / calibrate
└── docs/
    ├── quickstart.md
    ├── wiring.md
    └── test_results_v1.0.md   # coming
```

---

## Modularity & roadmap

Seed Mango is designed as a **platform**, not a one-off motor:

| Feature | Status |
|---------|--------|
| Swappable motor stators (e.g. 62BM26 / 80BM26) | 🔮 Planned — different torque/speed tiers |
| Active cooling (2510 fan, side vents) | 🔮 Mechanical path reserved |
| Custom RP2350 FOC board | 🔮 Roadmap — current units: MW6010 + ODrive 0.5.x |
| STEP / STL mechanical release | ⏳ Coming weeks |
| Flange adapters (8102, 5208, etc.) | ⏳ Planned |
| ROS2 control nodes | ⏳ Planned |
| GUI bench tool (`seed-mango-studio`) | ⏳ After SDK stabilizes |

---

## Comparison snapshot (vs Berkeley Lite 6512)

| | **Seed Mango (FC-30)** | **Berkeley 6512** |
|--|------------------------|-------------------|
| Gearbox | Metal cycloidal **30:1** | 3D-printed PLA **15:1** |
| Peak torque | **TBD** _(target ~35 N·m)_ | ~20 N·m _(paper)_ |
| Encoder | 14-bit absolute (MA732) | AS5600 |
| Driver | MW6010-class FOC | B-G431B-ESC1 |
| Assembly | Factory built | DIY ~$188 BOM |

---

## Safety

- Driver has **no reverse-polarity protection** — double-check XT30 before power-on.
- Install and enable the **brake resistor** before fast decel, regen, or high-torque tests.
- Do not exceed continuous stall current without monitoring `Iq` and driver temperature.

Details: `docs/safety.md` _(planned)_

---

## Citation

```bibtex
@misc{seedmango2026,
  title  = {Seed Mango (FC-30): Metal Cycloidal Actuator for Open Humanoid Robotics},
  author = {StarFruit Lab},
  year   = {2026},
  url    = {https://github.com/StarFruit-Lab/seed-mango}
}
```

Lineage: [Berkeley Humanoid Lite](https://lite.berkeley-humanoid.org/) · [Hybrid Robotics](https://github.com/HybridRobotics/Berkeley-Humanoid-Lite)

---

## Links

| Resource | URL |
|----------|-----|
| GitHub | https://github.com/StarFruit-Lab/seed-mango |
| Quick Start | [docs/quickstart.md](docs/quickstart.md) |
| Wiring | [docs/wiring.md](docs/wiring.md) |
| Waitlist | https://starfruit-actuator.subscribepage.io |
| YouTube | https://www.youtube.com/@StarFruitRobotics |

---

## License

[MIT](LICENSE) — software in this repository.

Hardware CAD / STEP files will be released under a separate open-hardware license (planned: **CERN OHL v2**) when published.
