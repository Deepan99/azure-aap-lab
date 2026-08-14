#!/bin/bash
# Fail if a credential looks hardcoded in the Ansible content.
#
# The previous inline CI check matched every "password:" line, including the
# templated references that are the correct pattern, so it had to be run with
# continue-on-error and never actually blocked anything. This version only
# reports values that are not templated, looked up, prompted or empty, so it can
# run as a blocking gate.
set -euo pipefail

paths=("${@:-playbooks ansible}")

# A value is suspicious when the key looks like a credential and the value is a
# literal (i.e. does not start with a Jinja expression or a lookup).
key_pattern='(password|passwd|secret|token|api_key|secret_key|access_token|private_key)[a-z_]*'
value_pattern='[[:space:]]*[:=][[:space:]]*("|'"'"')?[^"'"'"'<[:space:]{]'

findings=$(grep -rniE "${key_pattern}${value_pattern}" "${paths[@]}" \
  --include='*.yml' --include='*.yaml' \
  | grep -vE 'vault_|lookup\(|\{\{|_enabled|_file|prompt|private:|no_log|:[[:space:]]*(true|false|yes|no|omit|null|~)[[:space:]]*$' \
  || true)

if [[ -n "$findings" ]]; then
  echo "ERROR: potential hardcoded credentials found:"
  echo "$findings"
  echo
  echo "Use a vault variable, a lookup, or vars_prompt instead."
  exit 1
fi

echo "No hardcoded credentials found in: ${paths[*]}"
