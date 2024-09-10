Title: A parody of a friend
Summary: Just because it's there doesn't mean it's real
Authour: Oscar Peace
Tags: AI
      Arduino
      Go
Published: 31/8/2024

This post is about my recreation of the [friend.com](https://friend.com) AI necklace. It is divided into two main parts and a conclusion: the how I made it part, and the why I made it part and finally the conclusion If you only want to read one part, feel free to skip ahead.

# Why I made it

A while ago now, more specifically on the 30th July I saw a tweet about what seemed to be another weird AI product. I scrolled past it at the time, disregarding it as part of another part of the never ending AI hype tsunami. I then kept seeing it, this time with the addition of comments taking the piss. Now I had to take a look. What I found was something so unbelievable that it couldn't even be rivalled by the greatest satire writers of our time. It was a bluetooth microphone that had to be tethered to a phone at all times in order to work, plumbing data through digital pipes, to produce a 5 word response via ChatGPT to something you said. All while removing any organic human experience from the world and contributing to global warming. Absolutely amazing.

I had to make one.

> "we are doomed" - ThePrimeagen

When I eventually came around to deciding how to implement this project, I saw [this](https://x.com/tsarnick/status/1824203664120221811) tweet. At the time when I originally saw it and even now when re-watching it for writing this post I cringed heavily. To describe a large language model called "Emily" as "god-like" I believe you have to be on some other sideways plane of existence where everyone thinks computers are sentient and where the moon also happens to be made out of cheese. To give some credit to it's creator I believe he is one of the only people in the world to have such deeply entrenched tunnel vision when it comes to artificial intelligence.

Below this tweet there was a link to the full interview. As much as I didn't want to I now had to watch this as well. In the interview the creator of "friend", Avi Schiffmann, says that he doesn't think anything will ever replace human contact. Why did you make this then? He also goes on to say that one of his biggest inspirations as a founder is the creator of Uber, Travis Kalinick, who presided over the company whilst there was ["permitted culture of sexual harassment"](https://www.nytimes.com/2019/12/18/technology/uber-settles-eeoc-investigation-workplace-culture.html) and numerous reports of drivers working for the company sexually assaulting their passengers [as well](https://www.bbc.co.uk/news/business-62158976). Starting to see why any possible ethical problems may have been blindsided now.

He also reveals the fact that the AI is using a model provided by Meta which is trained using messages from it's *Messenger* platform, saying that any complaints about the ethics of it should be forwarded to Meta,  not him; even though he was the one who had the choice over which model to use. When questioned about the possibility of bringing loved ones back to life, he also references the *Black Mirror* episode [*Be Right Back*](https://en.wikipedia.org/wiki/Be_Right_Back) in which somebody is brought back to life as an android bot after dying in a car accident; seemingly without any reflection at all. Although, bringing someone you know back from the dead wouldn't be too much of a step from having something that replaces all the people you know already.

This of course brings me onto the natural ethical problems of having an artificially intelligent pseudo-friend. The main issue obviously being forming a connection with something that doesn't have any real sense of conscience, being, or awareness of it's human "companion" and believer. Anyone who was read the classic science fiction novel [*Do Androids Dream of Electric Sheep?*](https://en.wikipedia.org/wiki/Do_Androids_Dream_of_Electric_Sheep) or watched it's film adaptation *Blade Runner* will know about the distraught brought onto it's protagonist by his attraction to one of the robots he is supposed to kill. I know that isn't the best example but it should at least serve as a warning for what *could* happen.

That brings me to the end of my arguments against this product, which frankly should have never gotten past a drawing board or even onto a piece of paper in the first place. I mean seriously how difficult is it to hire somebody experienced in artificial intelligence and computer ethics? Oh wait, computer ethics isn't really a thing that exists in the world of over-hyped startups yet. All we seem to have for computer ethics for the vast majority of people who aren't researchers (especially tech-bros) is an [IBM slide](https://medium.com/@oneboredarchitect/ai-in-management-a-2023-perspective-on-a-1979-ibm-slide-ef368036fc1a) from 45 years ago saying:

> A COMPUTER CAN NEVER BE HELD ACCOUNTABLE
> 
> THEREFORE A COMPUTER MUST NEVER MAKE A MANAGEMENT DECISION

That being said, there are *lots* of papers on ethics and artificial intelligence. However, what's the point of screaming if nobody can hear you? And even if you write something critical you'll get [fired](https://www.theguardian.com/technology/2021/feb/26/google-timnit-gebru-margaret-mitchell-ai-research) from your company anyway.

We really are doomed if this thing takes off aren't we?

# How I made it

Because the existing product I was trying to parody was already a parody of itself in my opinion, I couldn't just recreate it with a pair of in ear headphones with a microphone that you can get for £1.99 from AliExpress, (or even better 17p if I were to get 10,000 of them in bulk from Alibaba) and an a basic Android app that would realistically take about one day to program. It would have to be better in someway. I settled on the following requirements:

- The output would have to be shown on device. The phone app just gives you a notification, I mean seriously how difficult is it to put a tiny speaker in necklace?
- No companion app would be required. Obviously it would still need a backend to talk to, as far as I know you can't run LLMs & speech recognition on microcontrollers yet.
- The cost would have to be less than the thing I was parodying. $99 dollars is quite an easy target to hit with a Cloudflare free tier and AliExpress at your disposal.

## Making the backend

I decided to use Cloudflare Workers for the backend of the project, mostly because they provided a way to use AI models for testing purposes (you wouldn't be able to use the free tier in production without going over the limit very quickly). I had also used them before albeit it via the workers SvelteKit adapter and hadn't any actually used any workers specific features (their key value storage KV, their database platform D1 etc.) before. TLDR; I hadn't actually made a proper barebones app before that used Workers

I considered using SvelteKit (just the server side routing functionality) again, however I settled upon using one of the templates available, more specifically the [itty-router](https://github.com/kwhitley/itty-router) template which is easy enough to use without reading *too* much of the documentation. It seemed easier to access the Workers APIs this way as well.

### The WAV file format

Once I had figured out how to setup a route, it was time to figure out how to create a WAV file. Fortunately this was rather easy, at least once I found something semi-comprehensive detailing the WAV file format. [This](http://www.topherlee.com/software/pcm-tut-wavformat.html) website turned out to be particularly useful. The WAV file format is then as follows:

Position | Value | Description
---------|-------|------------
0-3 | "RIFF" | The magic number to indicate a RIFF file
4-7 | File size | 32 bit signed integer to mark the size of the overall file minus the size of the remaining data to be read.
8-11 | "WAVE" | Actually marks this file as a WAV file
12-16 | "fmt " | The start of the format chunk, detailing information about the format of the audio data. Remember to include the space at the end, this gave me a massive headache.
16-19 | 16 |Length of the format data so far, always 16 bytes.
20-21 | Audio format | 1 is PCM
22-23 | Number of channels | In my case this was 1, I wasn't dealing with any stereo audio.
24-27 | Sample rate | In my case this was 4KHz, which produced a telephone call like sound.
28-31 | Byte rate | I'm not really sure why this field exists, since it can be calculated from the other values present. Here's how to calculate it anyway: `(sampleRate * bitsPerSample * channels) / 8`
32-33 | Block align | `(bitsperSample * channels) / 8`
34-35 | Bits per sample | For me this was 8 bits, as the Pico has a 12 bit analogue to digital converter (ADC), and recording 16 bit on a microcontroller is a no go. Also 12 bit audio isn't really a thing for various reasons, mainly the fact that it would take up the same space as 16 bit audio in memory.
36-39 | "data" | Data chunk header
40-43 | File size | File size of the PCM data - the size of the header so far. `(pcmData.length - header.length)`

**Note:** All characters are 1 byte long and ASCII encoded.

If you want to see an implementation of this in JavaScript go [here](https://github.com/sccreeper/fiend/blob/540d9ce50f7090d701d5c86943ca9eba76d54fc1/backend/src/lib/changeToWav.js). If not, that's understandable it's JavaScript, a language where direct access to actual bytes is unheard of and you have to do use special array to do it and not just a normal one. Thank you ECMA.

### The actual backend

Now that I had PCM to WAV conversion and a router setup it was time to establish what routes I would need. After 30 seconds I decided upon 3 routes:

- `/api/speechRecognition` - Route to upload PCM data and get a text response back of what you said.
- `/api/askQuestion` - Receives a text query and responds with whatever the LLM generated in response.
- `/api/changeToWav` - Literally just turns PCM data into a WAV file. Was initially made for testing purposes but I decided to keep it anyway.

The idea behind doing the WAV conversion on the server was that, even though it wasn't exactly CPU or memory intensive, I wanted to run a minimal amount of code on the Pico, even if it resulted in some weird design patterns. I also wanted to avoid duplication of code between the desktop client, which was mainly intended for debugging and the Pico client.

The Workers AI API was easy enough to interface with from each route, however I did have to do what felt like a bodge in order to expose it unless I only wanted it available in the `index.js` file. Luckily you can pass context to routes in itty so this is what I ended up doing.

Here's a brief implementation demonstrating interaction with the AI API:

```js

// This snippet is modified from backend/src/routes/askQuestion.js

const systemPrompt = "Some system prompt"

let messages = [
      {
            role: "system",
            content: systemPrompt
      },
      {
            role: "user",
            content: "Whatever you want to say."
      }
]

const llmResponse = await ctx.env.AI.run(
      "@cf/meta/llama-2-7b-chat-fp16",
      {messages}
)

```

- The `ctx` variable is passed in by the router.
- The `AI.run()` function takes two parameters: what model you want to use, and any data required by that model.

For testing the backend I just used the local development server, and didn't bother doing anything like adding API key support. Only because you should never attempt to recreate this.

Now I had a working (in theory) backend I had to make something to test it with.

## The desktop client

In order to make sure everything was working properly before I started making the client for the Pico, I decided to make a quick app in Golang to test with.

The exact details of it are too boring to write here but here's a brief overview anyway:

- There were two ways of using it, either a CLI or a UI.
- I used the `portaudio` library to record the audio.
- I used `fyne` and the Charm CLI library to make the UI and CLI respectively.

If you're a semi-experienced developer I'm pretty sure I don't need to go into details of how to send a HTTP request to a server and parse JSON, but if you're unsure then here's a [link](https://github.com/sccreeper/fiend/tree/540d9ce50f7090d701d5c86943ca9eba76d54fc1/clientDesktop) to the source for the desktop client.

After I finished the desktop client, I went on holiday for a week, so this project took a little hiatus. Here's a picture of some countryside to illustrate that:

![](/content/assets/fiend%20prototype/holiday%20countryside.jpg "Picture of countryside. Sorry it's in portrait, for some reason most of my photos from that holiday are.")

## Pico client

Now I had figured everything out using languages and platforms I was largely familiar with it was time to start over with something I wasn't that familiar with. I had used microcontrollers (more specifically Arduino) before for some quick weekend hobby projects, however I had never used them for something as complicated (in theory) as this.

For programming the Pico, I could either use MicroPython (automatic no, far too slow), the C SDK, or the Arduino Pico core. I decided to use the Arduino core because as previously mentioned I had used it before and I would also have access to the vast array of libraries for the Arduino ecosystem.

In order to actually be able to access the Arduino's serial output, which would be required for debugging, I had to add myself to the `uucp` group, thank you to the ArchLinux [documentation](https://wiki.archlinux.org/title/Working_with_the_serial_console) for telling me how do do that. 

```shell
sudo usermod -aG uucp oscar
```

### The first circuit

When I plugged everything in, there was no ["magic smoke"](https://en.wikipedia.org/wiki/Magic_smoke), and the blinking LED worked fine. This was a good sign. Then I tried pressing the button to see if it was working. This was my first problem (little did I know, of many).

The button was supposed to act as a push to talk button, however when I pressed it, it instantly acted as if I'd released it, even though I hadn't. After checking my code and realising that nothing was wrong with it, I then double checked my wiring. Turns out the ground rail on the breadboard hadn't actually been connected to anything this entire time.

Now I moved onto trying to record audio using this abridged code below:

```c++

// 1/4000
#define SAMPLE_DELAY 250

// Gets set to true/false when button if button is pressed.
bool recording;

// BUFFER_SIZE in this case is equivalent to:
// (sampleRate*bitDepth*maxLengthInSeconds)/8
uint8_t audioData[BUFFER_SIZE];

void setup() {
      // 12 bits by default, however just here as well to reinforce it in my mind.
      analogReadResolution(12); 
}


void loop() {

      if (recording) {

            if(bufferIndex >= BUFFER_SIZE) {
                  recording = false;
            } else {
                  int sample = analogRead(MIC_PIN);
                  audioData[bufferIndex] = (uint8_t) map(sample, 0, 4095, 0, 255);
                  bufferIndex++;
                  delayMicroseconds(SAMPLE_DELAY);
            }

      }

}

```

When finished this code would dump the contents of the `audioData` buffer to the serial output.

I tested the code, expecting to see a load of noise/random data in the serial output, however I did not. What I saw instead was exactly the same value, ±1 over and over again.

After several hours of debugging thinking my code was the problem (and achieving varying results), it turned out that this was actually a hardware issue instead. See, the microphone I had found, believing it had an amplifier on board didn't have any amplifier on it at all. The chip I believed was doing amplification was actually a comparator. A comparator is a chip that compares two electrical signals and outputs high if one of them is higher than the other. Not an amplifier. Instead of getting a signal that should have been a measurable number of volts, I was instead getting a millivolt signal.

In my search for solution, I looked on AliExpress I came across a module that had an amplifier built in, the [MAX4466](https://www.aliexpress.com/item/1005004019287254.html). I bought it and then waited seven days as it made it's way from China to me.

### The second circuit

Now I had an in theory working microphone, it was time to see if it worked or out. When I monitored the serial output this time around, I saw actual data. This was a good sign.

I needed to see if it was producing anything that actually resembled audio. To do this I used these commands:

```sh
# Sets the baud rate of the Serial.
stty -F /dev/ttyACM0 115200 raw

# Dump the serial output into a bin file.
cat /dev/ttyACM0 > out.bin

# Convert our raw pcm data into a wav file
ffmpeg -f u8 -ar 4000 -ac 1 -i out.bin -acodec pcm_u8 out.wav
```

When I listened to the wav file, I could hear what I was saying however the sound was still far too noisy to be usable. I was getting lots of sharp clicks in the audio at regular intervals. To further illustrate my point, here's what the waveform looked like:

![](/content/assets/fiend%20prototype/noisy%20waveform%20sc.png "Screenshot of a a noisy audio waveform with lots of negative peaks")

Following a bit of research, I learned about something called a low pass filter circuit, which is used to remove noise. I added this to the breadboard, and the noise was virtually eliminated. I used a 1k resistor with 10nF capacitor.

Audio coming out of the microphone was still quiet, however I could actually understand what I was saying and this meant it was usable.

The final schematic I came up was as follows (This was my first time using KiCad):

![](/content/assets/fiend%20prototype/fiendPrototypeCropped.png "Final circuit schematic for Fiend prototype")

If you want a PDF version, one is available [here](/content/assets/fiend%20prototype/fiendPrototype.pdf).

![](/content/assets/fiend%20prototype/breadboard.jpg "The final breadboard layout. I didn't have enough male to male jumpers.")

### Uploading the audio to the backend

Uploading the audio to the development server was easy enough, I just had to add the `--ip 0.0.0.0` switch to the `npx wrangler dev` command in order to expose the server to the local network instead of just my machine.

For processing the response I could either:

- Make my own length prefixed encoding.
- Just use JSON.

The Pico is a rather fast microcontroller so as long as I kept the JSON responses small, I would be able to parse them relatively quickly. I also had around 128kb of memory left at this point, which was plenty to parse JSON. With this in mind I decided to go with JSON, using the [`ArduinoJSON`](https://arduinojson.org/) library.

Decoding the JSON response was rather easy, however when I displayed what I got back on the display I was met with a sea of garbled characters instead of a nicely printed string. 

![](/content/assets/fiend%20prototype/screen%20garbled%20characters.jpg "Picture of OLED display showing garbled characters (seemingly random splatters of pixels)")

I originally believed this was a an issue with writing a multiline string to the display, and it all printing on one line (ignoring linebreaks) however when I wrote a method to print a multiline string and the problem still didn't go away, it must had be something else.

The only other thing that could still be affecting it was unsupported characters being written to the display. With this in mind I did some sanitizing of the output string on the server using the list of ASCII characters available in [this file](https://github.com/lexus2k/lcdgfx/blob/master/src/canvas/fonts/fonts.c).

Unfortunately this still didn't all fit on the screen, so I had to simply limit the length of the responses using my system prompt with some extra code.

### Cleaning everything up

Now everything was working I added some niceties to tie everything together:

- LED effects for statuses. This used the second core of the Pico for so requests could take place on the first one in order to avoid blocking.
- Green boxes around the names and using a smaller font to make sure everything fitted on the screen.
- Increased my system prompt to something far too long:   
```js
const systemPrompt = `You are fiend, and are supposed to act as somebody's friend but not really. You are a parody of another AI project called "friend". You should provide short responses, at most 1-2 sentences in length and under 64 characters. Do not use any emojis, and stray away from using excessive punctuation.`
```

////

/content/assets/fiend%20prototype/final/dumb.jpg "Dumb" prompt, with green boxes around speaker names

/content/assets/fiend%20prototype/final/hello.jpg "Hello" prompt

////

# Conclusion

To conclude I think this has been a good project, however I don't ever want to make anything like this to do with large language models again, unless it's only to parody some other ill-thought-out project. Also in my opinion it ended up being slightly better for something made in about a week (if I didn't have to wait for parts and go on holiday etc.) and only for a price of £12.67 ($16.64 USD) compared to the $99 USD retail price of the same thing.

If you really want to make one (you shouldn't) the bill of materials and repository are below in the appendix. You could probably change it run locally using [ollama](https://github.com/ollama/ollama), which is something I might try, although with a much smaller model.

# Appendix

Appendices, miscellaneous information.

## Bill of materials

**Note:** Any links are not necessarily 100% the exact same as what is used in the prototype, just the closest I could find.

Item | Amount | Cost | Link
-----|------|--------|------
Momentary pushbutton | 1 | £0.08 | [AliExpress](https://www.aliexpress.com/item/1005005315348507.html)
LED | 1 | £0.01 | [AliExpress](https://www.aliexpress.com/item/1005004515135362.html)
SSD1331 display | 1 | £3.50 | [AliExpress](https://www.aliexpress.com/item/1005005985458267.html)
MAX4466 microphone module | 1 | £0.97 | [AliExpress](https://www.aliexpress.com/item/1005004019287254.html)
Pico W | 1 | £6.80 | [Pimoroni](https://shop.pimoroni.com/products/raspberry-pi-pico-w?variant=40059369652307)
Jumper wires | 14 | £0.26 (1.875p per) | [AliExpress](https://www.aliexpress.com/item/1005005501503609.html)
1K resistor | 1 | 0.6p | [AliExpress](https://www.aliexpress.com/item/1005007010335100.html)
10k resistor | 1 | \|\| | \|\|
100 resistor | 1 | \|\| | \|\|
10nF ceramic capacitor | 1 | 0.7p | [AliExpress](https://www.aliexpress.com/item/1005005691634051.html)
Breadboard | 1 | £1.03 | [AliExpress](https://www.aliexpress.com/item/1005006236313056.html)

**Total:** £12.67

## Links

- [GitHub repo](https://github.com/sccreeper/fiend/)
- [friend.com](https://www.friend.com/)
- [Fortune magazine interview](https://youtu.be/xCzY3MvJlZY?si=eJVso78wEldqt4nj)


