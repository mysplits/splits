# Loading workouts into TrainingPeaks

Everything here was learned by breaking it. Read it before any `tp_create_workout` or `tp_update_workout`.

## Required on every workout

- **`sport`, always.** Without it TrainingPeaks stores `sport: null` and the workout does not sync to the watch or to indoor apps.

| Session | `sport` |
|---|---|
| Any swim | `Swim` |
| Bike indoor or outdoor | `Bike` |
| Any run | `Run` |
| Strength | `Strength` |
| Mobility, core | `Custom` |

- **Never `Brick`.** A brick is two workouts on the same day: `Bike` + `Run`. As a `Brick`, indoor apps do not pick up the bike and the watch has no separate run.
- **`duration_minutes` and `distance_km`, always,** as estimates. A swim by distance still needs a duration; an indoor ride by time still needs a distance. That is what adds up the planned hours of the week.
- **`description` has a hard limit of 2,000 characters.** Above it the call fails with `VALIDATION_ERROR` and nothing is created. Trim before calling.
- **`date`** as `YYYY-MM-DD`, or `YYYY-MM-DDTHH:MM:SS` for a planned start time. API timestamps come back in UTC.

## Unit of the structure: the golden rule

**If the session is measured in distance, the structure is in distance. If it is measured in time, the structure is in time. Never convert one into the other with the target pace.** An 8 km run is configured as 8,000 m, not as 42 min, because the watch guides the athlete step by step in the unit of the structure.

| Session | `primaryLengthMetric` | Step unit |
|---|---|---|
| Swim (always) | `distance` | `meter` (rests in `second`) |
| Bike outdoor | `distance` | `meter` |
| Bike indoor | `duration` | `second` |
| Run in km | `distance` | `meter` (strides can be 100 m, rests in `second`) |
| Run off the bike | `duration` | `second` |

## Two payload formats

### Simplified `structure`: time only
Good for indoor rides and runs by time. The server computes duration, IF and TSS.

```json
{
  "date": "2026-03-01", "sport": "Bike", "title": "4x8' 200-210W / 2' rec",
  "duration_minutes": 60, "distance_km": 30,
  "structure": {
    "primaryIntensityMetric": "percentOfFtp",
    "steps": [
      {"name": "Warm-up", "duration_seconds": 600, "intensity_min": 50, "intensity_max": 55, "intensityClass": "warmUp"},
      {"type": "repetition", "reps": 4, "steps": [
        {"name": "8' 200-210W", "duration_seconds": 480, "intensity_min": 88, "intensity_max": 92, "intensityClass": "active"},
        {"name": "2' rec", "duration_seconds": 120, "intensity_min": 45, "intensity_max": 50, "intensityClass": "rest"}
      ]},
      {"name": "Cool-down", "duration_seconds": 600, "intensity_min": 45, "intensity_max": 55, "intensityClass": "coolDown"}
    ]
  }
}
```

It **only accepts `duration_seconds`**. Any step in metres fails with "duration_seconds required".

### Native `structured_workout`: needed for distance
Required whenever any step is in metres (all swims, outdoor rides, runs in km). **Build it with `scripts/build_workout.py`** instead of by hand (run it with the MCP's Python, see `setup-trainingpeaks.md`; its docstring explains the input). Its output reproduces real TrainingPeaks workouts point by point. Use either `structure` or `structured_workout` in a call, never both.

Required top-level fields: `structure`, `polyline`, `primaryLengthMetric`, `primaryIntensityMetric`, `primaryIntensityTargetOrRange`, and **`visualizationDistanceUnit: "meter"`** if any step is in distance. Without it, TrainingPeaks and the watch show the unit as "undefined"; the `unit: "meter"` on each step is not enough.

A real run that loads and syncs correctly (threshold pace 4:12/km):

```json
{
  "structure": [
    {"type": "step", "length": {"value": 1, "unit": "repetition"}, "begin": 0, "end": 2000,
     "steps": [{"name": "Warm-up 2 km 5:50-6:10", "type": "step", "length": {"value": 2000, "unit": "meter"},
                "targets": [{"minValue": 68, "maxValue": 72}], "intensityClass": "warmUp", "openDuration": false}]},
    {"type": "step", "length": {"value": 1, "unit": "repetition"}, "begin": 2000, "end": 8000,
     "steps": [{"name": "6 km at 4:45-4:50", "type": "step", "length": {"value": 6000, "unit": "meter"},
                "targets": [{"minValue": 87, "maxValue": 88}], "intensityClass": "active", "openDuration": false}]},
    {"type": "step", "length": {"value": 1, "unit": "repetition"}, "begin": 8000, "end": 10000,
     "steps": [{"name": "Cool-down 2 km 6:00-6:20", "type": "step", "length": {"value": 2000, "unit": "meter"},
                "targets": [{"minValue": 66, "maxValue": 70}], "intensityClass": "coolDown", "openDuration": false}]}
  ],
  "polyline": [[0,0],[0,0.8182],[0.2,0.8182],[0.2,0],[0.2,1],[0.8,1],[0.8,0],[0.8,0.7955],[1,0.7955],[1,0]],
  "primaryLengthMetric": "distance",
  "primaryIntensityMetric": "percentOfThresholdPace",
  "primaryIntensityTargetOrRange": "range",
  "visualizationDistanceUnit": "meter"
}
```

### The polyline
**Required on create and on update**, or TrainingPeaks answers "missing required fields: polyline". It is the little chart of the workout:

- Points `[x, y]`. Each step draws `[x_start, 0], [x_start, y], [x_end, y], [x_end, 0]`.
- `x` = cumulative fraction of the total (0 to 1). In distance workouts, rests count as 10 m virtual. In mixed workouts, estimate the duration of distance steps from the target pace to place them on the axis.
- `y` = the step's max target divided by the workout's highest max target (for `percentOfThresholdPace`), or divided by 100 (for `percentOfThresholdHr` and `percentOfFtp`). Rests are drawn at 0.

The script computes all of this. When in doubt, read a workout that already works with `tp_get_workout` and copy its exact format.

`primaryIntensityMetric` values: `percentOfFtp`, `percentOfThresholdHr`, `percentOfThresholdPace`.

## Per sport

### Swim
- Always a structure, always by distance, `percentOfThresholdPace`.
- Step names include the metres: `"Warm-up 400m"`, `"200m steady"`, `"100m fast"`.
- **Rests (wall rest) are `rest` steps with intensity 0-0.** Any intensity above 0 makes TrainingPeaks count movement and add phantom metres to the planned distance.
- **Do not use repetition blocks in swims.** TrainingPeaks only draws one rep. Expand every rep as its own step with its own `begin`/`end`. The script does it with `expand_repeats`.
- The description also lists every block with paces and the total metres.

### Bike indoor
- Structure by time (simplified format is fine), `percentOfFtp`.
- Description: where (trainer and app), mode (ERG or not), and the blocks with watts.

### Bike outdoor
- Native structure by distance. `percentOfFtp` with an outdoor power meter, otherwise `percentOfThresholdHr`.
- `begin`/`end` in cumulative metres: warm-up 0→7000, block 7000→60000, cool-down 60000→65000.
- Description: "Outdoor." + route advice + blocks with km and targets + auto-lap setting.

### Run
- By km: native structure in distance. Off the bike: by time.
- Pace targets as `percentOfThresholdPace` (higher = faster); heart rate ceilings as `percentOfThresholdHr`. Use one metric per workout and put the other one in the description.

### Strength and mobility
- Title + `duration_minutes` only. **No structure.**
- They do not sync to the watch. The athlete marks them done with Quick Log in TrainingPeaks.

## Known TrainingPeaks quirks

- When a completed swim is paired on the web, TrainingPeaks may redisplay its paces using the run threshold. It is display only; the data is fine.
- A barometric glitch on some watches leaves garbage in completed runs (absurd elevation, TSS or efficiency factor). Ignore those values in the analysis and say so.
- Some indoor apps only show the workouts of the current day.
- Completed workouts often come back with `sport: null`. That is normal for completed activities; it only matters on planned ones. To know the sport, read `workout_type` with `tp_get_workout` (1 swim, 2 bike, 3 run; the full list with `tp_get_workout_types`).
- `tp_analyze_workout` can return `NOT_FOUND` even for workouts that exist. Fall back to the totals in `tp_get_workout` and ask the athlete for their laps.
- Every date-range tool accepts at most 90 days. `tp_get_workouts` over more than 2-3 weeks can overflow the output: query in chunks.
- `tp_get_peaks` only covers `Bike` (`power5min`, `power20min`...) and `Run` (`speed5K`, `speed10K`, `speedHalf`).
- `tp_update_speed_zones` sometimes fails with HTTP 500. Give the athlete the value to set by hand.

## Before you load

1. Re-read the week the athlete approved.
2. For each session: right `sport`, right unit, title matches the structure, description under 2,000 characters.
3. Build distance workouts with the script; validate with `tp_validate_structure` if available.
4. Create them, then list the week with `tp_get_workouts` and check every session is there with its sport and planned distance.
