Title: Optimising Go with SIMD assembly
Summary: Rendering is slow, but it can be made a lot faster
Authour: Oscar Peace
Tags: Go
      Goputer
      Projects
      Optimisation
      Assembly
      Avo
Published: 21/01/2026

*Note: This is a continuation from my [previous post](/blog/making-pong-in-goputer).*

Ever since goputer's switch to software rendering - instead of relying on frontends to do rendering operations themselves in hardware - drawing anything to the screen has been a bit of a bottleneck. Turns out doing stuff in hardware is a lot faster than doing it in software, especially when because of some very bad decisions earlier on, none of these operations are using 4 bytes and thus cannot be easily vectorised by a good compiler[^bytesimd].

The following post details my experience optimising my Go code with assembly. If you are already familiar with SIMD operations then feel free to skip the next section, however it may be helpful for anyone else who isn't. This article focuses on x86 vector instructions, however the principles of SIMD are the same for all CPU architectures.

# What is vectorisation and SIMD?

Firstly SIMD stands for:

- **S**ingle
- **I**nstruction
- **M**ultiple
- **D**ata

In essence this means that for a given instruction, which has multiple parameters (registers and/or memory locations), these parameters may themselves contain multiple pieces of data to be operated on in parallel.

Also, as opposed to scalar instructions which will operate on standard sized registers, vector instructions mostly operate on **vector registers**. On x86 vector registers can be 128, 256, or 512 bits wide.

@red Vector @isation refers to the process of rewriting a piece of code to make use of @red vector @ instructions.

A very simple example of vectorisation would be to say you had a loop which added two (very long) arrays together. Below is some Python[^pythonvector] pseudocode to demonstrate this:

```python

a = [x for x in range(1024)]
b = [x for x in range(1024)]
result = []

for i in range(len(a)):
    result.append(a[i] + b[i])

```

Traditionally the above code would be executed in a **scalar** manner. I.e. one addition would have to be executed for every pair of integers, a and b. This means that 1024 additions would have to be performed. While this may execute fairly quickly for small-ish arrays of integers such as this, it will get increasingly slower as the arrays grow.

A "vectorised" version of the above code would be as follows (for this example, a and b can be thought of as an array of `uint32`'s):

```python

a = [x for x in range(1024)]
b = [x for x in range(1024)]
result = []

for i in range(0, len(a), 16):
    c = vpaddd(a[i:i+16], b[i:i+16])

    result.extend(c)

```
*Note: The `extend` method is used to concatenate the two lists together.*

Compared to before we are now adding 16 integers together at a time, instead of just 1. This means our code will now execute (in theory) 16x faster.

Our `vpaddd` function can be thought of as an instruction intrinsic. An intrinsic is a "function" that tells the compiler that you want this operation to be carried out with this specific instruction. In our case, `vpaddd` refers to the "Add Packed Integers" instruction, specifically adding packed doubles - a packed instruction operates on values of it's size (byte/word/double etc.) as opposed to treating the register like one big number. In real code which uses intrinsics this would be `_mm_add_epi32`[^addintrinsic].

In our case, each integer is 32 bits wide, and we are using 512 bit `zmm` registers when performing the add instruction.

![](/content/assets/goputer/simd%20optimisation/pre%20simd%20add.png "Values in ZMM registers before adding, when i is zero")

The offset value in the above diagram refers to the number of bits each value is offset from the start of the register. Typically a vector register would be displayed with it's most significant bit first, but in this article, the least significant bit is displayed first.

We then perform the `vpaddd` instruction:

```x86asm
vpaddd zmm2, zmm1, zmm0
```

This takes each packed (packed, i.e. they are stored next to each other in the register, no gaps) double-word (32 bit integer)[^byteworddouble] in `zmm0` and `zmm1`, and adds them together, storing the result in `zmm2`. In Intel assembly syntax, operands follow the order of `destination, source`.

After we perform our `vpaddd` instruction, `zmm2` now has our result:

![](/content/assets/goputer/simd%20optimisation/post%20simd%20add.png)

In reality our `.extend` operation at the end would translate to a `vmovdqa64` (move double quadword aligned) instruction, in order to move our data back to our result array.

```x86asm
vmovdqa64 [rax], zmm0 
```
*Note: The register `rax` contains our current offset in our storage array. In practice any large enough register could contain this value.*

Adding isn't the only operation you can perform on a vector register though. Pretty much any operation that can be applied to a scalar register can be applied to vector registers as well, whether it be other arithmetic operations such as multiplication, or logical operations, and shifting.

There also exists a set of instructions specifically for operating on vector registers, such as broadcasting, shuffling, extraction/insertion, or other permutations. How these work will be detailed in the rest of the post.

# Using assembly with Go

The first half of this section focuses on writing raw assembly for use with Go, and the second half focuses on making use of the Avo library. I would recommend reading both halves as it is important to understand the assembly that Avo generates, and it is also sometimes easier to debug your code by reading the generated assembly.

## Raw assembly

*Note: From now on, Go's Plan9 inspired assembly syntax is used, the main difference being the order of operands is different (source, destination).*

Go makes it quite easy to link with assembly. It is used a lot in the standard library, especially in the `math` package, to make use of hardware specific features for various operations.

For example [`math/exp_amd64.s`](https://github.com/golang/go/blob/455282911aba7512e2ba045ffd9244eb97756247/src/math/exp_amd64.s) contains optimised code for calculating a base $e$ exponential.

A much simpler example would be something that [adds two numbers](https://github.com/mmcloughlin/avo/tree/c096992c06ffcc996c6ebb924d9d5cf1e53e49d4/examples/add)[^avocredit], i.e:

```x86asm
#include "textflag.h"

// func Add(x uint64, y uint64) uint64
TEXT ·Add(SB), NOSPLIT, $0-24
	MOVQ x+0(FP), AX
	MOVQ y+8(FP), CX
	ADDQ AX, CX
	MOVQ CX, ret+16(FP)
	RET
```

An explainer on the syntax used above:
```x86asm
TEXT ·Add(SB), NOSPLIT, $0-24
```
Above is the function declaration. `SB` is a virtual register used to refer to the static base pointer, which can be thought of as the origin of memory.

Names and descriptions for the pseudo-registers from the [Go documentation](https://go.dev/doc/asm):
> - FP: Frame pointer: arguments and locals.
> - PC: Program counter: jumps and branches.
> - SB: Static base pointer: global symbols.
> - SP: Stack pointer: the highest address within the local stack frame.

`NOSPLIT` tells the compiler not to insert a special piece of code that checks if the stack needs to grow. I don't fully understand this myself, and for our purposes it isn't important, but for those interested there is a detailed explanation in [this blogpost](https://mcyoung.xyz/2025/07/07/nosplit/) by Miguel Young de la Sota.

`$0-24` specifies the size of the stack frame for this function.

The move instruction, `MOVQ x+0(FP), AX`, can be read as: move the parameter `x`, offset zero bytes from the frame pointer `FP`, to the register `AX`. The same applies to the second move instruction, except an offset of 8 bytes instead of 0.

The final move instruction can be read as: move the value in `CX` to the return parameter, offset 16 bytes from the frame pointer.

This can then be linked to the following method stub:

```go
func Add(x uint64, y uint64) uint64
```

The method stub can then be used in any normal Go code, just as a normal function would.

While the above approach might be okay for writing small functions, as functions and their requirements get larger, and worrying about argument sizes, constant data, and register allocation becomes a problem, it might be useful to have some way to take this "boilerplate" work away.

## Here comes Avo

[Avo](https://github.com/mmcloughlin/avo) is a Go library that can be used to generate assembly by just writing normal Go code. The assembly example used previously was actually from Avo's examples directory. You still have to "write" the assembly yourself, but Avo will take care of all the boring stuff like argument sizes and Plan9 syntax for you.

Here is the Go code which could have be written instead to generate that assembly - in Avo, as in Go's assembly, operands follow a source, dest order:

```go
import . "github.com/mmcloughlin/avo/build"

func main() {
	TEXT("Add", NOSPLIT, "func(x, y uint64) uint64")
	
    x := Load(Param("x"), GP64())
	y := Load(Param("y"), GP64())
	
    ADDQ(x, y)
	
    Store(y, ReturnIndex(0))
	RET()
	
    Generate()
}
```

Notice how `x` and `y` are now actually variables, in this case virtual registers (64 bit) which have been allocated for us and initialized by Avo.

We then use the `Store` method to generate the instruction which pushes the result back onto the stack.

Avo also generates the stub file as well.

# Using SIMD with Go

As stated previously, the primary operation I wanted to optimise with SIMD was rendering. This is not only because it was a bottleneck, but also because rendering is an ideal candidate (or in my case slightly less than ideal) for a SIMD workflow.

In my case, I also couldn't use any AVX-512 instructions as my CPU does not support it.

## Video clearing

The first operation I wanted to make use of SIMD was `int vc`, or video clear interrupt. While a better approach could have been to make use of the `rep movsb` instruction, as I didn't care what was already in the buffer, just replacing it, the buffer format (RGB8), meant that this was not possible.

The steps I needed to take in order to do this were as follows:

1. Assemble the colour
2. Move the colour data to memory

"Assembling" the colour meant loading the RGB values from the parameters, then placing this data in the correct order in a vector register, or actually multiple, in order for it to be ordered properly.

Loading the parameters then ordering the colour correctly in a 32 bit register is quite simple:

```go
red := Load(Param("red"), GP8())
green := Load(Param("green"), GP8())
blue := Load(Param("blue"), GP8())
tmp := GP32()

MOVL(U32(0), tmp)
MOVB(blue, tmp.As8())
SHLL(Imm(8), tmp)
ORB(green, tmp.As8())
SHLL(Imm(8), tmp)
ORB(red, tmp.As8())
```

The value in this register can then be moved to an XMM register using a `MOVD` (move double word) instruction. Also a quick note, x86 is **little endian**, which means that the byte with the lowest value is stored first. This is why we move the blue first, then green, then red, as opposed to the other way round. This is important when we consider the order of bytes in the XMM register.

Once we've constructed the colour, we can move it to the lowest 4 bytes of the XMM register:

```go
MOVD(tmp, xmm0)
```

Once this data was in XMM, the rest of XMM needed to be filled with it. Also because it was a 3 byte pattern, and XMM registers are 16 bytes wide, the pattern would have to be repeated across 3 XMM registers in order to work properly.

An appropriate instruction for this is the shuffle instruction, specifically [`PSHUFB`](https://www.felixcloutier.com/x86/pshufb) or *Packed Shuffle Bytes*. It will re-order the contents of one vector register, when given a shuffle mask contained in another. TLDR; When given source `x`, destination `y`, and mask `m`, `y[i] = x[m[i]]`. 

![](/content/assets/goputer/simd%20optimisation/simd%20shuffle.png "Values are coloured to show which index the mask sources it's value from")

In this case the register is filled with a **@#d623f4 purple-ish @** colour.

Or in code:

```go
shuffle_mask := GLOBL("shuffle_mask", RODATA|NOPTR)
DATA(0, String([]byte{0, 1, 2, 0, 1, 2, 0, 1, 2, 0, 1, 2, 0, 1, 2, 0}))

VPSHUFB(shuffle_mask, xmm0, xmm0)
```

There is a problem here, because the mask is not a complete sequence, that is it ends in zero, instead of 2, multiple registers with slightly different masks must be used, in order to form one complete sequence.

```go
first_mask := GLOBL("first_mask", RODATA|NOPTR)
DATA(0, String([]byte{0, 1, 2, 0, 1, 2, 0, 1, 2, 0, 1, 2, 0, 1, 2, 0}))
second_mask := GLOBL("second_mask", RODATA|NOPTR)
DATA(0, String([]byte{1, 2, 0, 1, 2, 0, 1, 2, 0, 1, 2, 0, 1, 2, 0, 1}))
third_mask := GLOBL("third_mask", RODATA|NOPTR)
DATA(0, String([]byte{2, 0, 1, 2, 0, 1, 2, 0, 1, 2, 0, 1, 2, 0, 1, 2}))

MOVD(tmp, xmm0)
VPSHUFB(first_mask, xmm0, xmm0)
VPSHUFB(second_mask, xmm0, xmm1)
VPSHUFB(third_mask, xmm0, xmm2)
```

Once we have shuffled the contents correctly for each register, we can store that data in memory:

```go
Label("loop")

VMOVDQA(xmm0, Mem{Base: ptr})
VMOVDQA(xmm1, Mem{Base: ptr, Disp: 16})
VMOVDQA(xmm2, Mem{Base: ptr, Disp: 32})

VMOVDQA(xmm0, Mem{Base: ptr, Disp: 48})
VMOVDQA(xmm1, Mem{Base: ptr, Disp: 64})
VMOVDQA(xmm2, Mem{Base: ptr, Disp: 80})

VMOVDQA(xmm0, Mem{Base: ptr, Disp: 96})
VMOVDQA(xmm1, Mem{Base: ptr, Disp: 112})
VMOVDQA(xmm2, Mem{Base: ptr, Disp: 128})

VMOVDQA(xmm0, Mem{Base: ptr, Disp: 144})
VMOVDQA(xmm1, Mem{Base: ptr, Disp: 160})
VMOVDQA(xmm2, Mem{Base: ptr, Disp: 176})

ADDQ(Imm(192), ptr)
CMPQ(ptr, max)
JBE(LabelRef("loop"))
```

`max` is a value calculated before this (unrolled[^unrolling]) loop which stores the bounds of the array. The `Mem` struct tells avo to interpret this argument as a memory address, with the start (base) of this address being the value of `ptr`, and then offset by the value of `Disp`.

`VMOVDQA` is the "Move Double Quadword Aligned" instruction, which moves the vector register to main memory and vice versa. The "Aligned" part means that the location must be aligned on a certain boundary, in our case 8 bytes as we are targeting a 64 bit system. This is because CPUs **mainly** access memory in terms of their word size, which on a 64 bit system is 8 bytes, this tends to be faster than doing an *unaligned* memory operation.

## Video areas

A "video area" (`int va`) is the term used in goputer for drawing a rectangle to the screen. The logic for drawing an opaque video area is broadly the same as video clearing, apart from a different loop, so I have decided not to include it for brevity. Instead, this section focuses on drawing a transparent area and the additional code which is required to do that.

The main differences between drawing opaque colour, and transparent colour, is that we now need to not only load data from memory beforehand, but also perform arithmetic on it.

Because goputer's framebuffer doesn't actually store alpha values, blending is done in a sort of fake way:

$$
dest_R = ((src_R \times src_A) + (dest_R\times \lnot src_A)) \gg 8
$$

Or in a code form:

```go
dest[0] = byte((int(src[0])*int(src[3]) + int(dest[0])*^src[3]) >> 8)
```

Fortunately, this is fairly easy to vectorise. The first part of the operation, $(src_R \times src_A)$, can be performed ahead of the main loop because it is constant for each channel. However, before we do that, the byte values in the register need to be widened to 16 bit words, in order to avoid overflow and preserve accuracy.

This can be done with the `VPMOVZXBW`, or packed move ith zero extend, instruction. In our use case, it will take every byte in a XMM register, zero extend (which is to say it pads it with extra zeros instead of just inserting it with garbage data) it to a word, before packing those words into the YMM register. For the alpha channel, where the alpha value is 230 (0xE6), which will become 0x00E6 when widened:

![](/content/assets/goputer/simd%20optimisation/simd%20widen%20zero%20extend.png)

In order to fill the alpha register with both the inverted and inverted alpha values before it is widened, the `VPBROADCAST` instruction (specifically with the `B` for byte suffix) can be used. This instruction tells the CPU to take the first byte/word/double word etc. of this register, and then fill this other (or the same) register with it.

![](/content/assets/goputer/simd%20optimisation/simd%20broadcast.png)

With all the data in place, now the final colour result needs to be calculated. As mentioned previously, there exists a set of instructions for operating on packed values. So calculating the first part of the expression is as follows:

```go
VPMULLW(widened_shuffled_colour_bytes, widened_alpha_values, widened_shuffled_colour_bytes)
```

This instruction multiplies each packed word, and then stores the low (bits 0-16) result.

As for computing the rest of the expression, firstly the data needs to be loaded from memory and widened. Also, unlike before where the data in memory could be discarded, this time the 16th byte needs to be preserved for the next iteration - we are only writing 15 bytes at a time. This can be done with the `PEXTRB` and `PINSRB`, extract byte and insert byte respectively, instructions. I **wouldn't actually recommend** using these, as you will see later, but I am including them here so you can learn from my mistakes.

Load memory data, and extract last byte:
```go
VMOVDQU(Mem{Base: RDI}, memory_data)
XORL(last_byte, last_byte)
PEXTRB(Imm(15), memory_data, last_byte)
```

`Imm(15)` tells Avo that this an immediate value - a value embedded in the instruction operands, as opposed to being stored in a register or memory. In this case it will automatically determine the size, but similar functions exist for generating an immediate of a specific size.

Widen memory data, then multiply it with the inverted alpha values.

```go
VPMOVZXBW(memory_data, widened_memory_data)

// "Multiply Packed Signed Integers and Store Low Result"
VPMULLW(widened_memory_data, widened_inverted_alpha_values, widened_memory_data)
```

Finally, add the two values together and perform the packed shift operation:

```go
// "Add Packed Integers"
VPADDW(widened_memory_data, widened_shuffled_colour_bytes, widened_memory_data)

// "Shift Packed Data Right Logical"
VPSRLW(Imm(8), widened_memory_data, widened_memory_data)
```

Now the values had been calculated, they need to be packed back down into bytes, and stored back into main memory.

To pack the numbers back down, `PACKUSWB` ("Pack With Unsigned Saturation") is used. Saturation refers to how the words (which can be from 0-65535) are compressed back down into the byte range of 0-255. If the value is $\gt 255$, then it is clipped at 255. If it is $\lt0$, then it is clipped at zero. If in-between, then it is kept the same.

Because the pack instruction operates on 128 bit lane of the YMM register in order to operate on data in a stream, and per lane, the colour values are now split between each lane, note that this takes place after the rightwards shift, hence each value starts with 0x00:

![](/content/assets/goputer/simd%20optimisation/pack%20word%20to%20byte.png "Values which be kept are in bold. Line through centre is at the lane border.")

Luckily this can be rectified with the `VPERMQ` (Qwords Element Permutation) instruction. This instruction functions in a similar way to the shuffle instruction from earlier, but this time it operates on quad-words (64 bit) and the mask is only one byte, with four two bit values for the locations. The 256bit YMM register is split up into 4 quad-word slots.

In this case the mask is `0xD8`, or `0b11011000` in binary form. The source in the mask is implicit, based on the location of the bits within the mask.

| Bits | Source | Destination |
| ---- | ------ | ----------- |
| 00   | Q0     | Q0          |
| 10   | Q1     | Q2          |
| 01   | Q2     | Q1          |
| 11   | Q3     | Q3          |

The result:

![](/content/assets/goputer/simd%20optimisation/simd%20permute.png)

When all the data is in the correct place in YMM, the lower lane (bits 0-128) can be extracted and placed in XMM. This data can then be placed back into memory, but only after the last byte is inserted.

```go
VEXTRACTI128(Imm(0), widened_memory, memory_data)

PINSRB(Imm(15), last_byte, memory_data)
VMOVDQU(memory_data, Mem{Base: RDI})
```

*Note: This time the move instruction is the **unaligned** variant, as the pointer is incremented by 15 bytes each time, which is not a proper number for correct alignment.*

All of the code in this section has been extracts from the routine used in goputer, which is available [on GitHub](https://github.com/sccreeper/goputer/blob/668142325cf8a3f1ab1b9b425dbc34162c1820ab/pkg/vm/asm/video_area_alpha.go). The next section explains the rest of that routine in a bit more detail, it is not necessary to understand [the conclusion](#is-it-actually-faster) sections so feel free to skip it.

### Extra notes on the loop implementation

The loop itself is a standard `for y { for x }` style loop:

```go
Label("a_loop")

MOVQ(ptr, RDI)

CMPL(width, Imm(5))
JB(LabelRef("a_blit_remaining"))

Label("a_loop_x")

// 
// Loop body
// 

Label("a_loop_end")

XORL(counter_x, counter_x)
ADDQ(U32(960), ptr)
INCL(counter_y)
CMPL(counter_y, rows)
JB(LabelRef("a_loop"))
```

The body of the loop contains an additional branch to check if we are drawing $\lt5$ pixels ($15\text{ bytes}\div3=5$). This contains instructions which draw in a scalar as opposed to vector manner:

```go
MOVBWZX(Mem{Base: RDI}, tmp_16)
IMULW(inv_alpha_16, tmp_16)
ADDW(red_16, tmp_16)
SHRW(Imm(8), tmp_16)
MOVB(tmp_16.As8L(), Mem{Base: RDI})
```

The instructions are the same for red and green, but with a `Disp` value in the `Mem` struct of 1 and 2 respectively.

# Is it actually faster?

Now only one question remained:

**"Is this faster than before?"**

After all, it would be a bit pointless if it wasn't.

According to goputer's builtin profiler the video clear operation was now **~16% faster** in canned benchmarks[^benchmarks]. Not exactly a huge improvement but still something.

The video area operation with no alpha was actually on par with the scalar code from before. I tried optimising it further with cache prefetch instructions but these had no measurable effect.

Initially, the alpha area operation was **slower**, but after removing the extract/insert byte instructions and replacing them with normal memory -> register and vice versa move instructions, there was a **~60%** improvement.

The final code examples used in this article, after improvements are:

- [pkg/vm/asm/video_area.go](https://github.com/sccreeper/goputer/blob/850f3c482ba84b935bb27c9111bfd322edc5af16/pkg/vm/asm/video_area.go)
- [pkg/vm/asm/video_area_alpha.go](https://github.com/sccreeper/goputer/blob/850f3c482ba84b935bb27c9111bfd322edc5af16/pkg/vm/asm/video_area_alpha.go)
- [pkg/vm/asm/video_clear.go](https://github.com/sccreeper/goputer/blob/850f3c482ba84b935bb27c9111bfd322edc5af16/pkg/vm/asm/video_clear.go)

# Conclusion

In conclusion, while some of the improvements made aren't exactly as much as what is theoretically possible with SIMD, they are still something. At the end of the day computers are very fast, and as such will run un-optimised code just as well as optimised code. 

As I write this, Go is planning to add experimental support for [vector operations](https://antonz.org/go-1-26/#simd) as a builtin feature in the standard library in the next version, 1.26. So if I had done this a few months later it might have been a lot easier, and in the future it'll hopefully support more architectures (even including WASM), so I won't have to touch assembly at all. On the other hand, it has certainly been very interesting learning the ins and outs of x86 assembly and SIMD in particular.

Finally, apart from the addition of a high level language, the rest of the improvements I have [planned](https://github.com/sccreeper/goputer/issues) for goputer are fairly minor things, so there *probably* won't be another post like this for a while. For now, look at the other posts on [goputer](/posts?tags=goputer) or the repository [itself](https://github.com/sccreeper/goputer).



[^bytesimd]: SIMD instructions work better when using multiples of 4 elements, see this [ARM documentation](https://learn.arm.com/learning-paths/cross-platform/vectorization-friendly-data-layout/data-layout-basics-2/).

[^pythonvector]: In reality the reference Python interpreter, CPython, does not vectorise code. Vectorisation in Python can be achieved by using libraries such as [numpy](https://numpy.org/).

[^addintrinsic]: See [paddd](https://www.felixcloutier.com/x86/paddb:paddw:paddd:paddq#intel-c-c++-compiler-intrinsic-equivalents) on the x86 reference.

[^byteworddouble]: On x86 the terms byte (8 bits), word (16 bits), double-word (32 bits), and quad-word (64 bits) are sometimes used to denote integer sizes.

[^avocredit]: This example is from the `avo` library.

[^unrolling]: "Unrolling" refers to the practice of including multiple iterations of a loop in it's body, in order to reduce the total number of branches which occur.

[^benchmarks]: 
    Benchmarks were conducted using these examples and this hardware.

    - **Video clearing:** [examples/video_clear_bench.gpasm](https://github.com/sccreeper/goputer/blob/850f3c482ba84b935bb27c9111bfd322edc5af16/examples/video_clear_bench.gpasm)
    - **Video area, no alpha:** [examples/area_test.gpasm](https://github.com/sccreeper/goputer/blob/850f3c482ba84b935bb27c9111bfd322edc5af16/examples/area_test.gpasm)
    - **Video area, with alpha:** [examples/alpha_area_test.gpasm](https://github.com/sccreeper/goputer/blob/850f3c482ba84b935bb27c9111bfd322edc5af16/examples/alpha_area_test.gpasm)

    System specification:

    - **CPU:** Ryzen 7 7730U (8C, 16T)
    - **Memory:** 16GB
    - **WSL OS:** Fedora 42, 6.6.87.2-microsoft-standard-WSL2
    - **Host OS:** Windows 11, 10.0.26200