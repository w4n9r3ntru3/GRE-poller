package lib

import (
	"log"
)

const (
	// Noun is a noun
	Noun = "noun"
	// Verb is a verb
	Verb = "verb"
	// Adj is an adjective
	Adj = "adj"
	// Adv is an adverb
	Adv = "adv"
	// Aux is an auxiliary word
	Aux = "aux"
	// Conj is a conjunction
	Conj = "conj"
	// Pro is a pronoun
	Pro = "pro"
)

// None is empty
type None struct {
}

// N is short for None
func N() None { return None{} }

// SetToList converts a set to a list
func SetToList(set map[string]None) (list []interface{}) {
	list = make([]interface{}, 0)
	for key := range set {
		list = append(list, key)
	}
	return
}

// ListToSet converts a list to a set
func ListToSet(list []interface{}) (set map[string]None) {
	set = make(map[string]None)
	for _, key := range list {
		set[key.(string)] = N()
	}
	return
}

// Word represents a word
type Word struct {
	// Mng of a word
	Mng string

	// Exmp usage
	Exmp string

	// Which Knd
	Knd string

	// Smlr words
	Smlr map[string]None

	// Opst words
	Opst map[string]None

	// WordRoot of the current word
	WordRoot map[string]None

	// Derived word of the current word
	Derived map[string]None
}

// NewWordFrom creates a new word from a given map
func NewWordFrom(m map[string]interface{}) *Word {
	word := Word{}

	if meaning, ok := m["Mng"]; ok {
		word.Mng = meaning.(string)
	}

	if example, ok := m["Exmp"]; ok {
		word.Exmp = example.(string)
	}

	if kind, ok := m["Knd"]; ok {
		kind := kind.(string)
		switch kind {
		case Noun, Verb, Adj, Adv, Aux, Conj, Pro:
		default:
			log.Fatalln(kind, "is not a kind.")
		}
		word.Knd = kind
	}

	if similar, ok := m["Smlr"]; ok {
		list := similar.([]interface{})
		word.Smlr = ListToSet(list)
	}

	if opposite, ok := m["Opst"]; ok {
		list := opposite.([]interface{})
		word.Opst = ListToSet(list)
	}

	if root, ok := m["Prnt"]; ok {
		list := root.([]interface{})
		word.WordRoot = ListToSet(list)
	}

	if derived, ok := m["Cdrn"]; ok {
		list := derived.([]interface{})
		word.Derived = ListToSet(list)
	}

	return &word
}

// AsMap converts a word into a for serialization
func (word *Word) AsMap() map[string]interface{} {
	return map[string]interface{}{
		"Mng":  word.Mng,
		"Exmp":  word.Exmp,
		"Knd":     word.Knd,
		"Smlr":  SetToList(word.Smlr),
		"Opst": SetToList(word.Opst),
		"Prnt":   SetToList(word.WordRoot),
		"Cdrn": SetToList(word.Derived),
	}

}
