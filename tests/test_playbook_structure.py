"""Structural checks for the Ansible playbooks."""

import pytest
import yaml

from conftest import iter_tasks, load_yaml, playbook_paths

PLAYBOOKS = playbook_paths()
PLAYBOOK_IDS = [path.name for path in PLAYBOOKS]

# Keys that identify a task as something other than a module invocation.
TASK_METADATA_KEYS = {
    "name",
    "when",
    "become",
    "become_user",
    "register",
    "vars",
    "loop",
    "with_items",
    "with_fileglob",
    "tags",
    "ignore_errors",
    "failed_when",
    "changed_when",
    "notify",
    "until",
    "retries",
    "delay",
    "timeout",
    "async",
    "poll",
    "args",
    "delegate_to",
    "run_once",
    "no_log",
    "environment",
    "block",
    "rescue",
    "always",
    "listen",
    "loop_control",
}

DEPRECATED_KEYS = {"sudo", "sudo_user", "include", "with_flattened"}


@pytest.fixture(params=PLAYBOOKS, ids=PLAYBOOK_IDS)
def playbook(request):
    return request.param


def test_playbook_is_valid_yaml(playbook):
    with playbook.open(encoding="utf-8") as handle:
        yaml.safe_load(handle)


def test_playbook_is_a_list_of_plays(playbook):
    document = load_yaml(playbook)
    assert isinstance(document, list), f"{playbook.name} must be a list of plays"
    assert document, f"{playbook.name} must define at least one play"
    for play in document:
        assert isinstance(play, dict), f"{playbook.name} contains a non-mapping play"


def test_every_play_declares_name_hosts_and_tasks(playbook):
    for play in load_yaml(playbook):
        assert play.get("name"), f"{playbook.name} has a play without a name"
        assert play.get("hosts"), f"{playbook.name}: play '{play.get('name')}' has no hosts"
        assert play.get("tasks"), f"{playbook.name}: play '{play.get('name')}' has no tasks"


def test_every_task_is_named(playbook):
    for play in load_yaml(playbook):
        for task in iter_tasks(play):
            assert task.get("name"), (
                f"{playbook.name} contains an unnamed task: {sorted(task)}"
            )


def test_every_task_invokes_exactly_one_module(playbook):
    for play in load_yaml(playbook):
        for task in iter_tasks(play):
            if any(key in task for key in ("block", "rescue", "always")):
                continue
            modules = [key for key in task if key not in TASK_METADATA_KEYS]
            assert len(modules) == 1, (
                f"{playbook.name}: task '{task['name']}' invokes {modules}, "
                "expected exactly one module"
            )


def test_no_deprecated_task_keywords(playbook):
    for play in load_yaml(playbook):
        for task in iter_tasks(play):
            used = DEPRECATED_KEYS.intersection(task)
            assert not used, f"{playbook.name}: task '{task['name']}' uses {sorted(used)}"


def test_command_and_shell_tasks_are_idempotent(playbook):
    """``command``/``shell`` tasks must declare their change semantics.

    Without ``changed_when``, ``creates`` or a registered result these tasks
    report a change on every run, which breaks idempotence checks.
    """
    for play in load_yaml(playbook):
        for task in iter_tasks(play):
            for module in ("command", "shell", "ansible.builtin.command", "ansible.builtin.shell"):
                if module not in task:
                    continue
                args = task.get("args") or {}
                declares_change = (
                    "changed_when" in task
                    or "register" in task
                    or "creates" in args
                    or "removes" in args
                )
                assert declares_change, (
                    f"{playbook.name}: task '{task['name']}' uses {module} without "
                    "changed_when, creates/removes or register"
                )


def test_plays_targeting_remote_hosts_use_become(playbook):
    for play in load_yaml(playbook):
        if play["hosts"] in ("localhost", "127.0.0.1"):
            continue
        tasks = list(iter_tasks(play))
        privileged = any(
            key in task
            for task in tasks
            for key in ("dnf", "yum", "systemd", "service", "package")
        )
        if privileged:
            assert play.get("become") or any(task.get("become") for task in tasks), (
                f"{playbook.name}: play '{play['name']}' manages packages or services "
                "without become"
            )
