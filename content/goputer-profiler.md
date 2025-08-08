Title: Creating a profiler for goputer
Summary: Sometimes you have to do some measuring
Authour: Oscar Peace
Tags: Goputer
      Projects
      Go
Published: 09/08/2025

*Note: This is a continuation from my [previous post](/blog/writing-software-renderer).*

For a while now, goputer has had no way of measuring performance. The closest you could get was adding a frame rate counter to a frontend and hoping it would be somewhat accurate - spoiler, it wasn't. Turns out it takes a lot longer to render a frame than to add two numbers together, who would've guessed. This necessitated the creation of a better solution: a profiler.

I wasn't aiming for anything complex, such as Google's [pprof](https://github.com/google/pprof), instead I was just intending to measure how long each instruction took to run, then do a tiny bit of statistics to make the collected values slightly more useful. If anything it would also serve to highlight any outstanding issues with the core runtime in addition to any assembly I wrote.

# Design

My only experience using anything that could be considered a profiler thus far had been using browser dev-tools, which are much more complicated than anything I intended to make and are made for a very different domain. As such, I settled upon a very simple way of measuring performance:

1. Measure the time for each cycle
2. Add that data to an entry in a hashmap
3. Do some additional stuff to calculate the mean etc. at the end

As for the design I decided on a `Profiler` type which would have a `Data` field of type `map[uint64]*ProfileEntry` (the pointer was so I could change values in place), `ProfileEntry` would contain various data about that **specific** instruction - total cycle time, times executed.

The key for the map was created by packing the instruction (5 bytes) and the current program counter value, sort of akin to a [composite key](https://en.wikipedia.org/wiki/Composite_key). While this meant that only 3/4 bytes were available for the program counter value (largest value 16,777,215 so 16MB) the default memory addressable (not including the video buffer) size for goputer is 65KB, so I don't see this as being a problem, unless the program counter is overwritten. If I wanted to in the future I could change the key to two uint64's or just 9 bytes.

| Instruction | Address |
| ----------- | ------- |
| 40 bits     | 24 bits |

Now I had collected the data I needed some way to store it. While I could have simply just dumped the entire thing to a JSON file and been done with it, however this had a major drawback of being slower and the file size being larger. Also I just needed to store numbers.

All byte orders are little endian.

| Magic number | Number of entries | Total cycles     | Entries           |
| ------------ | ----------------- | ---------------- | ----------------- |
| `GPPR`       | 8 bytes (uint64)  | 8 bytes (uint64) | Variable 33 bytes |

Each entry was further broken down as follows:

| Instruction | Address          | Total cycle time | Total times executed | Standard deviation |
| ----------- | ---------------- | ---------------- | -------------------- | ------------------ |
| 5 bytes     | 4 bytes (`uint32`) | 8 bytes (`uint32`) | 8 bytes (`uint32`)     | 8 bytes (`float64`)  |

*Note: The standard deviation is technically stored as a uint64 in little-endian order, see [`math.Float64bits`](https://pkg.go.dev/math#Float64bits) which does some `unsafer.Pointer` stuff, specifically `*(*uint64)(unsafe.Pointer(&f)`, where `f` is the `float64` in question.*

To make things a bit nicer the `Load` and `Dump` methods both used Go's `io.ReaderSeeker` and `io.WriterSeeker` interfaces respectively.

# Making it useful

Collecting all this information was okay, but it was pretty useless on it's own unless you like reading binary file formats or printed structs. I needed some way to display it, for this I chose [`tview`](https://github.com/rivo/tview), a TUI framework, as while there already some small GUI apps I had developed for goputer, most notably the launcher, they really should have been console apps instead.

![](/content/assets/goputer/profiler/profiler.png "The profiler UI, with instructions sorted by times executed")

In the above screenshot, the source for the executable being analysed is available [here](https://github.com/sccreeper/goputer/blob/73942d06998e8cf1fea7e3e2a41acc92bf566660/examples/area_test.gpasm). As you have may have noticed there is also an option for grouping, this simply groups instructions which have the same opcode together and aggregates their data (apart from standard deviation and addresses).

![](/content/assets/goputer/profiler/profiler%20grouped.png "Profiler with grouping enabled")

You can also jump to instances of specific instructions using the "instruction" field. The first screenshot is much closer to the original representation of the data.

As a side-note, the numbers in that screenshot are much higher than they should be, in canned benchmarks they were much lower, my current theory is that for some reason running a windowed application in WSL is slower than a non-windowed one. I'll only find out for sure once make goputer run natively (on Windows without WSL) though.

Another useful addition might be to add some other form of visualisation (i.e. barcharts) however I can't really see the utility of it over the existing data view.

# What next?

Now armed with a profiler I can hopefully go about creating more complex programs and maybe even high level language, using the profiler to make performance analysis ever so slightly easier.

This was the one of the last major improvements I had planned for goputer. The ones that are most likely to be developed next are moving frontends to standalone executables instead of using Go's `plugin` library, which only works on Linux, FreeBSD, and MacOS, so no Windows support at all, and moving extensions to embedded Lua for the same reason. Software rendering doesn't show in the Python frontend/the Python frontend hasn't been updated since software rendering was implemented so that'll have to be fixed as well.

Also at the moment the profiler is currently just tacked onto the gp32 runtime without any way of turning it off, but that'll come as part of the previously mentioned frontends to standalone executables thing.

If you want to see any other posts linked to Goputer, click [here](/posts?tags=goputer) or the repository itself is [here](https://github.com/sccreeper/goputer).