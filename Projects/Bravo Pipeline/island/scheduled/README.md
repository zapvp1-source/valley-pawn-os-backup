# Island — scheduled/

Island-only scheduled task definitions (each as its own folder with a `SKILL.md`).

A task here is an island citizen: it reads from `../output/`, invokes handlers in `../source/`, and posts to a dedicated island Slack channel (or no channel at all during proving). It never touches a prod CSV, prod handler, or prod channel.

When an island task is proven, the migration step is to clone it into the real `/Users/joshuadavis/Documents/Claude/Scheduled/` folder and flip its paths from island to prod. See `../ISLAND.md` → Deployment checklist.
