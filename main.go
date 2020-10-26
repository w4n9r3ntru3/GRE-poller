package main

import (
	"encoding/json"
	"flag"
	"fmt"
	"io/ioutil"
	"log"

	"github.com/w4n9r3ntru3/GRE-data/lib"
	"gopkg.in/yaml.v2"
)

func main() {
	var err error

	panicIfNil := func(err error) {
		if err != nil {
			log.Fatalln(err)
		}
	}

	var inFileName, outFileName string

	flag.StringVar(&inFileName, "input", "data/vocabs.yaml", "Please specify input file to parse")
	flag.StringVar(&outFileName, "output", "data/database.json", "Please specify output file to generate")

	flag.Parse()

	var data []byte

	data, err = ioutil.ReadFile(inFileName)
	panicIfNil(err)

	contents := make(map[string]map[string]interface{})
	yaml.Unmarshal(data, &contents)

	allWords := make(map[string]lib.Word)
	for key, val := range contents {
		word := *lib.NewWordFrom(val)
		allWords[key] = word

		fmt.Printf("Key: %s, Value: %s\n", key, word)
	}

	converted := make(map[string]map[string]interface{})
	for key, val := range allWords {
		converted[key] = val.AsMap()
	}

	data, err = json.Marshal(converted)
	panicIfNil(err)
	err = ioutil.WriteFile(outFileName, data, 0664)
	panicIfNil(err)
}
