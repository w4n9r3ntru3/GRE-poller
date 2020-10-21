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

    def fromdict(self, d: defaultdict):
        self.meaning = d["M"]
        self.example = d["E"]
        self.similar = self.defaultset(d["S"])
        self.opposite = self.defaultset(d["O"])
        self.parents = self.defaultset(d["P"])
        self.children = self.defaultset(d["C"])
        return self

    @classmethod
    def safe_load(cls, string):
        return cls().fromdict(defaultdict(lambda x: None, **yaml.safe_load(string)))

    @property
    def isroot(self):
        return len(self.children) != 0

    def asdict(self) -> dict:
        return defaultdict(
            lambda x: None,
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
                # data: Dict[str, str]
                data: dict = yaml.safe_load(f)
        except IOError:
            data = {}
        self.data = {k: Word.safe_load(v) for (k, v) in data.items()}

    @staticmethod
    def concat_iterable(func, words):
        return set().union(words, *(func(w) for w in words))

    def ancestors(self, word: str) -> set:
        "Get the ancestors of a word"
        assert self.has(word)
        parents = self.data[word].parents
        ans = self.concat_iterable(self.ancestors, parents)
        parents.update(ans)
        return parents

    def decendants(self, word: str) -> set:
        "Get the decendants of a word"
        assert self.has(word)
        children = self.data[word].children
        ans = self.concat_iterable(self.decendants, children)
        children.update(ans)
        return children

    def add(self, word: str, info: Word):
        "Add a word to graph"

        self.data[word] = info

        assert self.check(word)

        ancestors = self.ancestors(word)
        for wordroot in ancestors:
            self.data.get(wordroot, Word()).children.add(word)

        decendants = self.decendants(word)
        for longword in decendants:
            self.data.get(longword, Word()).parents.add(word)

        prev = self.data.get(word, Word())
        info.parents.update(prev.parents)
        info.children.update(prev.children)
        self.data[word] = info

    def delete(self, word: str = "", also_root=False):
        if word == "":
            self.data = {}
            return

        assert self.has(word)

        w: Word = self.data[word]
        del self.data[word]

        for wordroot in w.parents:
            assert self.has(wordroot)

            r: Word = self.data[wordroot]
            r.children.remove(word)
            # also delete roots
            if also_root and not r.isroot:
                self.delete(wordroot)
                assert not self.has(wordroot)

        for longword in w.children:
            assert self.has(longword)

            l: Word = self.data[longword]
            l.parents.remove(word)

    def has(self, word: str):
        return word in self.data.keys()

    def get(self, word: str):
        assert self.has(word)
        return self[word]

    def check(self, word: str):
        return (
            self.has(word)
            and all(self.check(p) for p in self.data[word].parents)
            and all(self.check(d) for d in self.data[word].children)
        )

    def find(self, word: str = ""):
        return {k: str(v) for (k, v) in self.data.items() if word in k}

    def __getitem__(self, key: str):
        return self.data[key]

    def __del__(self):
        data = {k: v.safe_dump() for (k, v) in self.data.items()}

        with open(self.file, mode="w+", encoding=self.enc) as f:
            yaml.safe_dump(data, f)
