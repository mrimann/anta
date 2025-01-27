<!--
  ~ Copyright (c) 2023-2024 Arista Networks, Inc.
  ~ Use of this source code is governed by the Apache License 2.0
  ~ that can be found in the LICENSE file.
  -->

# Frequently Asked Questions (FAQ)

## Why am I seeing an `ImportError` related to `urllib3` when running ANTA?

When running the `anta --help` command, some users might encounter the following error:

```bash
ImportError: urllib3 v2.0 only supports OpenSSL 1.1.1+, currently the 'ssl' module is compiled with 'OpenSSL 1.0.2k-fips  26 Jan 2017'. See: https://github.com/urllib3/urllib3/issues/2168
```

This error arises due to a compatibility issue between `urllib3` v2.0 and older versions of OpenSSL.

#### How can I resolve this error?

1. _Workaround_: Downgrade `urllib3`

    If you need a quick fix, you can temporarily downgrade the `urllib3` package:

    ```bash
    pip3 uninstall urllib3

    pip3 install urllib3==1.26.15
    ```

2. _Recommended_: Upgrade System or Libraries:

    As per the [urllib3 v2 migration guide](https://urllib3.readthedocs.io/en/latest/v2-migration-guide.html), the root cause of this error is an incompatibility with older OpenSSL versions. For example, users on RHEL7 might consider upgrading to RHEL8, which supports the required OpenSSL version.

## Why am I seeing `AttributeError: module 'lib' has no attribute 'OpenSSL_add_all_algorithms'` when running ANTA

When running the `anta` commands after installation, some users might encounter the following error:

```bash
AttributeError: module 'lib' has no attribute 'OpenSSL_add_all_algorithms'
```

The error is a result of incompatibility between `cryptography` and `pyopenssl` when installing `asyncssh` which is a requirement of ANTA.

#### How can I resolve this error?

1. Upgrade `pyopenssl`

    ```bash
    pip install -U pyopenssl>22.0
    ```

## `__NSCFConstantString initialize` error on OSX

This error occurs because of added security to restrict multithreading in macOS High Sierra and later versions of macOS. https://www.wefearchange.org/2018/11/forkmacos.rst.html

#### How can I resolve this error?

1. Set the following environment variable

    ```bash
    export OBJC_DISABLE_INITIALIZE_FORK_SAFETY=YES
    ```

## Still facing issues?

If you've tried the above solutions and continue to experience problems, please report the issue in our [GitHub repository](https://github.com/arista-netdevops-community/anta).
