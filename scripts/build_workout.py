#!/usr/bin/env python3
"""
Builds a native TrainingPeaks `structured_workout` (with begin/end and polyline)
from a simple step list. Needed for any workout with steps in metres.

Usage:
    python build_workout.py input.json > structured_workout.json
    echo '{...}' | python build_workout.py -

Input:
{
  "length_metric": "distance",              # "distance" or "duration"
  "intensity_metric": "percentOfThresholdPace",  # or percentOfThresholdHr, percentOfFtp
  "threshold_pace_s_per_km": 252,           # optional: places distance steps on the
                                            # time axis in mixed workouts (run)
  "expand_repeats": true,                   # swims: always true
  "steps": [
    {"name": "Warm-up 400m", "meters": 400, "min": 80, "max": 83, "class": "warmUp"},
    {"repeat": 4, "steps": [
      {"name": "100m fast", "meters": 100, "min": 108, "max": 112, "class": "active"},
      {"name": "Rest 20\"", "seconds": 20, "class": "rest"}
    ]},
    {"name": "Cool-down 200m", "meters": 200, "min": 80, "max": 83, "class": "coolDown"}
  ]
}

Rules it enforces:
  - rest steps get intensity 0-0 (otherwise TrainingPeaks adds phantom metres)
  - in distance workouts, a rest counts as 10 m virtual on the polyline
  - visualizationDistanceUnit: "meter" whenever any step is in metres
  - polyline y = max / highest max (pace) or max / 100 (HR, FTP)
"""
import json
import sys

REST_VIRTUAL_M = 10


def flatten(steps, expand):
    """Yields ("step", step) or ("repeat", n, [steps]) items in order."""
    out = []
    for s in steps:
        if "repeat" in s:
            if expand:
                for _ in range(int(s["repeat"])):
                    out.extend(flatten(s["steps"], expand))
            else:
                out.append(("repeat", int(s["repeat"]), flatten(s["steps"], expand)))
        else:
            out.append(("step", s))
    return out


def is_rest(s):
    return s.get("class") == "rest"


def native_step(s):
    if "meters" in s:
        length = {"value": s["meters"], "unit": "meter"}
    elif "seconds" in s:
        length = {"value": s["seconds"], "unit": "second"}
    else:
        raise ValueError("Step needs 'meters' or 'seconds': %r" % s.get("name"))
    lo, hi = (0, 0) if is_rest(s) else (s["min"], s["max"])
    return {
        "name": s["name"],
        "type": "step",
        "length": length,
        "targets": [{"minValue": lo, "maxValue": hi}],
        "intensityClass": s.get("class", "active"),
        "openDuration": False,
    }


def axis_length(s, metric, pace):
    """Length of a step on the polyline's x axis, in the workout's primary unit."""
    if metric == "distance":
        if "meters" in s:
            return s["meters"]
        if is_rest(s):
            return REST_VIRTUAL_M
        if pace:  # time step inside a distance workout: convert with threshold pace
            return s["seconds"] / pace * 1000
        return REST_VIRTUAL_M
    # duration workout
    if "seconds" in s:
        return s["seconds"]
    if pace:
        return s["meters"] / 1000 * pace * (100.0 / max(s.get("max", 100), 1))
    raise ValueError("Distance step in a duration workout needs threshold_pace_s_per_km")


def build(cfg):
    metric = cfg.get("length_metric", "distance")
    imetric = cfg["intensity_metric"]
    pace = cfg.get("threshold_pace_s_per_km")
    expand = cfg.get("expand_repeats", False)
    items = flatten(cfg["steps"], expand)

    # Linear list of leaf steps with their x lengths, to place begin/end and the polyline
    def leaves(items):
        for it in items:
            if it[0] == "step":
                yield it[1]
            else:
                for _ in range(it[1]):
                    yield from leaves(it[2])

    all_leaves = list(leaves(items))
    total = sum(axis_length(s, metric, pace) for s in all_leaves)
    work_max = max((s["max"] for s in all_leaves if not is_rest(s)), default=100)
    y_div = work_max if imetric == "percentOfThresholdPace" else 100.0

    structure, polyline = [], []
    pos = 0.0  # cumulative position in the primary unit, for begin/end
    xpos = 0.0  # cumulative x length, for the polyline

    def round_x(v):
        return round(v / total, 4) if total else 0

    def draw(s):
        nonlocal xpos
        xs = round_x(xpos)
        xpos += axis_length(s, metric, pace)
        xe = round_x(xpos)
        y = 0 if is_rest(s) else round(s["max"] / y_div, 4)
        if not polyline:
            polyline.append([0, 0])
        polyline.extend([[xs, y], [xe, y], [xe, 0]] if y else [[xs, 0], [xe, 0], [xe, 0]])

    def primary(s):
        if metric == "distance":
            return s.get("meters", 0)
        return s.get("seconds", 0)

    for it in items:
        if it[0] == "step":
            s = it[1]
            begin = pos
            pos += primary(s)
            draw(s)
            structure.append({
                "type": "step",
                "length": {"value": 1, "unit": "repetition"},
                "steps": [native_step(s)],
                "begin": round(begin), "end": round(pos),
            })
        else:
            n, inner = it[1], it[2]
            inner_steps = [x[1] for x in inner if x[0] == "step"]
            begin = pos
            for _ in range(n):
                for s in inner_steps:
                    pos += primary(s)
                    draw(s)
            structure.append({
                "type": "repetition",
                "length": {"value": n, "unit": "repetition"},
                "steps": [native_step(s) for s in inner_steps],
                "begin": round(begin), "end": round(pos),
            })

    out = {
        "structure": structure,
        "polyline": polyline,
        "primaryLengthMetric": metric,
        "primaryIntensityMetric": imetric,
        "primaryIntensityTargetOrRange": "range",
    }
    if any("meters" in s for s in all_leaves):
        out["visualizationDistanceUnit"] = "meter"
    return out


def main():
    src = sys.argv[1] if len(sys.argv) > 1 else "-"
    cfg = json.load(sys.stdin if src == "-" else open(src, encoding="utf-8"))
    json.dump(build(cfg), sys.stdout, indent=2, ensure_ascii=False)
    sys.stdout.write("\n")


if __name__ == "__main__":
    main()
