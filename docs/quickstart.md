# Quick Start — Seed Mango (FC-30)

Get from **zero** to **connected + calibrated** in about **30 minutes**.

> **Scope:** This guide covers USB bench bringup on **Windows**.  
> **Firmware:** ODrive 0.5.x · **Python:** 3.10+ · **Package:** `odrive==0.5.4`

---

## What you need

| # | Item |
|---|------|
| 1 | Seed Mango (FC-30) actuator |
| 2 | DC supply **24–36 V**, ≥15 A |
| 3 | USB **data** Type-C cable |
| 4 | Brake resistor **2 Ω / ≥50 W** on EMG–GND _(required before closed-loop motion)_ |
| 5 | PC with Python 3.10+ |
| 6 | Bench fixture or vise — housing fixed, output shaft free |

Full wiring: **[wiring.md](wiring.md)**

---

## Step 1 — Clone and install

```powershell
git clone https://github.com/StarFruit-Lab/seed-mango.git
cd seed-mango
pip install -r requirements.txt
```

Verify:

```powershell
python -c "import odrive; print('odrive OK')"
```

---

## Step 2 — Install WinUSB (Windows, one-time)

1. Power **on** the actuator (see [wiring.md](wiring.md) for order)
2. Plug in USB Type-C
3. Open [Zadig](https://zadig.akeo.ie) → Options → **List All Devices**
4. Select **CyberBeast Motor Driver Device (Interface 2)**
5. Install **WinUSB**

> If `odrive.find_any()` times out, 90% of the time it is a charge-only cable or wrong USB driver.

---

## Step 3 — Run guided bringup

```powershell
python bringup.py
```

The script walks through:

| Step | Action | Safe without brake resistor? |
|------|--------|------------------------------|
| 1 | `connect()` | Yes |
| 2 | `diagnose()` — check `vbus`, errors, temperature | Yes |
| 3 | `get_encoder_status()` | Yes |
| 4 | `monitor()` — slowly hand-rotate output shaft | Yes (gentle only) |
| 5 | `auto_calibrate()` — motor will spin and beep | **Fixture required**; resistor recommended |

**Before Step 5:**

- Fix the **housing** firmly; output shaft **unloaded** and free to spin
- Confirm `vbus_voltage` is 24–36 V and no active errors

Type `yes` when prompted to start calibration.

---

## Step 4 — Configure brake resistor (before motion tests)

After calibration, enable the brake resistor in software:

```python
from SeedMangoSDK import SeedMangoSDK

a = SeedMangoSDK()
a.connect()
a.configure_brake_resistor(2.0)
# Driver reboots — wait 2 s, then reconnect:
a.connect()
a.diagnose()
```

Physical resistor must already be wired **EMG–GND** — see [wiring.md](wiring.md).

---

## Step 5 — First motion (position mode)

```python
from SeedMangoSDK import SeedMangoSDK
import time

a = SeedMangoSDK(reduction_ratio=-30.0)
a.connect()
a.set_mode('position')
a.move_to(30.0)
time.sleep(2)
a.move_to(0.0)
print("Done.")
```

Start with **±30°** on a bench fixture before attaching any linkage.

---

## Step 6 — Verify encoder (manual check)

With power on and **not** in closed-loop:

```python
a.monitor(duration=10.0, interval=0.2)
```

Slowly rotate the output shaft by hand. You should see:

- `末端` (output angle) changes smoothly
- `vbus` rises slightly during back-drive (normal)
- With brake resistor configured, `vbus` spike should stay bounded

---

## Expected `diagnose()` output (healthy unit)

| Field | Typical value |
|-------|---------------|
| `vbus_voltage` | 24–36 V |
| `axis_state` | `1` (idle) before `set_mode` |
| Errors | None |
| `output_angle_deg` | Changes when shaft is rotated |

---

## Common failures

| Symptom | Fix |
|---------|-----|
| `find_any` timeout | WinUSB on Interface 2; data cable; power on |
| `vbus` = 0 | Check XT30 polarity and supply |
| `CPR_POLEPAIRS_MISMATCH` | Re-run calibration; check magnet/encoder gap |
| `ObjectLostError` after save | **Normal** — driver reboots after `save_configuration()`; wait 2 s and `connect()` again |
| Motor jerks / `vbus` spike | Install and enable **2 Ω brake resistor** |

Full list: `docs/troubleshooting.md` _(planned)_

---

## Next steps

| Goal | Doc / file |
|------|------------|
| API reference | `SeedMangoSDK.py` |
| Bench test log | `docs/test_results_v1.0.md` _(coming)_ |
| Mechanical CAD | `mechanical/` _(coming)_ |
| Berkeley Lite integration | `docs/integrate_berkeley_lite.md` _(planned)_ |

---

## Minimal Python reference

```python
from SeedMangoSDK import SeedMangoSDK

actuator = SeedMangoSDK(reduction_ratio=-30.0)
actuator.connect()
actuator.diagnose()
actuator.get_encoder_status()
# actuator.auto_calibrate()   # once per unit, then saved
# actuator.set_mode('position')
# actuator.move_to(90.0)
```
