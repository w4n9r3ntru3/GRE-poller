import dataclasses
import json
import os
import sys
from collections import defaultdict
from enum import Enum
from os import path as os_path

import yaml


class WordKind(Enum):
    Noun = "noun"
    Verb = "verb"
    Adj = "adj"
    Adv = "adv"
    Aux = "aux"
    Pro = "pro"


class Word:
    def __init__(
        self,
        meaning: str = "",
        example: str = "",
        similar=None,
        opposite=None,
        parents=None,
        children=None,
    ):
        self.meaning = meaning
        self.example = example
        self.similar = self.defaultset(similar)
        self.opposite = self.defaultset(opposite)
        self.parents = self.defaultset(parents)
        self.children = self.defaultset(children)

    @staticmethod
    def defaultset(value):
        return value if value else set()

    def safe_dump(self):
        return yaml.safe_dump(self.asdict())

    def fromdict(self, d: dict):
        assert isinstance(d, dict)

        if not isinstance(d, defaultdict):
            d = defaultdict(lambda: None, **d)

        self.meaning = d["M"]
        self.example = d["E"]
        self.similar = self.defaultset(d["S"])
        self.opposite = self.defaultset(d["O"])
        self.parents = self.defaultset(d["P"])
        self.children = self.defaultset(d["C"])
        return self

    @classmethod
    def safe_load(cls, string):
        return cls().fromdict(yaml.safe_load(string))

    @property
    def isroot(self):
        return len(self.children) != 0

    def asdict(self) -> defaultdict:
        return defaultdict(
            lambda: None,
            M=self.meaning,
            E=self.example,
            S=self.similar,
            O=self.opposite,
            P=self.parents,
            C=self.children,
        )

    def __str__(self) -> str:
        return self.safe_dump()


class DataBase:
    def __init__(self, file="data.json", path="database", enc="utf-8"):
        os.makedirs(path, exist_ok=True)

        self.file = os_path.expanduser(os_path.join(path, file))
        self.enc = enc
        try:
            with open(self.file, mode="r+", encoding=self.enc) as f:
                data = yaml.safe_load(f)
        except IOError:
            data = {}
        data = {k: Word.safe_load(v) for (k, v) in data.items()}
        self.data = defaultdict(Word, **data)

    @staticmethod
    def concat_iterable(func, words):
        return words.union(func(w) for w in words)

    def ancestors(self, word: str) -> set:
        "Get the ancestors of a word"
        if word not in self:
            self[word] = Word()

        parents = self[word].parents
        ans = self.concat_iterable(self.ancestors, parents)
        parents.update(ans)
        return parents

    def decendants(self, word: str) -> set:
        "Get the decendants of a word"
        assert word in self
        children = self[word].children
        ans = self.concat_iterable(self.decendants, children)
        children.update(ans)
        return children

    def add(self, word: str, info: Word):
        "Add a word to graph"

        self[word] = info
        ancestors = self.ancestors(word)
        for wordroot in ancestors:
            self.data[wordroot].children.add(word)

        decendants = self.decendants(word)
        for longword in decendants:
            self.data[longword].parents.add(word)

        prev = self.data[word]
        info.parents.update(prev.parents)
        info.children.update(prev.children)
        self[word] = info

        assert self.check(word)

    def delete(self, word: str = "", also_root=False):
        if word == "":
            self.data = defaultdict(Word)
            return

        assert word in self

        w: Word = self[word]
        del self[word]

        for wordroot in w.parents:
            assert wordroot in self

            r: Word = self.data[wordroot]
            r.children.remove(word)
            # also delete roots
            if also_root and not r.isroot:
                self.delete(wordroot)
                assert wordroot not in self

        for longword in w.children:
            assert longword in self

            l: Word = self.data[longword]
            l.parents.remove(word)

    def check(self, word: str):
        return (
            word in self
            and all(self.check(p) for p in self[word].parents)
            and all(self.check(d) for d in self[word].children)
        )

    def find(self, word: str = ""):
        return {k: str(v) for (k, v) in self.data.items() if word in k}

    def __getitem__(self, key: str):
        return self.data[key]

    def __setitem__(self, key: str, value):
        self.delete(key)
        self.add(key, value)

    def __delitem__(self, key):
        self.delete(key)

    def __contains__(self, value) -> bool:
        return value in self.data

    def keys(self):
        return self.data.keys()

    def values(self):
        return self.data.values()

    def __del__(self):
        data = {k: v.safe_dump() for (k, v) in self.data.items()}

        with open(self.file, mode="w+", encoding=self.enc) as f:
            yaml.safe_dump(data, f)
