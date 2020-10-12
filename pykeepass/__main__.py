"""
Main module for CLI entrypoint handling all of the provided arguments and
subparser contexts to enable usage of PyKeePass as a standalone KeePass CLI
manager.
"""

from argparse import ArgumentParser, Namespace
from pykeepass import __version__, PyKeePass
from pykeepass.group import Group

SUBPARSER_TREE = "tree"
INDENT_WIDTH = 4
GROUP_BEGIN = "["
GROUP_END = "]"
TREE_HANDLE = "|"
TREE_HANDLE_END = "`"
TREE_TICK = "-- "


def generate_padding(indent: int) -> str:
    """Generate padding with tree handles (lines) on each indent."""
    len_pad = INDENT_WIDTH * indent
    padding = " " * len_pad
    if not padding:
        return padding  # empty string

    for idx in range(len_pad):
        if idx % INDENT_WIDTH != 0:
            continue
        # slice on every width's occasion and insert tree handle
        padding = padding[:idx] + TREE_HANDLE + padding[idx + 1:]
    return padding


def print_tree_children(
        children: list, padding: str, tree_iteration: int, tree_length: int,
        root: bool = False
):
    """Print group's children as a part of a parent tree."""
    len_children = len(children)
    for idx, item in enumerate(children):
        if idx == len_children - 1:
            print(padding + TREE_HANDLE_END + TREE_TICK + item)
            if tree_iteration < tree_length - 1:
                print()
            else:
                if not root:
                    print(padding)
        else:
            print(padding + TREE_HANDLE + TREE_TICK + item)


def print_tree(tree: dict, indent: int = 0, root: bool = False):
    """
    Handles all the fancy brackets, pipes, backticks, and ticks that make
    the visual tree out of ASCII in a console.
    """
    padding = generate_padding(indent=indent)

    tree_items = tree.items()
    len_tree = len(tree_items)
    for tidx, packed in enumerate(tree_items):
        title, values = packed

        group_prefix = padding
        if not root:
            group_prefix = padding[:-INDENT_WIDTH] + TREE_HANDLE + TREE_TICK
        print(group_prefix + f"{GROUP_BEGIN}{title}{GROUP_END}")
        groups = values["groups"]
        items = values["items"]

        for group in groups:
            print_tree(group, indent=indent + 1)

        print_tree_children(
            children=items, padding=padding, tree_iteration=tidx,
            tree_length=len_tree, root=root
        )


def collect_groups(group: Group) -> dict:
    """
    Collect group names and names of their children (entries) as a tree-like
    structure for easier printing.
    """
    result = {}
    name = group.name
    if name not in result:
        result[name] = {"groups": [], "items": [
            entry.title for entry in group.entries
        ]}

        for child in group.subgroups:
            result[name]["groups"].append(collect_groups(child))
    return result


def show_tree(
        filename: str, password: str, keyfile=None, transformed_key=None
):
    """Command for showing the KDBX as a tree in a console."""
    kdbx = PyKeePass(
        filename=filename, password=password,
        keyfile=keyfile, transformed_key=transformed_key
    )
    tree = collect_groups(kdbx.root_group)
    print_tree(tree, root=True)


def handle_commands(args: Namespace):
    """Handler for specific subparsers and their code branches."""
    if args.subparser == SUBPARSER_TREE:
        show_tree(
            filename=args.file, password=args.password,
            keyfile=args.keyfile, transformed_key=args.transformed_key
        )


def main():
    """Main function for the CLI entrypoint."""
    parser = ArgumentParser()
    parser.add_argument("--version", action="version", version=__version__)
    parser.add_argument("-p", "--password", required=True)
    parser.add_argument("-f", "--file", required=True)
    parser.add_argument("-k", "--keyfile", required=False)
    parser.add_argument("-t", "--transformed-key", required=False)

    sub = parser.add_subparsers(dest="subparser")
    sub = sub.add_parser(SUBPARSER_TREE, help="display KDBX items as a tree")

    args = parser.parse_args()

    handle_commands(args)
