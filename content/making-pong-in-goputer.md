Title: Making pong with my fantasy VM
Summary: Finally, a real project
Authour: Oscar Peace
Tags: Goputer
      Projects
      Go
Published: 28/10/2025

*Note: This is a continuation from my [previous post](/blog/goputer-profiler). This post can also serve as a more in-depth explanation of one of the goputer examples as well as a tutorial of sorts.*

For as long as goputer has existed, I have never made what I would call a complete program or project with it. Any code that has been written for it has been short examples, intended to test functionality rather than showcase what is possible. With this in mind I decided to embark on creating *Pong*. While I could have possibly gone for something a bit more advanced, such as *Snake* or *Tetris*, *Pong* was the simplest thing I could make whilst still testing the full feature set of goputer.

This post is split into four parts with a conclusion:

- Drawing
- Moving
- Scoring
- Debugging

Even though this post describes the function of each piece of code, I would still recommend skimming over the [syntax](https://github.com/sccreeper/goputer/wiki/Syntax) page in the documentation beforehand.

# Drawing

This was the easiest part. I often describe goputer as "an assembly language that controls Microsoft Paint", and it's not far from the truth. A huge part of the feature-set of goputer is drawing stuff to the screen. After all, what's the point of an educational tool if you can't draw things.

A pong screen is very simple to draw, it contains two paddles, a ball, and a dividing line. I'll get onto the score later.

Firstly the initial positions need to be defined so they can be changed later if necessary, also it's very poor practice to not use constants where possible.


```text
#def paddle_offset 5
#def paddle_width 5
#def paddle_height 25
#def paddle_speed 10

#def left_paddle_pos 120
#def right_paddle_pos 120

#def ball_x 160
#def ball_y 120
```

The first set of definitions define constants that are referenced in later code. The second set define the positions of the paddles and the ball respectively. The reason why everything is multiples of five is because it makes bounds checking ever so slightly easier, i.e. I shouldn't have to worry about [integer underflow](https://en.wikipedia.org/wiki/Arithmetic_underflow).

These needed to be used in conjunction with a routine that draws the shapes in question onto the screen:

```text
...

lda @left_paddle_pos
mov d0 vy0
add vy0 $d:paddle_height
mov a0 vy1

mov $320-d:paddle_offset-d:paddle_width vx0
mov $320-d:paddle_offset vx1

int va

...
```

A quick note on the immediate values prefixed with `$`:

- Expressions are evaluated from left-to-right, and don't follow normal operator precedence.
- `d:xyz` refers to the value of a definition at compile time.

Drawing the ball and the centre line followed a [similar routine](https://github.com/sccreeper/goputer/blob/d604504813b27805801260a1b21bc31588053b03/examples/pong.gpasm#L142-L157).

# Moving

A static image is pretty useless if you're trying to make a game, therefore the next thing I focused on was trying to make things move. 

## Moving the paddles

Firstly, I focused on moving the paddles, as I figured this would be the easiest thing to do because the code should be the same for both of them. The steps that were required were as follows:

1. Interrupt to register the keypress
2. Then decide which key it is, and thus which paddle to move
3. Move the respective paddle

Registering an interrupt listener is simple, however you can only register one per interrupt.

```text
#label keyup

// Do something

iret

#intsub kd keyup
```

This means the `keyup` label will be called whenever someone presses a key. After an interrupt is called the next step is to preserve any registers we are going to write to.

```text
push r01
push dp
push dl
push a0
sta @d0_store
```

The function of the last line is slightly different because it stores the entire value in `d0` on the static stack (populated and allocated at compile time) as opposed to the dynamic stack (populated and allocated at runtime). The `sta` instruction differentiates between addressing the static stack with immediate values and main memory with registers by checking if the argument is [greater than the number of registers](https://github.com/sccreeper/goputer/blob/d604504813b27805801260a1b21bc31588053b03/pkg/vm/load_store.go#L40). If so the first 4 bytes at that address show how many bytes to store.

After this there are a series of cascading equality checks to determine which key was pressed:

```text
...

neq kc $23
cndjmp @m_lp_down
lda @left_paddle_pos
mov d0 r01
eq r01 $0
cndjmp @move_end
sub r01 $d:paddle_speed
mov a0 d0
sta @left_paddle_pos
jmp @move_end

...
```

The above code does the following:

1. Is the `kc` (current key) register equal to any other value than 23. If so, jump to the next equality check, if not keep going.
2. Load the paddle position and see if it is equal to zero. If it is, jump to the cleanup label because we can't move any further.
3. Then subtract the paddle speed, because in this case we are moving up the screen.
4. Store the paddle position for later use and jump to the cleanup routine.

## Moving the ball

The ball is slightly different given the fact it moves in two dimensions, not one and needs to move every frame/update as opposed to whenever a user presses a specific key. I'm not showing the code that loads values into registers as you've already seen an example of that but in order to help with understanding the values in each register are as follows:

- `r00` is the ball's X position.
- `r01` is the Y position.
- `r02` is the X direction.
- `r03` is the Y direction.

```text
...

// Bounds right
neq r00 $320-d:ball_size
cndjmp @bbc_left
mov $0 r02
push $0
call @increase_score
jmp @check_paddles
// Bounds left
#label bbc_left
neq r00 $0
cndjmp @check_paddles
mov $1 r02
push $1
call @increase_score

...
```

You may notice the call to `increase_score` but I'll get back to that [later](#scoring). The bounds checking code for the right is the same. However, checking the top and bottom is different because the ball has to bounce, not resetting back to the centre of the screen.

"Bouncing" the ball for both the paddles and the top and bottom of the screen is simple. If the Y current direction value is 1, say when hitting the bottom of the screen, we make it zero and then the ball will go up when the move code is called. This same bouncing logic applies when hitting a paddle, yet this time the X direction is changed.

See the code for checking the right paddle:

```text
...

eq r00 $320-d:ball_size-d:paddle_width-d:paddle_offset
mov a0 r15
gt r01 r05
mov a0 r14
add r05 $d:paddle_height
lt r01 a0
mov a0 r13
and r15 r14
and a0 r13
inv a0
cndjmp @check_left_paddle
mov $0 r02
jmp @bbc_bottom

...
```

The process of the routine is as follows:

1. Check if the X position of ball such that it is in-line with the left hand side of the paddle.
2. Then see if the paddle Y is in-between the top and bottom of the paddle.
3. If both of these conditions are true (successive `and` operations), then we invert the ball direction and jump to the bottom bounds check.

# Scoring

Now all the movement logic was in place I needed a way to score the game. As mentioned earlier, the [`increase_score` routine](https://github.com/sccreeper/goputer/blob/d604504813b27805801260a1b21bc31588053b03/examples/pong.gpasm#L355) is called whenever the ball hits the left or right side. Before it is called, one value is pushed to the stack - which player's score to increase.

```text
...

lda @player_one_score
mov d0 r14
add r14 $1
mov a0 d0
sta @player_one_score
jmp @reset_ball

...
```

Above: Increasing the score for the left player/player one.

Even though the score was increasing, you still couldn't see what it's value was, at least without inspecting registers/memory locations. I still needed to write the assembly to display it.

## Integers to strings

In any other language you'd simply make use of a standard library function to convert an integer to a string, in Golang you'd use `strconv.Itoa(x)` or Python would make use of the even simpler `str(x)`. Unfortunately, working in an assembly language means you don't have access to such luxuries so you have to make these things yourself.

The loop that is used to convert a number into an integer is below:

```text
...

eq r01 $0
cndjmp @draw_zero

#label convert_number
mod r01 $10
add a0 $48
mov $1 dl
mov a0 vt
sr vt $1
div r01 $10
mov a0 r01

neq r01 $0
cndjmp @convert_number

sl vt $1
int vt

...
```

First we check if the number is already zero, as this is a special case. After than we keep taking the remainder of the number divided by ten, then writing the corresponding character to `vt` (the text buffer) - we also shift the text buffer right at this stage. We store the result of the division of the number for use in the next iteration of the loop. This repeats until the result of the division is zero.

We also have to shift the text buffer left by one byte to cleanup from the last iteration.

# Debugging

In all honestly there weren't actually that many bugs with the assembly I wrote, at least not any major ones that took ages to figure out. That being said, there were some problems with the runtime that I didn't know about or should have known about:

- The data stack didn't work properly, which meant the ball always teleported to the top of the screen when a key was pressed.
- The possibility of a race condition if a key was pressed in the middle of a ball update.

The stack not working properly was easy enough to fix, the race condition however required the addition of two new instructions and the exposure of the previously internal interrupt flag through a new control register. The two new instructions were inspired by x86's `sti` and `cli` (set and clear interrupt bit) instructions, albeit with different names.

```text
pri

mov r00 d0
sta @ball_x

mov r01 d0
sta @ball_y

mov r02 d0
sta @ball_direction_x

mov r03 d0
sta @ball_direction_y

eni
```

In this case, `pri` prevents interrupts, and `eni` re-enables them. The instructions in-between write the updated ball location data to memory.

# Conclusion

![](/content/assets/goputer/pong.png "The pong program running in the web frontend")

The next steps are probably to write a better *Pong* clone rather than the quite simple one I've got now, and also finding a way to speed up the VM - which will almost certainly require writing some of the rendering instructions in assembly. The other major improvement I have made since the last post has been to rewrite the expansion system around Lua instead of Go's `plugin` library, meaning that it is now cross platform.

Other than making the VM faster a proper IDE or even a VSCode extension would be nice.

If you want to see any other posts linked to Goputer, click [here](/posts?tags=goputer) or the repository is [here](https://github.com/sccreeper/goputer). The full source code for the *Pong* example talked about in this blog post is on GitHub [here](https://github.com/sccreeper/goputer/blob/d604504813b27805801260a1b21bc31588053b03/examples/pong.gpasm).