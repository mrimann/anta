# Copyright (c) 2023-2024 Arista Networks, Inc.
# Use of this source code is governed by the Apache License 2.0
# that can be found in the LICENSE file.
"""Module related to various connectivity tests."""

# Mypy does not understand AntaTest.Input typing
# mypy: disable-error-code=attr-defined
from __future__ import annotations

from ipaddress import IPv4Address
from typing import ClassVar

from pydantic import BaseModel

from anta.custom_types import Interface
from anta.models import AntaCommand, AntaMissingParamError, AntaTemplate, AntaTest


class VerifyReachability(AntaTest):
    """Test network reachability to one or many destination IP(s).

    Expected Results
    ----------------
    * Success: The test will pass if all destination IP(s) are reachable.
    * Failure: The test will fail if one or many destination IP(s) are unreachable.

    Examples
    --------
    ```yaml
    anta.tests.connectivity:
      - VerifyReachability:
          hosts:
            - source: Management0
              destination: 1.1.1.1
              vrf: MGMT
            - source: Management0
              destination: 8.8.8.8
              vrf: MGMT
    ```
    """

    name = "VerifyReachability"
    description = "Test the network reachability to one or many destination IP(s)."
    categories: ClassVar[list[str]] = ["connectivity"]
    commands: ClassVar[list[AntaCommand | AntaTemplate]] = [AntaTemplate(template="ping vrf {vrf} {destination} source {source} repeat {repeat}")]

    class Input(AntaTest.Input):
        """Input model for the VerifyReachability test."""

        hosts: list[Host]
        """List of host to ping."""

        class Host(BaseModel):
            """Model for a remote host to ping."""

            destination: IPv4Address
            """IPv4 address to ping."""
            source: IPv4Address | Interface
            """IPv4 address source IP or egress interface to use."""
            vrf: str = "default"
            """VRF context. Defaults to `default`."""
            repeat: int = 2
            """Number of ping repetition. Defaults to 2."""

    def render(self, template: AntaTemplate) -> list[AntaCommand]:
        """Render the template for each host in the input list."""
        return [template.render(destination=host.destination, source=host.source, vrf=host.vrf, repeat=host.repeat) for host in self.inputs.hosts]

    @AntaTest.anta_test
    def test(self) -> None:
        """Main test function for VerifyReachability."""
        failures = []
        for command in self.instance_commands:
            src = command.params.get("source")
            dst = command.params.get("destination")
            repeat = command.params.get("repeat")

            if any(elem is None for elem in (src, dst, repeat)):
                msg = f"A parameter is missing to execute the test for command {command}"
                raise AntaMissingParamError(msg)

            if f"{repeat} received" not in command.json_output["messages"][0]:
                failures.append((str(src), str(dst)))

        if not failures:
            self.result.is_success()
        else:
            self.result.is_failure(f"Connectivity test failed for the following source-destination pairs: {failures}")


class VerifyLLDPNeighbors(AntaTest):
    """Verifies that the provided LLDP neighbors are present and connected with the correct configuration.

    Expected Results
    ----------------
    * Success: The test will pass if each of the provided LLDP neighbors is present and connected to the specified port and device.
    * Failure: The test will fail if any of the following conditions are met:
        - The provided LLDP neighbor is not found.
        - The system name or port of the LLDP neighbor does not match the provided information.

    Examples
    --------
    ```yaml
    anta.tests.connectivity:
      - VerifyLLDPNeighbors:
          neighbors:
            - port: Ethernet1
              neighbor_device: DC1-SPINE1
              neighbor_port: Ethernet1
            - port: Ethernet2
              neighbor_device: DC1-SPINE2
              neighbor_port: Ethernet1
    ```
    """

    name = "VerifyLLDPNeighbors"
    description = "Verifies that the provided LLDP neighbors are connected properly."
    categories: ClassVar[list[str]] = ["connectivity"]
    commands: ClassVar[list[AntaCommand | AntaTemplate]] = [AntaCommand(command="show lldp neighbors detail")]

    class Input(AntaTest.Input):
        """Input model for the VerifyLLDPNeighbors test."""

        neighbors: list[Neighbor]
        """List of LLDP neighbors."""

        class Neighbor(BaseModel):
            """Model for an LLDP neighbor."""

            port: Interface
            """LLDP port."""
            neighbor_device: str
            """LLDP neighbor device."""
            neighbor_port: Interface
            """LLDP neighbor port."""

    @AntaTest.anta_test
    def test(self) -> None:
        """Main test function for VerifyLLDPNeighbors."""
        command_output = self.instance_commands[0].json_output

        failures: dict[str, list[str]] = {}

        for neighbor in self.inputs.neighbors:
            if neighbor.port not in command_output["lldpNeighbors"]:
                failures.setdefault("port_not_configured", []).append(neighbor.port)
            elif len(lldp_neighbor_info := command_output["lldpNeighbors"][neighbor.port]["lldpNeighborInfo"]) == 0:
                failures.setdefault("no_lldp_neighbor", []).append(neighbor.port)
            elif (
                lldp_neighbor_info[0]["systemName"] != neighbor.neighbor_device
                or lldp_neighbor_info[0]["neighborInterfaceInfo"]["interfaceId_v2"] != neighbor.neighbor_port
            ):
                failures.setdefault("wrong_lldp_neighbor", []).append(neighbor.port)

        if not failures:
            self.result.is_success()
        else:
            self.result.is_failure(f"The following port(s) have issues: {failures}")
