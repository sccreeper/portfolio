Title: 2023 Advent Of Code summary
Summary:    Advent of code 2023 from start to (close to) finish
Authour: Oscar Peace
Tags: AOC
      Go
Published: 19/12/2023

This is a megapost talking about every [Advent of Code](https://adventofcode.com) day for 2023, including the ones I didn't finish or attempt.

*All solutions talked about can be found [here](https://github.com/sccreeper/aoc/tree/main/2023).*

# Summaries

## Day 1 & Day 2

[Day 1](https://adventofcode.com/2023/day/1)
[Day 2](https://adventofcode.com/2023/day/2)

These days were the easiest. Day 2 felt slightly easier as the 2<sup>nd</sup> part of the solution wasn't too difficult to implement because of how I had already implemented part 1.

**Day 1**

All was involved here was some basic string manipulation (maybe foreshadowing what was to come), the only part of it which threw a spanner in the works was trying not to mess up indexing when reading characters from the string. This was also the only day where I tried to optimize my solution, not really achieving much.

**Day 2**

This felt somewhat similar to day 1, although with maybe *slightly* complicated string manipulation. The steps to the solution are below:

1. Split our input by `\n`
2. Split each line at `:` and throw away everything before it.
3. Then split the "handfuls" by `,` and parse how many red, green and blue cubes there are.
```go
// What we would get after looking at each line
type Game struct {
    ID int
    Handfuls []Handful
}

type Handful struct {
	Red   int
	Green int
	Blue  int
}

```
4. Then what followed was an incredibly trivial process of scanning through our list of `Game` structs and determining which ones had valid amounts of cubes then calculating the sum.

## Day 3
[Day 3](https://adventofcode.com/2023/day/3)

For me this day felt more complicated although it was probably only because I didn't notice that [this line](https://github.com/sccreeper/aoc/blob/59f2d1465b5f45ee8f9961f621046387230577bc/2023/3/main.go#L205C23-L205C23),
```go
col += col_index - 1 //I have no idea why I did this.
```
should have instead been this line:
```go
col += len(number)
```
This lost me at least half an hour (not that it mattered anyway, because I live in the UK and the puzzles are released at 5am for me) wondering why the test input worked and my input didn't.

The steps to the solution (parts 1 and 2) are below:

1. Split the input by `\n`
2. We make a 3D array of "gears", so we can have their X, Y and what numbers they are adjacent to & another array containing the locations of gears. (p2)
3. We also make an array for numbers that are adjacent to symbols.
4. We then scan through the input line by line and operating on each found number individually.
5. We perform checks to see where we can check around the number so we don't get any out of bounds errors. We store the valid checking locations in an array.
6. A series of if statements check if the "side" (L, R, T, B) exist for that number. If true the respective checks are formed, adding & subtracting from indexes. E.g. if checking the left, we -1 from our x, or if checking to the top, we -1 from our y etc. Diagonals can be checked by combining both x and y.
7. If the character is a gear (`*`), we store it's location and adjacent number in the `gears` and `gears_locations` array. (p2)
8. Then we can scan through the 2 groups of arrays we created (`gears & gear_locations`, `valid_numbers`) and perform the respective operations that are needed for the puzzle solution.

## Day 4

[Day 4](https://adventofcode.com/2023/day/4)

Part one of day 4 was very trivial, part 2 however tripped me up big time for some reason. This was the first one where I genuinely got stuck. I no longer like Elf's and cards.

I think the main reason why I found part 2 difficult it because I had to use recursion (later turns out I didn't), something to be honest I had very little experience actually using. I knew what it was conceptually but I didn't know how to implement. This was a problem that conceptually seemed easy but I found difficult to implement in code.

I eventually settled on a solution that didn't use recursion, with help (sorry) from people on the Go discord.

## Day 5

[Day 5](https://adventofcode.com/2023/day/5)

I found both parts of day 5 easy, however my first solution to part 2 had serious memory problems and took a very long time.

**Memory problems**

The first way I reduced memory is by doing each range of seeds separately instead of lumping them all into one array and [doing them in bulk](https://github.com/sccreeper/aoc/blob/13cdefb058ddb3f80f9292d899e6df586a0f588c/2023/5/main.go#L173).

The second way I reduced it (the much better way than the first) is just not creating any arrays at all, and just doing each number in the range as I went along.

Below is the code for the main part of part 2 that is executed in a goroutine.
```go
go func(start int, end int) {

    fmt.Printf("Seed range %d to %d\n", start, end-1)

    //Iterate through range and find number for that range

    var lowest int = math.MaxInt //No number can be bigger than this

    for j := start; j < end; j++ {
        x := part_1(Almanac{ //Perform part 1 processing on just a single number.
            Seeds: []int{j},
            Maps:  al.Maps,
        })

        if x < lowest {
            lowest = x
        }
    }

    lowest_seeds <- lowest //Push the result to a channel

}(al.Seeds[i], al.Seeds[i]+al.Seeds[i+1])
```

After this all the seeds in `lowest` are sorted, and the lowest one is returned.

## Day 6

[Day 6](https://adventofcode.com/2023/day/6)

I thought this day was going to be difficult however I actually found it rather easy. Part 1 was more difficult to implement than part 2 as part 2 was just doing part 1 with one number instead of multiple. However, my first solution to part 2 (and arguably part 1) was stupid. I realised after seeing solutions made only using [Desmos](https://www.desmos.com/calculator), that my [condition](https://github.com/sccreeper/aoc/blob/2de6bd2eb51e4f622246ec428649f7d92bb13814/2023/6/main.go#L117C23-L117C23):
```go
i*(race[0]-i) > race[1]
//i[0] = t and i[1] = d
```
and the loop it was in were effectively iterating to find the difference between two roots as what I had written could be rewritten as follows:

$$ x \cdot(t-x) > d $$
$$ x \cdot(t-x) - d = 0 $$
$$ -x^2 + tx -d=0 $$

Which could then be solved using the quadratic formula. This reduced the running time from ~60ms to ~10us.

## Day 7

[Day 7](https://adventofcode.com/2023/day/7)

Part 1 was relatively easy however I couldn't complete part 2 no matter what I did. Every solution I made for part 2 worked for the given example, however it didn't work for my puzzle input. This combined with the fact that I eventually realised that I was getting a different output each time I ran my code, I unfortunately gave up and conceded to using someone else's [solution](https://github.com/voiceroy/AOC-2023/blob/master/Day7/day7.go). I tried to port their solution to part 2 to get my code work at first, however I was still getting the error where I received a different output each time.

## Day 8

[Day 8](https://adventofcode.com/2023/day/8)

This was the first day which I found to include actual computer science concepts. Both part 1 and part 2 were actually a [graph](https://en.wikipedia.org/wiki/Graph_(discrete_mathematics)), which I only realised when I attempted to brute force part 2.

My first solution involved representing the graph as a map of nodes, with each nodes containing a slice of strings.
```golang
graph := map[string][2]string
```
When I attempted part 2, I replaced this with a system using structs and pointers instead of the map:
```golang
type Node struct {

    Data string
    Left *Node
    Right *Node

}
```
I also redid the code for part 1, even though the performance gains were marginal.

Part 2 was the essentially the same as doing part 1, but with different start (any value that ends with `A`) and end values (any value that ends with a `Z`), because of this the final result could not be brute-forced and instead the number of steps for each start value had to be run through a lowest common multiple function.

## Day 9

[Day 9](https://adventofcode.com/2023/day/9)

This was surprisingly easy, it felt like it should have belonged further towards the start, like a day 3 or 4 puzzle. Part 2 was essentially just a reverse of part 1 as well.

Because of this my first approach was to try and solve it by turning each sequence of numbers into an equation in the form of a polynomial sequence ( $ an^2 + bn + 2 $ etc. ), however I quickly realised that this would be more difficult than just computing the added/subtracted value for each sequence.

## Day 10

[Day 10](https://adventofcode.com/2023/day/10)

Part 1 was a a graph problem sort of similar to [day 8](#day-8), i.e. you have to parse your file and turn it into a graph, then traverse it. 

**Parsing the file & Part 1**

1. Go through the file line by line and assign each character an empty struct with respective type enum in a 2D array.
2. Then go through that 2D array and check each node to see what cells it can connect to and assign pointers based off of this.
3. Traverse the graph from the `S` (start) node and count all nodes then divide by 2.

**Part 2**

This is the part that I couldn't do. A lot of the solutions I made worked on the examples given, however, when I tried them on the real thing they didn't work. I will *try* to come back and do this later, although I wouldn't bet any money on it.

## Day 11

[Day 11](https://adventofcode.com/2023/day/11)

This was a nice break from how difficult I found day 10. I found parts 1 & 2 relatively trivial, with part 2 only being a small adpatation from my solution to part 1.

**Adapting part 1 to fit part 2**

Because I had already developed a generic `get_distance(a, b)` function for part 1, I could use this again for part 2 but now I had to figure out if any expanded rows/columns were between the 2 sets of coordinates. I could accomplish this by writing the following `if` statement encapsulated in a loop going through the pairs of galaxies followed by the locations of rows and columns. Each time a row/column was found to be between the 2 sets of coordinates, the scale factor for the transform value ($ (1 \times 10^6) - 1 $) would be incremented. Finally this would be added to the initial distance found in `get_distance`.

```golang
//Loop is same for columns, but using X coordinates instead of Y
for _, row := range rows {
    if v.PosY < row && galaxies[i].PosY > row {
        scale_factor++
    } else if v.PosY > galaxies[i].PosY && v.PosY > row && galaxies[i].PosY < row {
        scale_factor++
    }
}
```

## Day 12

[Day 12](https://adventofcode.com/2023/day/12)

This was the first day I looked at and was genuinely had no idea. Although I felt like I understood the problem, actually implementing it in code in a reasonable and efficient way, was an impossible task.

## Day 13

[Day 13](https://adventofcode.com/2023/day/13)

Half way through now however this is where I felt like I should stop. What I made for part 1 worked on the test data but didn't work on the real data. This after day 12 made me feel a bit demoralised to be honest however I was determined to at least try and attempt every day, with the mindeset that this was my first Advent of Code, so I shouldn't feel too bad about it.

## Day 14

[Day 14](https://adventofcode.com/2023/day/14)

The first part of this day I was able to complete relatively easily, however couldn't do part 2. From now on I think I'm going to try and do just the odd day.

## Day 15

[Day 15](https://adventofcode.com/2023/day/15)

This day was suprisingly easy to complete given the difficulty shown by some of the previous days, however from now on I probably won't be attempting every single day and instead only attempting just the occasional day up to the 25th.

## Day 16 & 17

[Day 16](https://adventofcode.com/2023/day/16)
[Day 17](https://adventofcode.com/2023/day/17)

Didn't attempt, day 17 required use of a path finding algorithm like [Dijkstra's](https://en.wikipedia.org/wiki/Dijkstra's_algorithm), which as somebody who hasn't really ever done any actual Computer Science theory would have been difficult to attempt. Day 16 just got left behind.

After this I didn't complete any more days (rip).

# TLDR

Difficulties:

(trivial, easy, medium, hard, difficult)

- Day 1: Trivial
- Day 2: Trivial
- Day 3: Easy
- Day 4: Medium (I had a brain block)
- Day 5: Easy
- Day 6: Trivial
- Day 7: Medium
- Day 8: Easy
- Day 9: Trivial
- Day 10: Medium (Only 1 star, couldn't do part 2)
- Day 11: Easy
- Day 12: Hard
- Day 13: Hard (Even though it probably shouldn't have been, probably still overshadowed by day 12)
- Day 14: Medium (Only able to complete part 1)
- Day 15: Easy
- Day 16: Didn't attempt (Medium in theory)
- Day 17: Didn't attempt (Hard in theory)