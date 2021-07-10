#! /usr/bin/env python
# -*- coding: utf8 -*-
#
# Copyright (c) 2021 Víctor Molina García
#
# This file is part of get-pip-pyopenssl.
#
# get-pip-pyopenssl is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# get-pip-pyopenssl is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with get-pip-pyopenssl. If not, see <https://www.gnu.org/licenses/>.
#
"""Script to create alternative `get-pip.py` scripts that use `pyOpenSSL`.

This script generates working `get-pip.py` scripts for Python versions
without Server Name Identification (SNI) support by forcing the use
of `pyOpenSSL` inside `pip`.

Because it is not possible to install packages until having a `pip`
that actually works, all the required dependencies are appended to
the end of the script, as the usual `get-pip.py` does with `pip`.

The resulting `get-pip.py` script solves PyPI issues #974 and #978
that left `pip` unusable for the Python versions without SNI support:
    https://github.com/pypa/pypi-support/issues/974
    https://github.com/pypa/pypi-support/issues/978
"""


class Package(object):
    """Wrapper class for Python packages coming from PyPI."""

    def __init__(self, filename):
        """Create a new instance from a Python package filename."""

        self.filename = filename
        self.data = None

    @property
    def name(self):
        """Python package name."""

        nsuffixes = 1 + int(self.filename.endswith(".tar.gz"))
        base = self.filename.rsplit(".", nsuffixes)[0]
        return self.filename.split("-")[0]

    @property
    def version(self):
        """Python package version in string format."""

        nsuffixes = 1 + int(self.filename.endswith(".tar.gz"))
        base = self.filename.rsplit(".", nsuffixes)[0]
        return base.split("-")[1]

    @property
    def url(self):
        """Python package remote url from the PyPI repository."""

        import re
        try:
            from urllib.request import urlopen
        except ImportError:
            from urllib2 import urlopen

        # Define some patterns.
        urlpattern = "https://pypi.org/project/{0}/{1}/#files"
        rowpattern = ".*<a href=\"(.*{0}.*)\">".format(
            self.filename.replace(".", "\\."))

        # Parse the download page from PyPI to get the package url.
        conn = urlopen(urlpattern.format(self.name, self.version))
        try:
            htmlpage = conn.read().decode("utf-8").splitlines()
        finally:
            conn.close()

        for htmlrow in htmlpage:
            match = re.match(rowpattern, htmlrow)
            if match:
                return match.group(1)
        msg = "no url found for package {0}".format(self.filename)
        raise ValueError(msg)

    def download(self):
        """Get the Python package as a :class:`bytes` object."""

        try:
            from urllib.request import urlopen
        except ImportError:
            from urllib2 import urlopen

        conn = urlopen(self.url)
        try:
            self.data = conn.read()
        finally:
            conn.close()

    def textify(self):
        """Return the Python package data as plain encoded text."""

        if self.data is None:
            self.download()

        return "\n".join([
            "\"{name}\": {{",
            "    \"filename\":",
            "        \"{filename}\",",
            "    \"filedata\": \"\"\"",
            "{filedata}",
            "    \"\"\",",
            "}},"
        ]).format(name=self.name,
                  filename=self.filename,
                  filedata=self.pkgencode(self.data))

    @staticmethod
    def pkgencode(data, pad=0, nchars=None):
        """Return data string from a data stream using base64."""

        spaces = " " * pad
        if nchars is None:
            nchars = 79 - pad

        from base64 import b64encode
        raw = b64encode(data).decode("utf-8")
        lines = [raw[i:i + nchars] for i in range(0, len(raw), nchars)]
        return "\n".join(["{0}{1}".format(spaces, line) for line in lines])

    @staticmethod
    def pkgdecode(text):
        """Return data stream from a data string using base64."""

        from base64 import b64decode
        return b64decode("".join(line.strip() for line in text.split("\n")))


def main():
    """Main script function."""

    import os.path
    import argparse

    # Define arguments.
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--version", type=str, help="Python version", required=True)

    # Parse arguments.
    args = parser.parse_args()
    version = args.version

    if version == "2.6":
        PACKAGES = [
            # Essential packages (`pip`, `wheel` and `setuptools`).
            Package("pip-9.0.3-py2.py3-none-any.whl"),
            Package("argparse-1.4.0-py2.py3-none-any.whl"),
            Package("wheel-0.29.0-py2.py3-none-any.whl"),
            Package("setuptools-36.8.0-py2.py3-none-any.whl"),
            # `cffi` and dependencies (for `cryptography`).
            Package("pycparser-2.18.tar.gz"),
            Package("cffi-1.11.2-cp26-cp26mu-manylinux1_x86_64.whl"),
            # `enum34` and dependencies (for `cryptography`).
            Package("ordereddict-1.1.tar.gz"),
            Package("enum34-1.1.10-py2-none-any.whl"),
            # `cryptography` and its remaining dependencies.
            Package("asn1crypto-1.4.0-py2.py3-none-any.whl"),
            Package("idna-2.7-py2.py3-none-any.whl"),
            Package("ipaddress-1.0.23-py2.py3-none-any.whl"),
            Package("cryptography-2.1.1-cp26-cp26mu-manylinux1_x86_64.whl"),
            # `pyOpenSSL` and its remaining dependencies.
            Package("six-1.13.0-py2.py3-none-any.whl"),
            Package("pyOpenSSL-16.2.0-py2.py3-none-any.whl"),
        ]
    elif version == "2.7":
        PACKAGES = [
            # Essential packages (`pip`, `wheel` and `setuptools`).
            Package("pip-20.3.4-py2.py3-none-any.whl"),
            Package("argparse-1.4.0-py2.py3-none-any.whl"),
            Package("wheel-0.36.2-py2.py3-none-any.whl"),
            Package("setuptools-44.1.1-py2.py3-none-any.whl"),
            # `cffi` and dependencies (for `cryptography`).
            Package("pycparser-2.20-py2.py3-none-any.whl"),
            Package("cffi-1.14.6-cp27-cp27mu-manylinux1_x86_64.whl"),
            # `enum34` and dependencies (for `cryptography`).
            Package("enum34-1.1.10-py2-none-any.whl"),
            # `cryptography` and its remaining dependencies.
            Package("asn1crypto-1.4.0-py2.py3-none-any.whl"),
            Package("idna-2.10-py2.py3-none-any.whl"),
            Package("ipaddress-1.0.23-py2.py3-none-any.whl"),
            Package("cryptography-2.2.2-cp27-cp27mu-manylinux1_x86_64.whl"),
            # `pyOpenSSL` and its remaining dependencies.
            Package("six-1.16.0-py2.py3-none-any.whl"),
            Package("pyOpenSSL-18.0.0-py2.py3-none-any.whl"),
        ]
    else:
        msg = "unsupported Python version '{0}'".format(version)
        raise ValueError(msg)

    pkgtext = []
    for pkg in PACKAGES:
        pkgtext.append(pkg.textify())
    injection = "\n".join(pkgtext)

    scripts_dir = os.path.dirname(__file__)
    template_file = os.path.join(scripts_dir, "get-pip-template.py")
    with open("get-pip-py{0}.py".format(version), "w") as fd1:
        with open(template_file, "r") as fd2:
            for line2 in fd2:
                if line2 == "#! /usr/bin/env python\n":
                    fd1.write("#! /usr/bin/env python{0}\n".format(version))
                elif line2 == "PACKAGES = {}\n":
                    fd1.write("PACKAGES = {{\n\n{0}\n\n}}\n".format(injection))
                else:
                    fd1.write(line2)


if __name__ == "__main__":
    main()
