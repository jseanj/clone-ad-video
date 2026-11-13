#!/usr/bin/env bash
# Proxy launcher; preserve argument boundaries and dynamically locate clone-any-video engine.
set -euo pipefail

# 1. Allow explicit binary override
if [[ -n "${CAV_BIN:-}" && -x "$CAV_BIN" ]]; then
  TARGET_BIN="$CAV_BIN"
# 2. Check if clone-any-video is directly available in PATH
elif command -v clone-any-video >/dev/null 2>&1; then
  TARGET_BIN="$(command -v clone-any-video)"
else
  # 3. Dynamically discover CAV_WORKSPACE
  SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
  REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

  CANDIDATE_DIRS=(
    "${CAV_WORKSPACE:-}"
    "${CLONE_ANY_VIDEO_HOME:-}"
    "${CLONE_ANY_VIDEO_PATH:-}"
    "$REPO_ROOT/../workspace/clone-any-video"
    "$REPO_ROOT/../clone-any-video"
    "$HOME/code/workspace/clone-any-video"
    "$HOME/code/clone-any-video"
  )

  FOUND_WORKSPACE=""
  for dir in "${CANDIDATE_DIRS[@]}"; do
    if [[ -n "$dir" && -d "$dir" && -f "$dir/Cargo.toml" ]]; then
      FOUND_WORKSPACE="$(cd "$dir" && pwd)"
      break
    fi
  done

  if [[ -z "$FOUND_WORKSPACE" ]]; then
    echo "Error: clone-any-video engine could not be found." >&2
    echo "To install clone-any-video, please follow the guide at:" >&2
    echo "  https://github.com/jseanj/clone-any-video" >&2
    echo "" >&2
    echo "If clone-any-video is already installed elsewhere, set CAV_WORKSPACE or CAV_BIN:" >&2
    echo "  export CAV_WORKSPACE=/path/to/clone-any-video" >&2
    echo "  export CAV_BIN=/path/to/clone-any-video/target/release/clone-any-video" >&2
    exit 1
  fi
  CAV_WORKSPACE="$FOUND_WORKSPACE"

  if [[ -x "$CAV_WORKSPACE/target/release/clone-any-video" ]]; then
    TARGET_BIN="$CAV_WORKSPACE/target/release/clone-any-video"
  elif [[ -x "$CAV_WORKSPACE/target/debug/clone-any-video" ]]; then
    TARGET_BIN="$CAV_WORKSPACE/target/debug/clone-any-video"
  else
    TARGET_BIN="cargo run --manifest-path $CAV_WORKSPACE/Cargo.toml --bin clone-any-video --"
  fi
fi

# Load environment / credentials if present
CAV_CONFIG_PATH="${CAV_ENV_FILE:-${CAV_WORKSPACE:-}/.env.local}"
if [[ -n "${CAV_ENV_FILE:-}" && ! -f "$CAV_CONFIG_PATH" ]]; then
  echo "CAV_ENV_FILE does not exist: $CAV_CONFIG_PATH" >&2
  exit 1
fi
if [[ -f "$CAV_CONFIG_PATH" ]]; then
  set -a
  source "$CAV_CONFIG_PATH"
  set +a
elif [[ -f "./.env.local" ]]; then
  set -a
  source "./.env.local"
  set +a
fi

if [[ "$TARGET_BIN" == cargo* ]]; then
  exec $TARGET_BIN "$@"
else
  exec "$TARGET_BIN" "$@"
fi
