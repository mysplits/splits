# Zones and tests

## When to test

- A sport has no threshold in TrainingPeaks or in `athlete.md`.
- The threshold is older than about 8 weeks during Base or Build.
- Recent workouts clearly contradict it (for example, threshold intervals that come out easy at low heart rate).
- Never in the last 3 weeks before the A race. Never in a load week's last days.

**Test fresh:** the middle of a recovery week, or after an easy day. A test done tired is useless and makes the athlete distrust the numbers. Load each test into TrainingPeaks as a structured workout.

## Swim: CSS (Critical Swim Speed)

1. Warm-up: 400 m easy + 4x50 m progressive (the last one fast), 1 min rest between 50s.
2. **400 m test:** as fast as can be held evenly. Write down the time.
3. 200 m easy (3-5 min).
4. **200 m test:** all out. Write down the time.
5. Cool-down 200 m easy.

**CSS (seconds per 100 m) = (T400 - T200) / 2.** Example: 400 m in 7:00 (420 s) and 200 m in 3:20 (200 s) → (420 - 200) / 2 = 110 s = **1:50/100 m**.

Update the swim threshold pace with `tp_update_speed_zones`. If the API fails, give the athlete the value to set by hand in TrainingPeaks settings.

**Do not judge a swim test by heart rate.** If the athlete could not go faster because of a local limit (shoulders, technique) with breathing and heart rate to spare, the CSS underestimates what they can hold over a long distance. Note it in `status.md`.

## Bike: FTP20

Indoors, on a smart trainer in **fixed resistance or level mode (not ERG)**:

1. Warm-up 10 min easy + 3x1 min high cadence with 1 min easy.
2. **5 min all out.** This empties the anaerobic reserve so the 20 min reflects threshold.
3. 5-10 min easy.
4. **20 min as hard as can be held evenly.** Start a little conservative and build.
5. Cool-down 10 min.

**FTP = 0.95 × average power of the 20 min.**

- **The 5 min all-out validates the test, not the final heart rate.** If the 5 min was a real effort and the 20 min was even and maximal, the test is good.
- A test where the athlete held back "to survive the 20 min" is not maximal: do not lower FTP because of it. Keep the previous value and retest when fresh.
- If a direct test and an estimate from heart rate disagree, **the test wins**. Read estimates as a ceiling, not as a value.

Update with `tp_update_ftp`. TrainingPeaks recalculates the power zones (Coggan).

No power meter: skip FTP. Bike quality goes by heart rate and perceived effort.

## Run: threshold (30 min test)

On a flat route or track, after 15 min warm-up with a few strides:

1. **30 min solo, as hard as can be held evenly.** Lap at 10 min.
2. **Threshold heart rate (LTHR) = average heart rate of the last 20 min.**
3. **Threshold pace = average pace of the 30 min.**
4. Cool-down 10 min.

A recent race of 10 km to a half marathon done all out can replace the test: threshold pace is roughly 10 km race pace + 10-15 s/km.

Update threshold heart rate with `tp_update_hr_zones` and threshold pace with `tp_update_speed_zones`.

## Zone systems

| Sport | Basis | System |
|---|---|---|
| Heart rate (all sports) | LTHR per sport | Friel, 7 zones |
| Bike power | FTP | Coggan, 6-7 zones |
| Swim pace | CSS | % of threshold speed (see `method.md`) |
| Run pace | Threshold pace | % of threshold speed for quality; HR ceiling for easy |

Bike LTHR is usually 5-10 bpm lower than run LTHR. If the athlete has no bike LTHR, estimate it from the FTP test (average HR of the 20 min × 0.95) and refine it with their rides.

**One heart rate set for all sports.** TrainingPeaks may hold a single HR zone set (`workoutTypeId` 0) instead of one per sport (1 swim, 2 bike, 3 run). That set is almost always the run LTHR. Do not use it as is for outdoor rides: estimate the bike LTHR as above, write both in `athlete.md`, and offer to set a bike-specific HR zone set with `tp_update_hr_zones`.

**Threshold dates.** TrainingPeaks does not store when a threshold was set. Record the date and source in `athlete.md` every time you set one, so the 8-week rule can be applied later.

**Percent of threshold pace in TrainingPeaks is a % of speed, not of time:** higher means faster. 100% = threshold. Example with a 4:12/km threshold: 4:45/km ≈ 88%, 6:00/km ≈ 70%.

Convert a target pace to %: `threshold_pace_seconds / target_pace_seconds × 100`.
