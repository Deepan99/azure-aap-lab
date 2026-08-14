"""Checks that credentials never get committed in playbooks or Terraform."""

import re

import pytest

from conftest import iter_tasks, load_yaml, playbook_paths, terraform_paths

PLAYBOOKS = playbook_paths()
PLAYBOOK_IDS = [path.name for path in PLAYBOOKS]

SECRET_VAR_PATTERN = re.compile(
    r"^\s*(?!#)[\w.]*(password|passwd|secret|api_key|access_token|private_key)[\w.]*\s*[:=]\s*(?P<value>\S.*)$",
    re.IGNORECASE,
)

# A secret assignment is acceptable when the value is templated, looked up from
# the environment, sourced from a vault variable, a documentation placeholder, a
# boolean/numeric toggle, or empty.
SAFE_VALUE_PATTERN = re.compile(
    r"""\{\{            # a Jinja template
      |lookup\(         # an env or file lookup
      |vault_           # a vault variable
      |\$\{             # a shell or Terraform interpolation
      |<[^>]+>          # a documentation placeholder such as <your_password>
      |^["']?(true|false|yes|no|none|null|\d+)["']?,?$
      |^["']["']$       # an explicitly empty value
    """,
    re.IGNORECASE | re.VERBOSE,
)


def decode_text(raw):
    """Decode repository text that may be stored as UTF-8 or UTF-16."""
    for encoding in ("utf-8-sig", "utf-16"):
        try:
            return raw.decode(encoding)
        except UnicodeDecodeError:
            continue
    return raw.decode("utf-8", errors="replace")


def secret_assignments(text):
    for lineno, line in enumerate(text.splitlines(), start=1):
        match = SECRET_VAR_PATTERN.match(line)
        if match and not SAFE_VALUE_PATTERN.search(match.group("value")):
            yield lineno, line.strip()


@pytest.mark.parametrize("playbook", PLAYBOOKS, ids=PLAYBOOK_IDS)
def test_playbooks_contain_no_literal_secrets(playbook):
    findings = list(secret_assignments(playbook.read_text(encoding="utf-8")))
    assert not findings, f"{playbook.name} assigns literal secrets: {findings}"


@pytest.mark.parametrize("path", terraform_paths(), ids=lambda path: path.name)
def test_terraform_contains_no_literal_secrets(path):
    findings = list(secret_assignments(path.read_text(encoding="utf-8")))
    assert not findings, f"{path.name} assigns literal secrets: {findings}"


@pytest.mark.parametrize("playbook", PLAYBOOKS, ids=PLAYBOOK_IDS)
def test_secret_prompts_are_not_echoed(playbook):
    for play in load_yaml(playbook):
        for prompt in play.get("vars_prompt") or []:
            name = prompt.get("name", "")
            if re.search(r"password|secret|token", name, re.IGNORECASE):
                assert prompt.get("private", True) is not False, (
                    f"{playbook.name}: vars_prompt '{name}' echoes a secret to the terminal"
                )


@pytest.mark.parametrize("playbook", PLAYBOOKS, ids=PLAYBOOK_IDS)
def test_files_holding_secrets_are_not_world_readable(playbook):
    """Generated inventories and credential files must not be readable by all users."""
    for play in load_yaml(playbook):
        for task in iter_tasks(play):
            for module in ("copy", "template", "ansible.builtin.copy", "ansible.builtin.template"):
                args = task.get(module)
                if not isinstance(args, dict):
                    continue
                body = str(args.get("content", "")) + str(args.get("src", ""))
                if not re.search(r"password|secret|token", body, re.IGNORECASE):
                    continue
                mode = str(args.get("mode", ""))
                assert mode in ("0600", "0640", "0400"), (
                    f"{playbook.name}: task '{task['name']}' writes credentials with "
                    f"mode {mode or 'unset'}"
                )


def test_vault_and_state_files_are_gitignored(repo_root):
    ignored = decode_text(repo_root.joinpath(".gitignore").read_bytes())
    for pattern in ("vault.yml", "*.vault", "*.tfstate", "*.tfstate.backup"):
        assert pattern in ignored, f".gitignore is missing {pattern}"


def test_no_unencrypted_vault_file_is_committed(repo_root):
    for directory in ("playbooks", "ansible"):
        names = {path.name for path in repo_root.joinpath(directory).iterdir()}
        assert "vault.yml" not in names, f"an unencrypted vault.yml is committed in {directory}/"


def test_vault_example_only_contains_placeholders(repo_root):
    example = repo_root.joinpath("playbooks/vault.yml.example").read_text(encoding="utf-8")
    for _, line in secret_assignments(example):
        assert "your_" in line, f"vault.yml.example holds a real looking value: {line}"
