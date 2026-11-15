# Thirdminute 0.2.10 for Codex CLI

Thirdminute is a Linux preview that adds long-term memory to Codex chats. It
learns from completed turns and gives Codex tools to recall what it learned.
The memory graph is stored on your machine. Consolidation and memory
maintenance use Codex model requests, which include the source or memory
records needed for the job.

## Install

Use x86-64 Linux with Python 3.11 or later and stock Codex CLI 0.169.0,
0.168.0, 0.167.2, or 0.166.0. Use 0.169.0 for a new installation. Sign in
to Codex with an account that can run the model you choose for memory workers.
The preview was tested with `gpt-6.1-terra` at `xhigh`, which is the default.
The setup below uses keyword search and Python's standard library.

Download `thirdminute-0.2.10-linux.tar.gz` and `SHA256SUMS` from the Thirdminute
release into `~/Downloads`. Run these commands in Bash. If you downloaded the
files elsewhere, set `tm_download` to that directory.

```bash
tm_download="$HOME/Downloads"
tm_install="$HOME/.local/share/thirdminute/0.2.10"
(cd "$tm_download" &&
  awk '$2 == "thirdminute-0.2.10-linux.tar.gz"' SHA256SUMS | sha256sum --strict -c -) &&
  mkdir -p "$tm_install" &&
  tar -xzf "$tm_download/thirdminute-0.2.10-linux.tar.gz" -C "$tm_install" &&
  codex plugin marketplace add "$tm_install/marketplace" &&
  codex plugin add thirdminute@thirdminute-local
```

The local marketplace is the extracted folder that Codex installs from. Keep
it at that location until you remove the marketplace from Codex.

Set up Thirdminute's data directory. These paths use Codex's configured home
when you set `CODEX_HOME`.

```bash
tm_codex_dir="${CODEX_HOME:-$HOME/.codex}"
tm_package="$tm_codex_dir/plugins/cache/thirdminute-local/thirdminute/0.2.10"
tm_data="$tm_codex_dir/plugins/data/thirdminute-thirdminute-local"

thirdminute() {
  python3 "$tm_package/launch.py" --data "$tm_data" "$@"
}

mkdir -p "$tm_codex_dir/sessions"
thirdminute setup --source-root "$tm_codex_dir/sessions" --prototype-bytes
thirdminute status
```

Setup leaves learning disabled. If you already use other direct-only tool
namespaces in Codex, pass `--existing-namespace NAME` for each one during setup.
A direct-only namespace lists tools Codex calls individually.

## Choose the memory worker model

After setup, use `thirdminute worker-model MODEL --effort LEVEL`. Replace
`MODEL` with a model ID available to you in Codex and `LEVEL` with a reasoning
effort the model supports. If you omit `--effort`, the command saves `xhigh`.
Run `thirdminute status` to see the saved choice.

One setting applies to consolidation, focused maintenance, exploratory
maintenance, and graph repair. A worker that has already started keeps its
model through any corrections. The next worker to start uses the saved choice,
including work already in the queue. Choose your ordinary chat model in Codex.

To restore the preview default, run `thirdminute worker-model gpt-6.1-terra`.
Codex checks model access when a worker starts. Thirdminute uses the same byte
limits and tool requirements for every model.

## Approve the hooks and start learning

Use this command to open Codex with Thirdminute's options. Keep the path and
function definitions for later terminal sessions.

```bash
tm_codex() {
  python3 -c '
import json
import os
import subprocess
import sys

launcher, data, *args = sys.argv[1:]
options = subprocess.check_output(
    [sys.executable, launcher, "--data", data, "codex-options"], text=True
)
os.execvp("codex", ["codex", *json.loads(options), *args])
' "$tm_package/launch.py" "$tm_data" "$@"
}

tm_codex
```

In Codex, open `/hooks` and review and approve the eight hooks for
`thirdminute@thirdminute-local`. Hooks are commands that Codex runs at specific
points in a chat. Review them again when Codex requests approval after an update.
Exit Codex and run these commands.

```bash
thirdminute enable
thirdminute start
thirdminute status
tm_codex
```

While learning is enabled, turns that start in chats with the plugin active
become eligible for learning. This includes new turns in existing chats. The
source reader reads records from the configured Codex sessions directory. The
host saves eligible source, learned memory, and pending work in
`$tm_data/memory.sqlite`. Learning starts at the time you enable it.

## Learn and recall one fact

Send this test message in Codex.

> Routine inspections for the fictional Meadow Relay take place in the Jade Annex. Reply only ACK.

Exit the chat after Codex answers. The host keeps running. For this small test,
allow 15 minutes of inactivity and time for the consolidation worker to finish.
Run `thirdminute status` and check for a committed job and a new graph version.
Open a fresh chat with `tm_codex` and send this request.

> Use Thirdminute's `memory_search` to find where routine inspections take place for the Meadow Relay. Give the exact location from the tool reply.

The reply should contain `Jade Annex`. When earlier recall results need a refresh,
Codex can receive a short notice asking it to retrieve current memory records.

## Check status or pause learning

Run `thirdminute status` to see whether learning is enabled, whether the host
is running, and whether source or jobs need attention. For a local status page,
run `thirdminute status-page` and open the URL it prints. The host writes its
log to `$tm_data/host.log`.

- `thirdminute stop` stops the host and any worker it started. Codex can still
  queue later turns while learning is enabled. Use `thirdminute start` to resume
  processing. Run it again after restarting your machine.
- `thirdminute disable` stops the host and excludes turns that start afterward
  from learning. A turn already eligible can finish capture. Recall stays
  available while the plugin is installed and active. Use `thirdminute enable`
  and `thirdminute start` to resume learning.

## Back up and restore

Finish participating turns and exit Codex before backing up. The backup
contains Thirdminute's saved state. Keep your Codex chat histories separately.
Use these commands to create a private backup with a new path.

```bash
thirdminute stop
tm_backup_dir=$(mktemp -d "$HOME/thirdminute-backup.XXXXXX") &&
  thirdminute backup "$tm_backup_dir/memory.sqlite" &&
  printf '%s\n' "$tm_backup_dir/memory.sqlite"
```

To restore a backup from this installation, finish participating turns, exit
Codex, and stop the host. Set `tm_backup` to the absolute path printed above.
Keep the same Thirdminute data and Codex sessions paths. Check that the database
has no `memory.sqlite-journal`, `memory.sqlite-wal`, or `memory.sqlite-shm` file.
If one remains, reopen and close the database normally before trying again.
This command keeps a copy of the current database before it puts the backup
in place.

```bash
tm_backup="$tm_backup_dir/memory.sqlite"
thirdminute stop &&
  test ! -e "$tm_data/memory.sqlite-journal" &&
  test ! -e "$tm_data/memory.sqlite-wal" &&
  test ! -e "$tm_data/memory.sqlite-shm" &&
  tm_restore_dir=$(mktemp -d "$tm_data/restore.XXXXXX") &&
  cp -- "$tm_data/memory.sqlite" "$tm_restore_dir/before-restore.sqlite" &&
  install -m 600 -- "$tm_backup" "$tm_restore_dir/memory.sqlite" &&
  mv -- "$tm_restore_dir/memory.sqlite" "$tm_data/memory.sqlite" &&
  thirdminute status
```

The backup contains the saved learning and worker model settings. Check them
in `status` before opening a chat. Open a fresh chat to check recall, then
start the host when you are ready to process source again.

## Uninstall

Exit participating Codex chats and run these commands.

```bash
thirdminute disable &&
  codex plugin remove thirdminute@thirdminute-local &&
  codex plugin marketplace remove thirdminute-local
```

Codex removes the installed plugin. Thirdminute's data stays in `$tm_data`.

## Software license

The original Thirdminute software is offered under the PolyForm Strict License
1.0.0. The license permits noncommercial use and the institutional uses it
lists. Permission to modify or redistribute Thirdminute requires a separate
grant. See the `LICENSE` file included with the release.
[PolyForm Strict License 1.0.0](https://polyformproject.org/licenses/strict/1.0.0)

The bundled Codex material carries Apache License 2.0 terms. [Third-party notice](NOTICE)
