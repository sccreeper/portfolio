Title: 2023 Advent of Code
Summary: My first advent of code
Authour: Oscar Peace
Tags: Go
      AOC
Published: 1/12/23

This is my first ever year actually doing this. I considered maybe working on [goputer](https://www.github.com/sccreeper/goputer) so I complete it using that, but considering I had never done it before and didn't know what it was going to be like, and the fact that there were *still* some bugs (my fault) with the runtime that couldn't be ironed out before it started, I ended up using Go.

My solution for day 1 is below, and it definitely isn't the best, (I saw solutions written using [one shell command](https://discord.com/channels/118456055842734083/1179763373538279476/1180119445356683274) on the golang discord.), and [this](https://gist.github.com/zyxkad/e30999e17636f2526b1f0143ae5e206d) one that took 2.5ms to run. My original solution below took 2-3ms to run on average according to the `time` command. Also below is my more "optimized" solution which managed to reduce the time to around 1ms. The biggest source of noise and delay was actually reading the file in, this lead to a 1ms reduction in runtime.

**First solution**

Original: [GitHub](https://github.com/sccreeper/aoc/blob/e0486249269765485b365fc672589bbe0134e191/2023/1/main.go)
```go

package main

import (
	"fmt"
	"os"
	"strconv"
	"strings"
)

const integers = "1234567890"

var words []string = []string{"one", "two", "three", "four", "five", "six", "seven", "eight", "nine"}
var word_digits []string = []string{"1", "2", "3", "4", "5", "6", "7", "8", "9"}

func main() {

	var input_name string
	fmt.Println("Input file name:")
	fmt.Scanln(&input_name)

	input_data, err := os.ReadFile(input_name)
	if err != nil {
		fmt.Printf("No input called: %s", input_name)
	}

	input_string := string(input_data)

	var total int

	for _, line := range strings.Split(input_string, "\n") {

		var line_numbers []string = make([]string, 0)

		for i := 0; i < len(line); i++ {

			if strings.Contains(integers, string(line[i])) { //Words can't start with integers.

				line_numbers = append(line_numbers, string(line[i]))

			} else {

				for j := 0; j < len(words); j++ {

					if i+len(words[j]) < len(line)+1 {

						if string(line[i:i+len(words[j])]) == words[j] {

							line_numbers = append(line_numbers, word_digits[j])

						}

					}

				}

			}

		}

		if len(line_numbers) == 0 {
			continue
		} else if len(line_numbers) == 1 {

			i, _ := strconv.Atoi(line_numbers[0] + line_numbers[0])
			total += i
			fmt.Println(i)

		} else {

			i, _ := strconv.Atoi(line_numbers[0] + line_numbers[len(line_numbers)-1])
			total += i
			fmt.Println(i)

		}

	}

	fmt.Println(total)

}

```

**Second solution**

Original: [GitHub](https://github.com/sccreeper/aoc/blob/d284d0f7d60ec198c9b8819c1dc3eb1e7a2e4d64/2023/1/main.go)

```go

package main

import (
	_ "embed"
	"fmt"
	"strconv"
	"strings"
	"time"
)

const integers = "1234567890"

var words []string = []string{"one", "two", "three", "four", "five", "six", "seven", "eight", "nine"}
var word_lengths []int = []int{3, 3, 5, 4, 4, 3, 5, 5, 4}
var word_digits []string = []string{"1", "2", "3", "4", "5", "6", "7", "8", "9"}

//go:embed calibration.txt
var input_string string
var total int

func main() {

	start := time.Now()

	for _, line := range strings.Split(input_string, "\n") {

		var line_numbers []string = make([]string, 0)
		var line_length int = len(line)

		for i := 0; i < line_length; i++ {

			if strings.Contains(integers, string(line[i])) { //Words can't start with integers.

				line_numbers = append(line_numbers, string(line[i]))

			} else {

				for j := 0; j < 9; j++ {

					if i+word_lengths[j] < line_length+1 {

						if string(line[i:i+word_lengths[j]]) == words[j] {

							line_numbers = append(line_numbers, word_digits[j])

						}

					}

				}

			}

		}

		if len(line_numbers) == 0 {
			continue
		} else if len(line_numbers) == 1 {

			i, _ := strconv.Atoi(line_numbers[0] + line_numbers[0])
			total += i

		} else {

			i, _ := strconv.Atoi(line_numbers[0] + line_numbers[len(line_numbers)-1])
			total += i

		}

	}

	used := time.Since(start)
	fmt.Println("Time used:", used)

	fmt.Println(total)

}

```

I probably won't update this with solutions to the other days in the challenge however I will post them on on [this](https://github.com/sccreeper/aoc) git repo.