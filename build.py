import yaml

from helper import Add, All, Del, Get, Word

if __name__ == "__main__":
    with open("vocabs.yaml", "r") as f:
        content = f.read()

    data: dict = yaml.safe_load(content)

    for (key, value) in data:
        assert isinstance(key, str)
        assert isinstance(key, dict)

        Add(key, Word().fromdict(value))
