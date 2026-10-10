# Home Assistant Water Valve Protection

Two independent blueprints for a switch-controlled main water valve: **ON opens; OFF closes**.

## Import

[Import leak protection](https://my.home-assistant.io/redirect/blueprint_import/?blueprint_url=https%3A%2F%2Fgithub.com%2FTeeseeone%2FHA-Water-Valve-Protection-Blueprint%2Fblob%2Fmain%2Fblueprints%2Fwater_valve_protection.yaml)

[Import optional monthly test](https://my.home-assistant.io/redirect/blueprint_import/?blueprint_url=https%3A%2F%2Fgithub.com%2FTeeseeone%2FHA-Water-Valve-Protection-Blueprint%2Fblob%2Fmain%2Fblueprints%2Fwater_valve_monthly_test.yaml)

Requires Home Assistant 2024.10 or newer. Importing alone does not create or enable an automation.

## Setup

1. Create a Toggle helper under Settings → Devices & services → Helpers. Name it **Water shutoff lock**. Keep its restored state; do not set a fixed initial state.
2. Create an automation from **Water Valve Protection**.
3. Select your valve switch, e.g. `switch.hovedventil_vann`, and the lock helper.
4. Select moisture/leak binary sensors directly and/or select Home Assistant labels. Labels can be attached to devices or entities. Only binary sensors with device class **moisture** are included. Area labels are not expanded. Label changes are picked up by the next scan.
5. Optionally select an actuator fault binary sensor. For a persistently asserted flag on an otherwise working actuator, choose **Notify only**, or leave it unselected.
6. Optional notification actions can use `{{ valve_message }}` as their message. Choose your phone's notify action. Keep these actions short so they do not delay subsequent scans.
7. Supervise a leak-sensor test and confirm physical water shutoff.

## Leak protection

Scans every five seconds and on Home Assistant startup. Any wet sensor enables the persistent shutoff lock. While locked, OFF is sent if the valve is not reporting OFF, including when it is unavailable. It retries on subsequent scans. Persistent notifications identify the shutoff and reported faults. Optional phone actions run once when a leak first enables the lock.

**This blueprint never sends ON.** A drying sensor does not release the lock. Investigate the cause, confirm sensors are dry, turn the helper OFF, then reopen the valve manually. With a wet sensor the lock will be asserted again. The lock must remain available; test after any restart.

Fault handling never blocks emergency OFF commands. Notify/block modes show a persistent fault notification while fault is reported; ignore mode suppresses it. This flag is not treated as verified valve position.

Unavailable leak sensors alone do not automatically close the valve. They block the monthly test. Leak events shorter than the scan interval can be missed. This is supplementary Home Assistant protection, not a claim of certified leak protection.

## Optional monthly exercise

Create a second automation from **Water Valve Monthly Timed Test**. Use the **same valve, helper, sensors, labels and fault policy** as the protection automation.

Scheduled testing is disabled by default. Choose day 1–28, local test time, measured motor travel time (default 30 seconds), and closed hold time (default 5 seconds). Enable after a supervised test.

The test requires:
- At least one selected moisture sensor, all reporting dry.
- Lock helper OFF and valve reporting ON.
- If fault handling is **block**, every selected fault sensor must report OFF.

It sends OFF, waits travel + hold time, rechecks guards, sends ON, and waits the opening travel time. It does not reopen a valve that was already closed at the start. Wet/unavailable sensors, an enabled/unavailable lock, unavailable valve, or a blocking fault during either wait aborts the test and enables the lock. A failed reported OFF also prevents reopening. During opening, an interruption sends OFF again.

ON/OFF state is only a controller report. For actuators without independent feedback, the result says **test commands completed**, not that physical closure is verified. There is no independent position-feedback input in v1.0.

Home Assistant restart, automation reload, or a service error during testing can leave water closed. No automatic recovery opening is performed; inspect manually. An open-command result without reported ON creates a test-result warning. Monthly tests that fail preconditions are skipped, without automatic catch-up.

## Known device

IOTPerfect PF-PM02D-TYZ (`_TZE200_d0ypnbvn`) exposes switch state and fault in Zigbee2MQTT. Separate physical-position feedback is not exposed. This does not establish whether it has internal motor limit switches.

## Validation

YAML and blueprint input-reference checks are performed locally. Structural safety tests check that protection never opens the valve, scheduled tests default to disabled, both travel waits include interlocks, and faults cannot gate emergency closure. This has not been executed against a live Home Assistant instance or physical valve.

Documentation: [Zigbee2MQTT PF-PM02D-TYZ](https://www.zigbee2mqtt.io/devices/PF-PM02D-TYZ.html).
