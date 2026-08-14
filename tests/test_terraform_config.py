"""Static checks for the Terraform configuration in ``terraform/``."""

import re

import pytest

from conftest import hcl_blocks

AAP_MIN_OS_DISK_GB = 64


@pytest.fixture(scope="session")
def variables(terraform_config):
    return dict(hcl_blocks(terraform_config, "variable"))


@pytest.fixture(scope="session")
def outputs(terraform_config):
    return dict(hcl_blocks(terraform_config, "output"))


@pytest.fixture(scope="session")
def resources(terraform_config):
    """Map ``type.name`` to the resource body."""
    found = {}
    for resource_type, instances in hcl_blocks(terraform_config, "resource"):
        for name, body in instances.items():
            found[f"{resource_type}.{name}"] = body
    return found


def test_provider_and_version_constraints_are_pinned(terraform_config):
    settings = terraform_config["terraform"][0]
    assert settings["required_version"].startswith(">=")
    azurerm = settings["required_providers"][0]["azurerm"]
    assert azurerm["source"] == "hashicorp/azurerm"
    assert azurerm["version"].startswith("~>"), "azurerm version must be constrained"


def test_every_variable_declares_a_type_and_description(variables):
    for name, body in variables.items():
        assert body.get("type"), f"variable '{name}' has no type"
        assert body.get("description"), f"variable '{name}' has no description"


def test_every_output_declares_a_description(outputs):
    for name, body in outputs.items():
        assert body.get("description"), f"output '{name}' has no description"


def test_outputs_reference_declared_resources_and_variables(outputs, resources, variables):
    for name, body in outputs.items():
        value = str(body["value"])
        for reference in re.findall(r"\b(azurerm_[a-z0-9_]+)\.([a-z0-9_]+)\b", value):
            address = ".".join(reference)
            assert address in resources, f"output '{name}' references unknown {address}"
        for variable in re.findall(r"\bvar\.([a-z0-9_]+)\b", value):
            assert variable in variables, f"output '{name}' references unknown var.{variable}"


def test_core_infrastructure_resources_are_declared(resources):
    expected = {
        "azurerm_resource_group.rg",
        "azurerm_virtual_network.vnet",
        "azurerm_subnet.subnet",
        "azurerm_public_ip.public_ip",
        "azurerm_network_security_group.nsg",
        "azurerm_network_interface.nic",
        "azurerm_network_interface_security_group_association.nic_nsg",
        "azurerm_linux_virtual_machine.vm",
    }
    assert expected <= set(resources)


def test_network_security_group_rules_are_well_formed(resources):
    rules = resources["azurerm_network_security_group.nsg"]["security_rule"]
    priorities = [rule["priority"] for rule in rules]
    assert len(priorities) == len(set(priorities)), "NSG rule priorities must be unique"
    for rule in rules:
        assert rule["direction"] in ("Inbound", "Outbound")
        assert rule["access"] in ("Allow", "Deny")
        assert rule["protocol"] in ("Tcp", "Udp", "Icmp", "*")


def test_ssh_access_is_restrictable_by_variable(resources, variables):
    rules = resources["azurerm_network_security_group.nsg"]["security_rule"]
    ssh_rules = [rule for rule in rules if str(rule["destination_port_range"]) == "22"]
    assert ssh_rules, "no inbound SSH rule is defined"
    for rule in ssh_rules:
        assert "var.allowed_ssh_source_ip" in str(rule["source_address_prefix"]), (
            "the SSH rule must take its source range from var.allowed_ssh_source_ip"
        )
    assert "allowed_ssh_source_ip" in variables


def test_aap_controller_vm_meets_platform_requirements(resources, variables):
    vm = resources["azurerm_linux_virtual_machine.vm"]
    assert "var.vm_size" in str(vm["size"])
    assert variables["vm_size"]["default"] == "Standard_D4s_v5", (
        "AAP requires at least 4 vCPUs and 16 GB RAM"
    )
    os_disk = vm["os_disk"][0] if isinstance(vm["os_disk"], list) else vm["os_disk"]
    assert int(os_disk["disk_size_gb"]) >= AAP_MIN_OS_DISK_GB
    image = (
        vm["source_image_reference"][0]
        if isinstance(vm["source_image_reference"], list)
        else vm["source_image_reference"]
    )
    assert image["publisher"] == "RedHat" and image["offer"] == "RHEL"
    assert image["sku"].startswith("9-"), "the playbooks target RHEL 9"


def test_vm_uses_ssh_keys_and_no_password_authentication(resources):
    vm = resources["azurerm_linux_virtual_machine.vm"]
    assert "admin_ssh_key" in vm, "the VM must be provisioned with an SSH key"
    assert "admin_password" not in vm
    assert vm.get("disable_password_authentication", True) is not False


def test_network_addressing_is_consistent(resources):
    vnet = resources["azurerm_virtual_network.vnet"]
    subnet = resources["azurerm_subnet.subnet"]
    assert "var.vnet_address_space" in str(vnet["address_space"])
    assert "var.subnet_address_prefix" in str(subnet["address_prefixes"])
    assert "azurerm_virtual_network.vnet.name" in str(subnet["virtual_network_name"])


def test_public_ip_supports_a_standard_load_balanced_setup(resources):
    public_ip = resources["azurerm_public_ip.public_ip"]
    assert public_ip["allocation_method"] == "Static"
    assert public_ip["sku"] == "Standard"
    assert "var.public_ip_dns_label" in str(public_ip["domain_name_label"])
