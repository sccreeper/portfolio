Title: Making an 8 bit adder-subtractor in Minecraft
Summary: Most un-optimised calculator
Authour: Oscar Peace
Tags: Minecraft
      Logic
      Hardware
Published: 22/12/2024

***Note:** This post assumes that you have familiarity with positive binary decimal conversion and logic gates.*

Part of my course at university covers logical circuits, the most basic of these being an adder. I've also always wanted to make something like this in Minecraft, I'd always download computer/calculator maps when I was younger; and then break them while trying to figuring out how they work. What I built wasn't the most optimised or compact way of building an adder in Minecraft (some logic gates are much larger than others), however it did work. This article goes through some of the theory of adders and documents building one in Minecraft.

# The half adder

In order to add 1 bit, you need something called a half adder. This doesn't exactly take care of carrying properly but it can be combined with another half adder in order to create a full adder.

![](/content/assets/minecraft%20adder%20subtractor/diagrams/half%20adder.png)

Of course building one in Minecraft is slightly different as there are no discrete blocks for logic gates. Instead you must construct the logic gates block by block which means that some gates are much larger than others. Especially the XOR gate which is *the main gate* for adders/subtractors. A full list of the logic gate schematics can be found on the wiki [here](https://minecraft.wiki/w/Redstone_circuits/Logic).

![](/content/assets/minecraft%20adder%20subtractor/screenshots/half%20adder%20ingame.png "The unconnected redstone lines are the inputs and outputs.")

# Full adder

The full adder consists of two half-adders connected together with an additional input for any carry over from a previous full adder. This carry input will come in helpful when dealing with [two's complement](#adder-subtractor) later as well.

![](/content/assets/minecraft%20adder%20subtractor/diagrams/full%20adder.png)

This is again the same in Minecraft, and once again is larger:

![](/content/assets/minecraft%20adder%20subtractor/screenshots/full%20adder%20ingame.png)

If you want to create a multi-bit adder then you connect the carry line from the first adder into the second adder, then second to third, third to forth, and so on.

# Multi-bit adder

A 1 bit adder on it's own is a bit useless, because the biggest number is $ 2^1 $ bits i.e. 1. However adding more bits is easy. As described previously you just chain the adders together with the carry of the previous adder going into the carry in of the next adder:

![](/content/assets/minecraft%20adder%20subtractor/diagrams/multi%20bit%20adder.png)

Doing this in Minecraft is practically the same, however it just takes longer:

![](/content/assets/minecraft%20adder%20subtractor/screenshots/multibit%20adder%20ingame.png)

In the above screenshot the carry line for each full adder is the sunken bit of redstone, in-between the previous and next adder. Each full adder is highlighted by a red box.

# Adder subtractor

One (and the most common) way of representing numbers in binary is to use two's complement. The steps to converting a normal decimal number to this format are as follows:

1. Convert the number to normal binary.
2. Flip all the bits, i.e. a one becomes a zero and a zero becomes a one.
3. Finally, add 1.

You only convert the negative number in this case. Don't convert the positive number as well.

In order to do this on our diagram above, we simply add a NOT gate to every B input. This leaves us with one small problem though; our circuit is now only going to be a subtractor. In order to fix this we can use a XOR gate instead. This means our input will only be inverted if out control switch is on. See the XOR truth table below:

B | Control | Out
--|---|----
0 | 0 | 0
1 | 0 | 1
0 | 1 | 1
1 | 1 | 0

This can then be represented in the diagram below:

![](/content/assets/minecraft%20adder%20subtractor/diagrams/adder%20subtractor.png "Ignore the circle at the end of the XOR gates. These are meant to be XOR, not XNOR.")

This now unfortunately increases the size of our adder-subtractor in Minecraft as the XOR gate is the largest of all the gates.

Now we have connected an XOR gate to all our B inputs, the adder subtractor is now complete.

![](/content/assets/minecraft%20adder%20subtractor/screenshots/full%20adder%20subtractor%20ingame.png "The control line is on the bottom of this screenshot")

# The final thing

Only being able to add 3 bits together isn't that great, I think most people are capable of adding numbers smaller than 8 together. In order to make it actually useful I added 5 more adders to bring the total number of bits to 8, meaning numbers up-to 255 ($2^8-1$) can now be represented.

////

/content/assets/minecraft%20adder%20subtractor/screenshots/finished%20front%20side.png The interface for the adder subtractor.

/content/assets/minecraft%20adder%20subtractor/screenshots/finished%20top.png The buses connecting the interface to the actual logic.

/content/assets/minecraft%20adder%20subtractor/screenshots/finished%20left%20side.png One of the sides, showing the two layers of adders. The bottom layer being 0-4, top 5-7.

////

# Conclusion

This was a nice little mini project to put something I'd learnt into practice. I still have no idea how people build functional computers in this game, or even ["Minecraft inside Minecraft"](https://youtu.be/-BP7DhHTU-I). If I was to come back to this I'd at least need to learn some more WorldEdit.