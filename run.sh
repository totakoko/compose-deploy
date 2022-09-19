#!/bin/sh -e

current_dir="$(dirname "$(readlink -f "$0")")"

usage() {
  echo "Usage: compose-deploy <command>"
  echo "Available commands:"
  echo "  - deploy : deploy the infrastructure"
  echo "  - exec <commands>... : run shell commands on the server"
  echo "  - run [-v local_bind:remote_bind...] <module> <service> <commands>... : run one-time commands against a service"
  echo "  - update-module <module> [services...] : update a specific module (and only some services if specified)"
  exit 1
}

update_ssh_configuration() {
  if [ -n "$SSH_FINGERPRINT_BASE64" ]; then
    export SSH_FINGERPRINT=$(echo $SSH_FINGERPRINT_BASE64 | base64 -d)
  fi
  if [ -z "$SSH_FINGERPRINT" ]; then
    echo "Missing environment variable SSH_FINGERPRINT"
    exit 1
  fi
  if [ -n "$SSH_PRIVATE_KEY_BASE64" ]; then
    export SSH_PRIVATE_KEY=$(echo $SSH_PRIVATE_KEY_BASE64 | base64 -d)
  fi
  if [ -z "$SSH_PRIVATE_KEY" ]; then
    echo "Missing environment variable SSH_PRIVATE_KEY"
    exit 1
  fi

  mkdir -p ~/.ssh
  chmod 700 ~/.ssh
  eval $(ssh-agent -s) > /dev/null
  if ! echo "$SSH_PRIVATE_KEY" | tr -d '\r' | ssh-add -; then
    echo "Could not load SSH_PRIVATE_KEY. Wrong format?"
    exit 1
  fi
  echo "$SSH_FINGERPRINT" >> ~/.ssh/known_hosts
}

if [ -z "$SSH_HOST" ]; then
  echo "Missing environment variable SSH_HOST"
  exit 1
fi
SSH_USER=${SSH_USER:-root}
SSH_PORT=${SSH_PORT:-22}
echo "$SSH_HOST ansible_port=$SSH_PORT remote_user=$SSH_USER" > "$current_dir"/inventory.ini

ANSIBLE_ARGS="${ANSIBLE_ARGS:-}"
export MODULES_ROOT="${MODULES_ROOT:-/modules}"
if [ -n "$GITLAB_CI" ]; then
  MODULES_ROOT="$CI_PROJECT_DIR"
fi
if [ -n "$CIRCLECI" ]; then
  # working directory is not expanded, see https://discuss.circleci.com/t/circle-working-directory-doesnt-expand/17007/5
  MODULES_ROOT="${CIRCLE_WORKING_DIRECTORY//\~/$HOME}"
fi

if [ -n "$SSH_FROM_ENV" ]; then
  update_ssh_configuration
fi

if [ -n "$CRYPT_KEY_BASE64" ]; then
  echo "Crypt key is defined. Unlocking project..."
  echo "$CRYPT_KEY_BASE64" | base64 -d > /tmp/key-file
  git-crypt unlock /tmp/key-file
fi

command=$1
echo "Running command: $command"
shift $(( $# > 0 ? 1 : 0 ))
case "$command" in
"deploy")
  ansible-playbook $ANSIBLE_ARGS "$current_dir"/playbooks/deploy.yml
  ;;

"exec")
  commands="$*"
  if [ -z "$commands" ]; then
    usage
  fi
  ansible-playbook ${ANSIBLE_ARGS:--v} -e commands="'$commands'" "$current_dir"/playbooks/exec.yml
  ;;

"run")
  mounts=""
  while getopts v: option; do
    case "${option}" in
    v) mounts="$mounts,${OPTARG}";;
    esac
  done
  shift "$((OPTIND-1))"
  mounts="${mounts:1}"
  module="$1"
  if [ -z "$module" ]; then
    usage
  fi
  service="$2"
  if [ -z "$service" ]; then
    usage
  fi
  shift $(( $# > 0 ? 2 : 0 ))
  escaped_commands=''
  for i in "$@"; do
    i="${i//\\/\\\\}"
    escaped_commands="$escaped_commands \"${i//\"/\\\"}\""
  done
  if [ -z "$escaped_commands" ]; then
    usage
  fi
  ansible-playbook ${ANSIBLE_ARGS:--v} -e rawmounts="'$mounts'" -e module="$module" -e service="$service" -e commands="'$escaped_commands'" "$current_dir"/playbooks/run.yml
  ;;

"update-module")
  module="$1"
  shift $(( $# > 0 ? 1 : 0 ))
  services="$*"
  if [ -z "$module" ]; then
    usage
  fi
  ansible-playbook $ANSIBLE_ARGS -e module="$module" -e services="'$services'" "$current_dir"/playbooks/update-module.yml
  ;;

*)
  usage
  ;;
esac
