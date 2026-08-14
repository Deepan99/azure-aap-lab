"""Shared fixtures and helpers for the static validation test suite."""

import re
from pathlib import Path

import hcl2
import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
PLAYBOOK_DIRS = ("playbooks", "ansible")

# YAML files in those directories that are configuration, not playbooks.
NON_PLAYBOOK_FILES = {"playbooks/azure_dynamic_inventory.yml"}


def playbook_paths():
    """Every Ansible playbook tracked in the repository, sorted for stable test ids."""
    paths = []
    for directory in PLAYBOOK_DIRS:
        for path in sorted((REPO_ROOT / directory).glob("*.yml")):
            if path.relative_to(REPO_ROOT).as_posix() not in NON_PLAYBOOK_FILES:
                paths.append(path)
    return paths


def terraform_paths():
    return sorted((REPO_ROOT / "terraform").glob("*.tf"))


def load_yaml(path):
    with path.open(encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def load_hcl(path):
    with path.open(encoding="utf-8") as handle:
        return normalize_hcl(hcl2.load(handle))


def normalize_hcl(node):
    """Strip the quoting and block markers that ``hcl2`` keeps around labels and strings."""
    if isinstance(node, dict):
        return {
            ".".join(block_labels(key)): normalize_hcl(value)
            for key, value in node.items()
            if key != "__is_block__"
        }
    if isinstance(node, list):
        return [normalize_hcl(item) for item in node]
    if isinstance(node, str):
        return unquote(node)
    return node


def unquote(value):
    if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
        return value[1:-1]
    return value


def block_labels(key):
    """Split an ``hcl2`` block key such as ``"azurerm_public_ip"."public_ip"`` into labels."""
    if key.startswith('"'):
        return re.findall(r'"([^"]*)"', key)
    return [key]


def iter_tasks(play):
    """Yield every task in a play, flattening block/rescue/always and handlers."""
    sections = ("pre_tasks", "tasks", "post_tasks", "handlers")
    for section in sections:
        yield from _flatten(play.get(section) or [])


def _flatten(tasks):
    for task in tasks:
        if not isinstance(task, dict):
            continue
        yield task
        for key in ("block", "rescue", "always"):
            yield from _flatten(task.get(key) or [])


def hcl_blocks(document, block_type):
    """Yield (address, body) pairs for a top level HCL block type such as ``variable``.

    The address is the block's labels joined by a dot, so a resource yields
    ``azurerm_public_ip.public_ip`` and a variable yields ``location``.
    """
    for block in document.get(block_type, []):
        for address, body in block.items():
            yield address, body


@pytest.fixture(scope="session")
def repo_root():
    return REPO_ROOT


@pytest.fixture(scope="session")
def terraform_config():
    """The merged Terraform configuration for the ``terraform/`` directory."""
    merged = {}
    for path in terraform_paths():
        for block_type, blocks in load_hcl(path).items():
            merged.setdefault(block_type, []).extend(blocks)
    return merged
