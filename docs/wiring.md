# Wiring Guide — Seed Mango (FC-30)

> **Model:** Seed Mango / FC-30 · 30:1 metal cycloidal actuator  
> **Driver:** MW6010-class FOC (ODrive 0.5.x firmware)  
> **Last updated:** 2026-07-15

---

## 1. Before you start

| Item | Spec | Notes |
|------|------|-------|
| DC supply | **24–36 V**, ≥15 A | 36 V recommended for load tests |
| USB cable | **Data-capable Type-C** | Charge-only cables will not work |
| Brake resistor | **2 Ω, ≥50 W** | Between **EMG** and **GND** (see §3) |
| Polarity | **Verify twice** | Driver has **no reverse-polarity protection** |

**Power-on order:**

1. **Power OFF**
2. Connect XT30 power leads (check + / −)
3. Connect brake resistor (if installed)
4. **Power ON** — driver LED should light
5. Plug in USB Type-C
6. Run `bringup.py` or SDK

---

## 2. Power connector (XT30)

```
  XT30 on driver
  ┌─────────────┐
  │  +  (red)   │  ← 24–36 V positive
  │  −  (black) │  ← GND / negative
  └─────────────┘
```

| Check | Pass criteria |
|-------|---------------|
| Voltage at rest | `vbus_voltage` ≈ 24–36 V in `diagnose()` |
| Polarity | Wrong polarity can **destroy the driver** — no recovery |

Use a bench supply with current limit (e.g. 5 A) for first connect, then raise for load tests.

---

## 3. Brake resistor (required before motion / regen)

When the output shaft is back-driven or the motor decelerates quickly, the driver generates regen current. Without a brake resistor, bus voltage can spike and damage the supply or driver.

| Item | Value |
|------|-------|
| Port | **EMG** and **GND** on the 5-pin header (top two pins per driver manual §2.4.7) |
| Resistor | **2 Ω / ≥50 W** (wire-wound, ceramic) |
| Enable in software | `configure_brake_resistor(2.0)` in SeedMangoSDK |

```
  5-pin header (view from wire side)
  ┌─────────────────┐
  │ EMG ●           │  ← resistor leg 1
  │ GND ●           │  ← resistor leg 2
  │ ...             │
  └─────────────────┘
        │
     [ 2Ω 50W ]
```

> **Safe bringup without resistor:** connect + diagnose + manual back-drive only (slow, light). Do **not** run closed-loop motion or calibration jerks until the resistor is installed and configured.

---

## 4. USB debug (Type-C)

| Item | Detail |
|------|--------|
| Interface | **Interface 2** — `CyberBeast Motor Driver Device` |
| Windows driver | **WinUSB** via [Zadig](https://zadig.akeo.ie) |
| Python package | `odrive==0.5.4` (must match 0.5.x firmware) |
| Do not install | ODrive Native driver on Interface 2 if using `odrive` Python tools |

**Zadig steps (Windows):**

1. Power on actuator, plug USB
2. Open Zadig → Options → **List All Devices**
3. Select **CyberBeast Motor Driver Device (Interface 2)**
4. Driver target: **WinUSB** → Install Driver

---

## 5. CAN bus (optional, multi-actuator)

| Item | Default |
|------|---------|
| Protocol | CAN 2.0 |
| Bitrate | 500 kbps (configurable in firmware) |
| Use case | Multi-actuator robots; USB used for debug / single-unit bench |

Single-unit bench testing only needs USB. Document CAN pinout in a future hardware revision note.

---

## 6. Bench fixture (recommended)

For calibration, fix the **stator housing** and leave the **output shaft free to rotate**.

See internal fixture spec: `mechanical/FC30_bench_cal_fixture_spec_v1.md` _(coming in mechanical release)_.

Minimum checks:

- [ ] Housing cannot move when pushed
- [ ] Output shaft rotates smoothly 360° by hand
- [ ] USB and power plugs accessible without removing fixture

---

## 7. Wiring checklist

| Step | Done |
|------|------|
| XT30 polarity verified with multimeter | ☐ |
| Supply set to 24 V / current limit 5 A (first power-on) | ☐ |
| Brake resistor soldered EMG–GND | ☐ |
| WinUSB installed on Interface 2 (Windows) | ☐ |
| Data-capable Type-C cable | ☐ |
| `pip install -r requirements.txt` | ☐ |
| `python bringup.py` connects (`vbus` OK, no errors) | ☐ |

---

## 8. Related docs

- [Quick Start](quickstart.md)
- [Safety](safety.md) _(planned)_
- [Troubleshooting](troubleshooting.md) _(planned)_
