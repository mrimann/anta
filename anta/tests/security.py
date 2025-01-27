# Copyright (c) 2023-2024 Arista Networks, Inc.
# Use of this source code is governed by the Apache License 2.0
# that can be found in the LICENSE file.
"""Module related to the EOS various security tests."""

from __future__ import annotations

# Mypy does not understand AntaTest.Input typing
# mypy: disable-error-code=attr-defined
from datetime import datetime, timezone
from typing import ClassVar

from pydantic import BaseModel, Field, model_validator

from anta.custom_types import EcdsaKeySize, EncryptionAlgorithm, PositiveInteger, RsaKeySize
from anta.models import AntaCommand, AntaTemplate, AntaTest
from anta.tools.get_item import get_item
from anta.tools.get_value import get_value
from anta.tools.utils import get_failed_logs


class VerifySSHStatus(AntaTest):
    """Verifies if the SSHD agent is disabled in the default VRF.

    Expected Results
    ----------------
    * Success: The test will pass if the SSHD agent is disabled in the default VRF.
    * Failure: The test will fail if the SSHD agent is NOT disabled in the default VRF.

    Examples
    --------
    ```yaml
    anta.tests.security:
      - VerifySSHStatus:
    ```
    """

    name = "VerifySSHStatus"
    description = "Verifies if the SSHD agent is disabled in the default VRF."
    categories: ClassVar[list[str]] = ["security"]
    commands: ClassVar[list[AntaCommand | AntaTemplate]] = [AntaCommand(command="show management ssh", ofmt="text")]

    @AntaTest.anta_test
    def test(self) -> None:
        """Main test function for VerifySSHStatus."""
        command_output = self.instance_commands[0].text_output

        line = next(line for line in command_output.split("\n") if line.startswith("SSHD status"))
        status = line.split("is ")[1]

        if status == "disabled":
            self.result.is_success()
        else:
            self.result.is_failure(line)


class VerifySSHIPv4Acl(AntaTest):
    """Verifies if the SSHD agent has the right number IPv4 ACL(s) configured for a specified VRF.

    Expected Results
    ----------------
    * Success: The test will pass if the SSHD agent has the provided number of IPv4 ACL(s) in the specified VRF.
    * Failure: The test will fail if the SSHD agent has not the right number of IPv4 ACL(s) in the specified VRF.

    Examples
    --------
    ```yaml
    anta.tests.security:
      - VerifySSHIPv4Acl:
          number: 3
          vrf: default
    ```
    """

    name = "VerifySSHIPv4Acl"
    description = "Verifies if the SSHD agent has IPv4 ACL(s) configured."
    categories: ClassVar[list[str]] = ["security"]
    commands: ClassVar[list[AntaCommand | AntaTemplate]] = [AntaCommand(command="show management ssh ip access-list summary")]

    class Input(AntaTest.Input):
        """Input model for the VerifySSHIPv4Acl test."""

        number: PositiveInteger
        """The number of expected IPv4 ACL(s)."""
        vrf: str = "default"
        """The name of the VRF in which to check for the SSHD agent. Defaults to `default` VRF."""

    @AntaTest.anta_test
    def test(self) -> None:
        """Main test function for VerifySSHIPv4Acl."""
        command_output = self.instance_commands[0].json_output
        ipv4_acl_list = command_output["ipAclList"]["aclList"]
        ipv4_acl_number = len(ipv4_acl_list)
        if ipv4_acl_number != self.inputs.number:
            self.result.is_failure(f"Expected {self.inputs.number} SSH IPv4 ACL(s) in vrf {self.inputs.vrf} but got {ipv4_acl_number}")
            return

        not_configured_acl = [acl["name"] for acl in ipv4_acl_list if self.inputs.vrf not in acl["configuredVrfs"] or self.inputs.vrf not in acl["activeVrfs"]]

        if not_configured_acl:
            self.result.is_failure(f"SSH IPv4 ACL(s) not configured or active in vrf {self.inputs.vrf}: {not_configured_acl}")
        else:
            self.result.is_success()


class VerifySSHIPv6Acl(AntaTest):
    """Verifies if the SSHD agent has the right number IPv6 ACL(s) configured for a specified VRF.

    Expected Results
    ----------------
    * Success: The test will pass if the SSHD agent has the provided number of IPv6 ACL(s) in the specified VRF.
    * Failure: The test will fail if the SSHD agent has not the right number of IPv6 ACL(s) in the specified VRF.

    Examples
    --------
    ```yaml
    anta.tests.security:
      - VerifySSHIPv6Acl:
          number: 3
          vrf: default
    ```
    """

    name = "VerifySSHIPv6Acl"
    description = "Verifies if the SSHD agent has IPv6 ACL(s) configured."
    categories: ClassVar[list[str]] = ["security"]
    commands: ClassVar[list[AntaCommand | AntaTemplate]] = [AntaCommand(command="show management ssh ipv6 access-list summary")]

    class Input(AntaTest.Input):
        """Input model for the VerifySSHIPv6Acl test."""

        number: PositiveInteger
        """The number of expected IPv6 ACL(s)."""
        vrf: str = "default"
        """The name of the VRF in which to check for the SSHD agent. Defaults to `default` VRF."""

    @AntaTest.anta_test
    def test(self) -> None:
        """Main test function for VerifySSHIPv6Acl."""
        command_output = self.instance_commands[0].json_output
        ipv6_acl_list = command_output["ipv6AclList"]["aclList"]
        ipv6_acl_number = len(ipv6_acl_list)
        if ipv6_acl_number != self.inputs.number:
            self.result.is_failure(f"Expected {self.inputs.number} SSH IPv6 ACL(s) in vrf {self.inputs.vrf} but got {ipv6_acl_number}")
            return

        not_configured_acl = [acl["name"] for acl in ipv6_acl_list if self.inputs.vrf not in acl["configuredVrfs"] or self.inputs.vrf not in acl["activeVrfs"]]

        if not_configured_acl:
            self.result.is_failure(f"SSH IPv6 ACL(s) not configured or active in vrf {self.inputs.vrf}: {not_configured_acl}")
        else:
            self.result.is_success()


class VerifyTelnetStatus(AntaTest):
    """Verifies if Telnet is disabled in the default VRF.

    Expected Results
    ----------------
    * Success: The test will pass if Telnet is disabled in the default VRF.
    * Failure: The test will fail if Telnet is NOT disabled in the default VRF.

    Examples
    --------
    ```yaml
    anta.tests.security:
      - VerifyTelnetStatus:
    ```
    """

    name = "VerifyTelnetStatus"
    description = "Verifies if Telnet is disabled in the default VRF."
    categories: ClassVar[list[str]] = ["security"]
    commands: ClassVar[list[AntaCommand | AntaTemplate]] = [AntaCommand(command="show management telnet")]

    @AntaTest.anta_test
    def test(self) -> None:
        """Main test function for VerifyTelnetStatus."""
        command_output = self.instance_commands[0].json_output
        if command_output["serverState"] == "disabled":
            self.result.is_success()
        else:
            self.result.is_failure("Telnet status for Default VRF is enabled")


class VerifyAPIHttpStatus(AntaTest):
    """Verifies if eAPI HTTP server is disabled globally.

    Expected Results
    ----------------
    * Success: The test will pass if eAPI HTTP server is disabled globally.
    * Failure: The test will fail if eAPI HTTP server is NOT disabled globally.

    Examples
    --------
    ```yaml
    anta.tests.security:
      - VerifyAPIHttpStatus:
    ```
    """

    name = "VerifyAPIHttpStatus"
    description = "Verifies if eAPI HTTP server is disabled globally."
    categories: ClassVar[list[str]] = ["security"]
    commands: ClassVar[list[AntaCommand | AntaTemplate]] = [AntaCommand(command="show management api http-commands")]

    @AntaTest.anta_test
    def test(self) -> None:
        """Main test function for VerifyAPIHttpStatus."""
        command_output = self.instance_commands[0].json_output
        if command_output["enabled"] and not command_output["httpServer"]["running"]:
            self.result.is_success()
        else:
            self.result.is_failure("eAPI HTTP server is enabled globally")


class VerifyAPIHttpsSSL(AntaTest):
    """Verifies if eAPI HTTPS server SSL profile is configured and valid.

    Expected Results
    ----------------
    * Success: The test will pass if the eAPI HTTPS server SSL profile is configured and valid.
    * Failure: The test will fail if the eAPI HTTPS server SSL profile is NOT configured, misconfigured or invalid.

    Examples
    --------
    ```yaml
    anta.tests.security:
      - VerifyAPIHttpsSSL:
          profile: default
    ```
    """

    name = "VerifyAPIHttpsSSL"
    description = "Verifies if the eAPI has a valid SSL profile."
    categories: ClassVar[list[str]] = ["security"]
    commands: ClassVar[list[AntaCommand | AntaTemplate]] = [AntaCommand(command="show management api http-commands")]

    class Input(AntaTest.Input):
        """Input model for the VerifyAPIHttpsSSL test."""

        profile: str
        """SSL profile to verify."""

    @AntaTest.anta_test
    def test(self) -> None:
        """Main test function for VerifyAPIHttpsSSL."""
        command_output = self.instance_commands[0].json_output
        try:
            if command_output["sslProfile"]["name"] == self.inputs.profile and command_output["sslProfile"]["state"] == "valid":
                self.result.is_success()
            else:
                self.result.is_failure(f"eAPI HTTPS server SSL profile ({self.inputs.profile}) is misconfigured or invalid")

        except KeyError:
            self.result.is_failure(f"eAPI HTTPS server SSL profile ({self.inputs.profile}) is not configured")


class VerifyAPIIPv4Acl(AntaTest):
    """Verifies if eAPI has the right number IPv4 ACL(s) configured for a specified VRF.

    Expected Results
    ----------------
    * Success: The test will pass if eAPI has the provided number of IPv4 ACL(s) in the specified VRF.
    * Failure: The test will fail if eAPI has not the right number of IPv4 ACL(s) in the specified VRF.

    Examples
    --------
    ```yaml
    anta.tests.security:
      - VerifyAPIIPv4Acl:
          number: 3
          vrf: default
    ```
    """

    name = "VerifyAPIIPv4Acl"
    description = "Verifies if eAPI has the right number IPv4 ACL(s) configured for a specified VRF."
    categories: ClassVar[list[str]] = ["security"]
    commands: ClassVar[list[AntaCommand | AntaTemplate]] = [AntaCommand(command="show management api http-commands ip access-list summary")]

    class Input(AntaTest.Input):
        """Input parameters for the VerifyAPIIPv4Acl test."""

        number: PositiveInteger
        """The number of expected IPv4 ACL(s)."""
        vrf: str = "default"
        """The name of the VRF in which to check for eAPI. Defaults to `default` VRF."""

    @AntaTest.anta_test
    def test(self) -> None:
        """Main test function for VerifyAPIIPv4Acl."""
        command_output = self.instance_commands[0].json_output
        ipv4_acl_list = command_output["ipAclList"]["aclList"]
        ipv4_acl_number = len(ipv4_acl_list)
        if ipv4_acl_number != self.inputs.number:
            self.result.is_failure(f"Expected {self.inputs.number} eAPI IPv4 ACL(s) in vrf {self.inputs.vrf} but got {ipv4_acl_number}")
            return

        not_configured_acl = [acl["name"] for acl in ipv4_acl_list if self.inputs.vrf not in acl["configuredVrfs"] or self.inputs.vrf not in acl["activeVrfs"]]

        if not_configured_acl:
            self.result.is_failure(f"eAPI IPv4 ACL(s) not configured or active in vrf {self.inputs.vrf}: {not_configured_acl}")
        else:
            self.result.is_success()


class VerifyAPIIPv6Acl(AntaTest):
    """Verifies if eAPI has the right number IPv6 ACL(s) configured for a specified VRF.

    Expected Results
    ----------------
    * Success: The test will pass if eAPI has the provided number of IPv6 ACL(s) in the specified VRF.
    * Failure: The test will fail if eAPI has not the right number of IPv6 ACL(s) in the specified VRF.
    * Skipped: The test will be skipped if the number of IPv6 ACL(s) or VRF parameter is not provided.

    Examples
    --------
    ```yaml
    anta.tests.security:
      - VerifyAPIIPv6Acl:
          number: 3
          vrf: default
    ```
    """

    name = "VerifyAPIIPv6Acl"
    description = "Verifies if eAPI has the right number IPv6 ACL(s) configured for a specified VRF."
    categories: ClassVar[list[str]] = ["security"]
    commands: ClassVar[list[AntaCommand | AntaTemplate]] = [AntaCommand(command="show management api http-commands ipv6 access-list summary")]

    class Input(AntaTest.Input):
        """Input parameters for the VerifyAPIIPv6Acl test."""

        number: PositiveInteger
        """The number of expected IPv6 ACL(s)."""
        vrf: str = "default"
        """The name of the VRF in which to check for eAPI. Defaults to `default` VRF."""

    @AntaTest.anta_test
    def test(self) -> None:
        """Main test function for VerifyAPIIPv6Acl."""
        command_output = self.instance_commands[0].json_output
        ipv6_acl_list = command_output["ipv6AclList"]["aclList"]
        ipv6_acl_number = len(ipv6_acl_list)
        if ipv6_acl_number != self.inputs.number:
            self.result.is_failure(f"Expected {self.inputs.number} eAPI IPv6 ACL(s) in vrf {self.inputs.vrf} but got {ipv6_acl_number}")
            return

        not_configured_acl = [acl["name"] for acl in ipv6_acl_list if self.inputs.vrf not in acl["configuredVrfs"] or self.inputs.vrf not in acl["activeVrfs"]]

        if not_configured_acl:
            self.result.is_failure(f"eAPI IPv6 ACL(s) not configured or active in vrf {self.inputs.vrf}: {not_configured_acl}")
        else:
            self.result.is_success()


class VerifyAPISSLCertificate(AntaTest):
    """Verifies the eAPI SSL certificate expiry, common subject name, encryption algorithm and key size.

    Expected Results
    ----------------
    * Success: The test will pass if the certificate's expiry date is greater than the threshold,
                   and the certificate has the correct name, encryption algorithm, and key size.
    * Failure: The test will fail if the certificate is expired or is going to expire,
                   or if the certificate has an incorrect name, encryption algorithm, or key size.

    Examples
    --------
    ```yaml
    anta.tests.security:
      - VerifyAPISSLCertificate:
          certificates:
            - certificate_name: ARISTA_SIGNING_CA.crt
              expiry_threshold: 30
              common_name: AristaIT-ICA ECDSA Issuing Cert Authority
              encryption_algorithm: ECDSA
              key_size: 256
            - certificate_name: ARISTA_ROOT_CA.crt
              expiry_threshold: 30
              common_name: Arista Networks Internal IT Root Cert Authority
              encryption_algorithm: RSA
              key_size: 4096
    ```
    """

    name = "VerifyAPISSLCertificate"
    description = "Verifies the eAPI SSL certificate expiry, common subject name, encryption algorithm and key size."
    categories: ClassVar[list[str]] = ["security"]
    commands: ClassVar[list[AntaCommand | AntaTemplate]] = [AntaCommand(command="show management security ssl certificate"), AntaCommand(command="show clock")]

    class Input(AntaTest.Input):
        """Input parameters for the VerifyAPISSLCertificate test."""

        certificates: list[APISSLCertificate]
        """List of API SSL certificates."""

        class APISSLCertificate(BaseModel):
            """Model for an API SSL certificate."""

            certificate_name: str
            """The name of the certificate to be verified."""
            expiry_threshold: int
            """The expiry threshold of the certificate in days."""
            common_name: str
            """The common subject name of the certificate."""
            encryption_algorithm: EncryptionAlgorithm
            """The encryption algorithm of the certificate."""
            key_size: RsaKeySize | EcdsaKeySize
            """The encryption algorithm key size of the certificate."""

            @model_validator(mode="after")
            def validate_inputs(self: BaseModel) -> BaseModel:
                """Validate the key size provided to the APISSLCertificates class.

                If encryption_algorithm is RSA then key_size should be in {2048, 3072, 4096}.

                If encryption_algorithm is ECDSA then key_size should be in {256, 384, 521}.
                """
                if self.encryption_algorithm == "RSA" and self.key_size not in RsaKeySize.__args__:
                    msg = f"`{self.certificate_name}` key size {self.key_size} is invalid for RSA encryption. Allowed sizes are {RsaKeySize.__args__}."
                    raise ValueError(msg)

                if self.encryption_algorithm == "ECDSA" and self.key_size not in EcdsaKeySize.__args__:
                    msg = f"`{self.certificate_name}` key size {self.key_size} is invalid for ECDSA encryption. Allowed sizes are {EcdsaKeySize.__args__}."
                    raise ValueError(msg)

                return self

    @AntaTest.anta_test
    def test(self) -> None:
        """Main test function for VerifyAPISSLCertificate."""
        # Mark the result as success by default
        self.result.is_success()

        # Extract certificate and clock output
        certificate_output = self.instance_commands[0].json_output
        clock_output = self.instance_commands[1].json_output
        current_timestamp = clock_output["utcTime"]

        # Iterate over each API SSL certificate
        for certificate in self.inputs.certificates:
            # Collecting certificate expiry time and current EOS time.
            # These times are used to calculate the number of days until the certificate expires.
            if not (certificate_data := get_value(certificate_output, f"certificates..{certificate.certificate_name}", separator="..")):
                self.result.is_failure(f"SSL certificate '{certificate.certificate_name}', is not configured.\n")
                continue

            expiry_time = certificate_data["notAfter"]
            day_difference = (datetime.fromtimestamp(expiry_time, tz=timezone.utc) - datetime.fromtimestamp(current_timestamp, tz=timezone.utc)).days

            # Verify certificate expiry
            if 0 < day_difference < certificate.expiry_threshold:
                self.result.is_failure(f"SSL certificate `{certificate.certificate_name}` is about to expire in {day_difference} days.\n")
            elif day_difference < 0:
                self.result.is_failure(f"SSL certificate `{certificate.certificate_name}` is expired.\n")

            # Verify certificate common subject name, encryption algorithm and key size
            keys_to_verify = ["subject.commonName", "publicKey.encryptionAlgorithm", "publicKey.size"]
            actual_certificate_details = {key: get_value(certificate_data, key) for key in keys_to_verify}

            expected_certificate_details = {
                "subject.commonName": certificate.common_name,
                "publicKey.encryptionAlgorithm": certificate.encryption_algorithm,
                "publicKey.size": certificate.key_size,
            }

            if actual_certificate_details != expected_certificate_details:
                failed_log = f"SSL certificate `{certificate.certificate_name}` is not configured properly:"
                failed_log += get_failed_logs(expected_certificate_details, actual_certificate_details)
                self.result.is_failure(f"{failed_log}\n")


class VerifyBannerLogin(AntaTest):
    """Verifies the login banner of a device.

    Expected Results
    ----------------
    * Success: The test will pass if the login banner matches the provided input.
    * Failure: The test will fail if the login banner does not match the provided input.

    Examples
    --------
    ```yaml
    anta.tests.security:
      - VerifyBannerLogin:
            login_banner: |
                # Copyright (c) 2023-2024 Arista Networks, Inc.
                # Use of this source code is governed by the Apache License 2.0
                # that can be found in the LICENSE file.
    ```
    """

    name = "VerifyBannerLogin"
    description = "Verifies the login banner of a device."
    categories: ClassVar[list[str]] = ["security"]
    commands: ClassVar[list[AntaCommand | AntaTemplate]] = [AntaCommand(command="show banner login")]

    class Input(AntaTest.Input):
        """Input model for the VerifyBannerLogin test."""

        login_banner: str
        """Expected login banner of the device."""

    @AntaTest.anta_test
    def test(self) -> None:
        """Main test function for VerifyBannerLogin."""
        login_banner = self.instance_commands[0].json_output["loginBanner"]

        # Remove leading and trailing whitespaces from each line
        cleaned_banner = "\n".join(line.strip() for line in self.inputs.login_banner.split("\n"))
        if login_banner != cleaned_banner:
            self.result.is_failure(f"Expected `{cleaned_banner}` as the login banner, but found `{login_banner}` instead.")
        else:
            self.result.is_success()


class VerifyBannerMotd(AntaTest):
    """Verifies the motd banner of a device.

    Expected Results
    ----------------
    * Success: The test will pass if the motd banner matches the provided input.
    * Failure: The test will fail if the motd banner does not match the provided input.

    Examples
    --------
    ```yaml
    anta.tests.security:
      - VerifyBannerMotd:
            motd_banner: |
                # Copyright (c) 2023-2024 Arista Networks, Inc.
                # Use of this source code is governed by the Apache License 2.0
                # that can be found in the LICENSE file.
    ```
    """

    name = "VerifyBannerMotd"
    description = "Verifies the motd banner of a device."
    categories: ClassVar[list[str]] = ["security"]
    commands: ClassVar[list[AntaCommand | AntaTemplate]] = [AntaCommand(command="show banner motd")]

    class Input(AntaTest.Input):
        """Input model for the VerifyBannerMotd test."""

        motd_banner: str
        """Expected motd banner of the device."""

    @AntaTest.anta_test
    def test(self) -> None:
        """Main test function for VerifyBannerMotd."""
        motd_banner = self.instance_commands[0].json_output["motd"]

        # Remove leading and trailing whitespaces from each line
        cleaned_banner = "\n".join(line.strip() for line in self.inputs.motd_banner.split("\n"))
        if motd_banner != cleaned_banner:
            self.result.is_failure(f"Expected `{cleaned_banner}` as the motd banner, but found `{motd_banner}` instead.")
        else:
            self.result.is_success()


class VerifyIPv4ACL(AntaTest):
    """Verifies the configuration of IPv4 ACLs.

    Expected Results
    ----------------
    * Success: The test will pass if an IPv4 ACL is configured with the correct sequence entries.
    * Failure: The test will fail if an IPv4 ACL is not configured or entries are not in sequence.

    Examples
    --------
    ```yaml
    anta.tests.security:
      - VerifyIPv4ACL:
          ipv4_access_lists:
            - name: default-control-plane-acl
              entries:
                - sequence: 10
                  action: permit icmp any any
                - sequence: 20
                  action: permit ip any any tracked
                - sequence: 30
                  action: permit udp any any eq bfd ttl eq 255
            - name: LabTest
              entries:
                - sequence: 10
                  action: permit icmp any any
                - sequence: 20
                  action: permit tcp any any range 5900 5910
    ```
    """

    name = "VerifyIPv4ACL"
    description = "Verifies the configuration of IPv4 ACLs."
    categories: ClassVar[list[str]] = ["security"]
    commands: ClassVar[list[AntaCommand | AntaTemplate]] = [AntaTemplate(template="show ip access-lists {acl}")]

    class Input(AntaTest.Input):
        """Input model for the VerifyIPv4ACL test."""

        ipv4_access_lists: list[IPv4ACL]
        """List of IPv4 ACLs to verify."""

        class IPv4ACL(BaseModel):
            """Model for an IPv4 ACL."""

            name: str
            """Name of IPv4 ACL."""

            entries: list[IPv4ACLEntry]
            """List of IPv4 ACL entries."""

            class IPv4ACLEntry(BaseModel):
                """Model for an IPv4 ACL entry."""

                sequence: int = Field(ge=1, le=4294967295)
                """Sequence number of an ACL entry."""
                action: str
                """Action of an ACL entry."""

    def render(self, template: AntaTemplate) -> list[AntaCommand]:
        """Render the template for each input ACL."""
        return [template.render(acl=acl.name, entries=acl.entries) for acl in self.inputs.ipv4_access_lists]

    @AntaTest.anta_test
    def test(self) -> None:
        """Main test function for VerifyIPv4ACL."""
        self.result.is_success()
        for command_output in self.instance_commands:
            # Collecting input ACL details
            acl_name = command_output.params["acl"]
            acl_entries = command_output.params["entries"]

            # Check if ACL is configured
            ipv4_acl_list = command_output.json_output["aclList"]
            if not ipv4_acl_list:
                self.result.is_failure(f"{acl_name}: Not found")
                continue

            # Check if the sequence number is configured and has the correct action applied
            failed_log = f"{acl_name}:\n"
            for acl_entry in acl_entries:
                acl_seq = acl_entry.sequence
                acl_action = acl_entry.action
                if (actual_entry := get_item(ipv4_acl_list[0]["sequence"], "sequenceNumber", acl_seq)) is None:
                    failed_log += f"Sequence number `{acl_seq}` is not found.\n"
                    continue

                if actual_entry["text"] != acl_action:
                    failed_log += f"Expected `{acl_action}` as sequence number {acl_seq} action but found `{actual_entry['text']}` instead.\n"

            if failed_log != f"{acl_name}:\n":
                self.result.is_failure(f"{failed_log}")
