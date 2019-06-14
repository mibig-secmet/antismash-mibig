# License: GNU Affero General Public License v3 or later
# A copy of GNU AGPL v3 should have been included in this software package in LICENSE.txt.

"""Script to generate mibig html output from mibig json file."""

import json
from os import path
from sys import argv
from subprocess import call

def _main():
    json_path = argv[1]
    gbk_folder = argv[2]
    output_folder = argv[3]
    antismash_path = path.abspath(path.dirname(__file__))

    with open(json_path, "r") as json_file:
        data = json.load(json_file)
        mibig_acc = data["cluster"]["mibig_accession"]
        gbk_acc = data["cluster"]["loci"]["accession"]
        gbk_path = path.join(gbk_folder, "{}.gbk".format(gbk_acc))
        output_path = path.join(output_folder, mibig_acc)
        commands = [
            "python",
            path.join(antismash_path, "run_antismash.py"),
            "-v",
            "--mibig-mode",
            "--mibig-json",
            json_path,
            "--output-dir",
            output_path,
            gbk_path
        ]
        print("Generating MIBiG output for {}".format(mibig_acc))
        if call(commands) == 0:
            print("Generating antiSMASH output for {}".format(mibig_acc))
            if "Bacteria" in data["cluster"]["loci"]["taxonomy"]:
                commands = [
                    "python",
                    path.join(antismash_path, "run_antismash.py"),
                    "-v",
                    "--taxon",
                    "bacteria",
                    "--output-dir",
                    path.join(output_path, "generated"),
                    path.join(output_path, "{}.region001.gbk".format(gbk_acc))
                ]
                call(commands)
            elif "Fungi" in data["cluster"]["loci"]["taxonomy"]:
                commands = [
                    "python",
                    path.join(antismash_path, "run_antismash.py"),
                    "-v",
                    "--taxon",
                    "fungi",
                    "--output-dir",
                    path.join(output_path, "generated"),
                    path.join(output_path, "{}.region001.gbk".format(gbk_acc))
                ]
                call(commands)
            elif "Viridiplantae" in data["cluster"]["loci"]["taxonomy"]:
                "Plant BGC is temporarily not supported"
            else:
                "Taxon is not supported (yet)"

if __name__ == "__main__":
    _main()