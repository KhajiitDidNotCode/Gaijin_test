# It was not specified in the description of the task,
# but I've added two more pint outs for better understanding what's going on:
# - in case of error in files with CMDS var (Python code error)
# - in case of error while executing a command (eg. echo5)

import subprocess
import sys
from glob import iglob
from importlib.util import module_from_spec, spec_from_file_location
from itertools import chain
from typing import Generator


def get_files(directory: str) -> Generator[str, None, None]:
    files = []
    for file in iglob(directory + "/**/*.py", recursive=True):
        files.append(file)
    files.sort()
    return (file for file in files)


def get_commands(file: str) -> list:
    module_spec = spec_from_file_location(file.split("/")[-1], file)
    module = module_from_spec(module_spec)

    try:
        module_spec.loader.exec_module(module)
        try:
            return module.CMDS
        except AttributeError:  # no CMDS variable
            pass
    except Exception as e:
        print(f'An error "{e.__class__.__name__}" occured in module "{file}"')

    return []


def run_command(command: str):
    try:
        subprocess.run(
            command, shell=True, check=True
        )  # this part can be async in case of commands that more complicated than "echo"
    except subprocess.CalledProcessError:
        print(f'An error occured while executing the command "{command}"')


if __name__ == "__main__":
    directory = sys.argv[1]
    commands_log = set()
    commands_hash = {}  # dicts in python 3.7+ keep the order of elements
    files = get_files(directory)

    for file in files:
        commands = get_commands(file)
        # print("Got commands", commands, "from file", file)
        commands_hash[file] = commands

    for command in list(chain.from_iterable(commands_hash.values())):
        if command in commands_log:
            print(f'Command "{command}" was already executed. Skipping.')
        else:
            # print(f'Running command "{command}"...')
            run_command(command)
            commands_log.add(command)
