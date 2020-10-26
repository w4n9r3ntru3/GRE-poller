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
	list = make([]interface{}, len(set))
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
	// Meaning of a word
	Meaning string

	// Example usage
	Example string

	// Which Kind
	Kind string

	// Similar words
	Similar map[string]None

	// Opposite words
	Opposite map[string]None

	// WordRoot of the current word
	WordRoot map[string]None

	// Derived word of the current word
	Derived map[string]None
}

// NewWordFrom creates a new word from a given map
func NewWordFrom(m map[string]interface{}) *Word {
	word := Word{}

	if meaning, ok := m["M"]; ok {
		word.Meaning = meaning.(string)
	}
	if example, ok := m["E"]; ok {
		word.Example = example.(string)
	}
	if kind, ok := m["K"]; ok {
		kind := kind.(string)
		switch kind {
		case Noun, Verb, Adj, Adv, Aux, Conj, Pro:
		default:
			log.Fatalln(kind, "is not a kind.")
		}
		word.Kind = kind
	}

	if similar, ok := m["S"]; ok {
		list := similar.([]interface{})
		word.Similar = ListToSet(list)
	}

	if opposite, ok := m["O"]; ok {
		list := opposite.([]interface{})
		word.Opposite = ListToSet(list)
	}

	if root, ok := m["P"]; ok {
		list := root.([]interface{})
		word.WordRoot = ListToSet(list)
	}

	if derived, ok := m["C"]; ok {
		list := derived.([]interface{})
		word.Derived = ListToSet(list)
	}

	return &word
}

// AsMap converts a word into a for serialization
func (word *Word) AsMap() map[string]interface{} {
	return map[string]interface{}{
		"M": word.Meaning,
		"E": word.Example,
		"K": word.Kind,
		"S": SetToList(word.Similar),
		"O": SetToList(word.Opposite),
		"P": SetToList(word.WordRoot),
		"C": SetToList(word.Derived),
	}

}
