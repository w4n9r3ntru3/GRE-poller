from collections import defaultdict

import yaml

from helper import Add, Del, Find, Get, Word

if __name__ == "__main__":
    with open("vocabs.yaml", "r") as f:
        content = f.read()

    data: dict = yaml.safe_load(content)

    for (key, value) in data.items():
        assert isinstance(key, str)
        assert isinstance(value, dict)

        Add(key, Word().fromdict(value))
