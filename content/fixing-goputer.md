Title: Fixing my fantasy virtual machine
Summary: Removing a lot of tech debt
Authour: Oscar Peace
Tags: Go
      Goputer
      Projects
Published: 24/4/2025

When I first started [goputer](https://github.com/sccreeper/goputer) I had very little idea how compilers worked. I thought I had enough of an idea how computers worked (fetch execute cycle so on) in order to build a model that wasn't too far fetched. I also was writing it in Go, as my first major project using the language. This decision to use a language which I had never even written a "Hello World!" in before resulted in some rather shoddy code and as a result a lot of tech debt.

Fast forward almost 3 years since I started and a lot has changed. I'm now at university doing this computer science thing "properly" and I understand Go and it's idioms much better than I did previously, at least I think so anyway. The original model I based goputer on has held up reasonably well, which luckily means no major underlying things need changing. What does need changing however, is the original assembly language I designed. 

I figured that the removal of the tech debt was going to be a gradual rather than instant process, hoping that it wouldn't acquire too much interest as I developed the project further. Another saving grace would be redoing some fundamental parts (I'm hoping to write a software rasteriser in the future, instead of each frontend having it's own rendering logic) which would allow me to take a bulldozer to some parts without knocking the whole house down. Firstly, I started with redoing the assembly language.

# Fixing the assembly

This wasn't really a problem with the assembly language per se, but it isn't important enough to deserve it's own subheading. For some reason I decided that the halt instruction (which takes milliseconds to stop for as an argument) should block the main thread instead of using $\Delta t$. This was especially annoying on the [JavaScript frontend](https://goputer.oscarcp.net/) where you couldn't do *anything*, arguably a skill issue on my part but whatever. Thank you Brendan Eich for nothing. This is now fixed.

Back to the assembly language. Much like the aforementioned [JavaScript](https://github.com/denysdovhan/wtfjs), there were many inconsistencies and flaws. The main thing that was wrong was the lack of consistency when it came to syntax - mainly compiler directives. There were 2 visually distinctive ways to declare something that should be used by the compiler:

```plaintext

def defined_colour 0xFF0000FF

:jump_block

end

intsub kd jump_block 

```

The problem with the first and last line is that they are both compiler statements, however they take the visual form of instructions. While they can be distinguished by length it is possible for definitions at least, to make them shorter:

```plaintext
// A definition

def reg 1

// An instruction

mov r00 r01
```

While the above example would arguably be considered bad practice and may not be a problem for someone familiar with the language, it is still possible to do it. The interrupt subscription is only longer because of it's initial `intsub`, but it still follows the same form as most instructions (`<instruction> <reg> <reg>`). In order to differentiate compiler directives from instructions (which were the only thing important to the VM) I decided that they should be prefixed with a # similar to C preprocessor directives. With this in mind they now looked like this:

```plaintext
#def reg 1

#intsub kd jump_block
```

Now I just had to fix the biggest problem with the language: "jump blocks". Instead of using the same concept utilised by virtually every other assembly language - [labels](https://en.wikipedia.org/wiki/Label_(computer_science)) - I made these things called "jump blocks", so called because it was a block of instructions you could **only** jump to or call. Due to this restriction, and a forced return, these were more akin to procedures/functions than labels. Not really something you want in a low level language. This also made writing any form of branching borderline impossible as the place you wanted to branch to had to be somewhere else entirely, it couldn't be contiguous with the current sequence of instructions. 

```plaintext
// A jump block

:some_code

end

// A label

#label some_code

```

I understand that labels in many languages don't actually tell you what they are, and are more of a syntax feature but goputer is meant to be easy to learn (for beginners). This addition now made it slightly easier to write branches. In hindsight I could have kept the jump blocks but because they are effectively redundant when considering the existence of labels there's no point.

One other reason why it was so difficult to write branches was because of a lack of a return instruction. As mentioned previously, there was forced return with the jump blocks but this required some serious mental gymnastics to work with, so I added a interrupt return (`iret`) and return (`ret`) instruction. Now all the foundational problems (for the most part) had been fixed.

# The parser

The previous parser was incredibly basic. Each line was considered to be it's own statement and it just walked through them all and just did `line.split(" ")` before some if statements to determine what each line was. This made it difficult to add anything new as I had to figure out where to add it in the spaghetti mess of if-else code before making sure it didn't conflict with anything else it wasn't meant to.

The rewritten parser still follows the same mantra of going line by line (multiple line expressions don't exist yet) however it now uses regex for determining (and for some part parsing) statement types instead of splitting and character checking. This should make it easier to add new types of statements as all I have to do now is write a regex expression and add an if statement instead of burying it in an entangled nest of spaghetti.

It still doesn't follow the same exact steps used by other parsers (tokenization, AST generation, parsing), instead these steps are kind of combined into one. When I write a high level language that is more syntactically complex then I would apply these steps however the assembly language is rather simple. There is also no basic code generation for making writing common instruction sequences easier (or even meta instructions) however this shouldn't be too difficult to add later down the line now.

# Bytecode generation

The bytecode generation for the most part was quite easy, as there weren't any major changes to individual elements, apart from some of them being removed and then moved around accordingly. Beforehand the generated "executable" if you will, had these elements:

1. File identifier (`GPTR`)
2. Header
3. Data block
4. Jump blocks
5. Interrupt table
6. Instructions/entry point

The header contained the location (relative to the file) of each of these segments minus itself and the file identifier. The new format didn't require the jump blocks anymore and the interrupt table was technically part of the header anyway so that was moved as well:

1. File identifier (`GPTR`)
2. Header
3. Interrupt table
4. Data block
5. Instructions

This finalized version was relatively easy to output albeit some minor issues concerning me forgetting to add an entrypoint location and calculating incorrect locations for some parts. More on the executable format can be found on the wiki [here](https://github.com/sccreeper/goputer/wiki/Executable-format/).

# The future

There are 3 main goals I'd like to accomplish with goputer as I continue developing it, they are:

- Extending compatibility to other platforms. At the moment it only works on Linux which [isn't great but not terrible](https://youtu.be/uL8ZmYf9pX4) either. Before I first tried [developing with WSL](/blog/developing-on-windows) I briefly tried to get it working on Windows but this wasn't to much avail. This is mainly down to how it utilises Go's plugin package to load frontends which at the moment [only works on Linux](https://github.com/golang/go/issues/19282), and it seems likely it'll stay like this for the foreseeable future.
- Creation of a high level language. The assembly language is okay but using it for complex programs isn't ideal. This will probably be a rather significant undertaking as I currently lack a lot of the knowledge required to do it properly.
- Moving rendering to a software rasteriser. This should be the easiest thing to do (frankly it is also the most appealing) and should solve a long standing problem of a program rendering differently depending on the frontend being used. It'll also allow for the framebuffer to be accessed by the program which means it should be possible to do some advanced-ish rendering.

I'm also considering writing a VSCode extension or an IDE, not really sure what would be more beneficial at this stage. 

With all of this in mind I'm happy to be working on this again and as I write this the first year at university is almost over so I should have plenty of time soon enough.