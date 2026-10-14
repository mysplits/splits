# SPLITS

**Your endurance coach, inside your own Claude, on top of your TrainingPeaks.**

SPLITS is a free skill for Claude. It reads your TrainingPeaks, asks you what it cannot see there, builds a plan to your race, designs every session with a purpose, loads it into your calendar and reviews what you actually did. For triathletes, and for athletes who only run, ride or swim.

**Landing page:** https://mysplits.github.io

## What it does

- **Reads before it asks.** Profile, thresholds, zones, races, fitness (CTL/ATL) and your last 8-12 weeks of training come from TrainingPeaks. It only asks for what is missing: your story as an athlete, your goal, your availability, your equipment, your injuries.
- **Finds your zones.** If a threshold is missing or stale, it proposes the test (CSS for swimming, FTP20 for the bike, a 30-minute threshold run) and updates TrainingPeaks with the result.
- **Builds the plan.** Base, build, peak and taper counted back from your A race, 3 load weeks for 1 recovery week, an evidence-based taper and the recovery after it.
- **Coaches every week.** It analyses your completed sessions block by block, plans the next week from what you really did, asks for your OK and loads it into TrainingPeaks as structured workouts your watch and trainer can follow.
- **Disagrees when it should.** It is built to give you the best answer for your performance, not the one you want to hear.

## Install

1. Download [`splits.zip`](https://github.com/mysplits/splits/releases/latest/download/splits.zip) from the latest release.
2. In Claude, go to Settings, Capabilities, Skills, and upload the zip.
3. Open the **Code** tab of Claude Desktop and type **"Set up SPLITS"**. Claude walks you through:
   1. Connecting TrainingPeaks (it installs the connector for you)
   2. Choosing a folder for your training notes
   3. Reading your TrainingPeaks
   4. A few questions about you and your goal
   5. Zones and tests
   6. Your plan and your first week

## Requirements

- Claude Desktop with the Code tab (Claude Code). Setup needs a shell to install the TrainingPeaks connector.
- A TrainingPeaks account. Premium unlocks structured workouts on your device and planning ahead.
- Python 3.10 or newer (Claude helps you install it if needed).

## Privacy

- SPLITS has no server. Your own Claude talks to TrainingPeaks from your own computer.
- The connection uses the open-source [TrainingPeaks MCP server](https://github.com/JamsusMaximus/trainingpeaks-mcp) by James McAulay. Your TrainingPeaks session cookie is stored encrypted in your system keyring and is never shown to Claude.
- Your profile, plan and session notes live in a local folder you choose.
- Nothing is loaded into your calendar without your OK.

## Not medical advice

SPLITS is a training tool, not a doctor. If something hurts, if you feel dizzy or faint, or if you have a health condition, talk to a medical professional before following any plan.

## What's in this repo

| Path | What it is |
|---|---|
| `SKILL.md` | How the coach works: setup, the weekly loop, session design and loading rules |
| `references/method.md` | Periodization, 3:1 cycles, taper, 80/20, weekly structure, sessions per sport, naming |
| `references/zones-and-tests.md` | CSS, FTP20 and run threshold tests, and how zones are derived |
| `references/trainingpeaks.md` | How to load workouts that actually sync: units, payloads, polyline and every quirk found the hard way |
| `references/setup-trainingpeaks.md` | Installing and authenticating the TrainingPeaks connector |
| `scripts/build_workout.py` | Builds the native structured workout (with its polyline) for swims, outdoor rides and runs by distance |
| `templates/` | Athlete profile, plan, session note and race checklist |

## Feedback

Found a bug or have an idea? [Open an issue](https://github.com/mysplits/splits/issues).

---

Built by [Borja Anadón](https://borjaanadon.com). MIT licence.
