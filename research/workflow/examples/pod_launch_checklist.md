# Pod Launch Checklist

- Confirm repo path, branch, remote, and dirty state.
- Commit and push the exact script to be run.
- Create or update the run registry entry with `planned` status.
- Confirm GPU requirement, budget ceiling, and no spot instance policy.
- Copy or clone the committed repo state onto the pod.
- Write `manifest.json` before starting the long job.
- Start the job detached with durable stdout and stderr logging.
- Save the process ID to `run.pid`.
- Confirm the first heartbeat and first output record.
- Update run registry status to `running`.
