Title: Programming on Windows
Summary: The most half way experience you'll ever have
Authour: Oscar Peace
Tags: Other
      Development
Published: 4/10/2024

Recently I got a new laptop. This laptop came with Windows 11. Having been an avid Linux user for the past couple of years (Arch BTW) this is something I would typically try to avoid. However, because I am currently starting my first year of university as I write this, I wanted to ensure that I would be able to use any software they may need.

Fast forward to the end of my induction week, and there isn't any weird obscure software that needs to be installed (yet, and if I really need to I can use the university computers); but it feels like I'm in for the long haul now so I might as well try and commit to it, as painful as that may be.

# WSL?

Windows Subsystem for Linux (WSL), has been around for a while now, and to be honest it would probably fulfill most of my needs. However, I also wanted to ensure that my programs actually ran on Windows as well, so I decided to start this by redoing certain parts of [goputer](https://github.com/sccreeper/goputer). I'll get onto that later in the post though. WSL does have support for running graphical applications under X11 as well, which is quite handy just in case I can't get anything working at all (foreshadowing).

# Installing stuff

There's no need to explain this really, but Windows has no built in or universally used package manager. Technically there is [WinGet](https://github.com/microsoft/winget-cli) which is developed by Microsoft, however this doesn't come pre-installed with Windows so I'm not counting it. Because of this I decided to use [Chocolatey](https://community.chocolatey.org/) instead, mostly because I had heard of it before; probably a bad decision now with hindsight but it works so I don't care enough to change it.

Once you have installed Chocolatey, installing packages is the same as any other package manager. You just run `choco install packageName` and then it installs it. The most annoying part is having to open another shell session whenever you install a new package because of the path changing. Like why.

Having installed most of the required packages, I realised that in order to get my goputer project working at all; I will have to rewrite large parts of it. Call this a "skill-issue" if you like, but I was not willing to invest large amounts of time to get something working under Windows when it worked perfectly fine on Linux. This would be a part I would end up rewriting anyway (specifically the extension and frontend system), only because it was a bad initial design decision.

More information of the architecture of goputer as it was when I wrote this can be found [here](https://github.com/sccreeper/goputer/wiki/Frontends/84468e9f9421d897474efe0ff4b1c8b043aabffb).

# Porting stuff 

The only thing I had to port now in order to get my project sort of running on Windows was rewriting the [magefile](https://magefile.org/), a build system that allows you to write build scripts in Golang. When I first wrote it I had used a bunch of shell commands instead of built in language functionality, which was a mistake because now it didn't work on Windows at all. After rewriting the build file, the project did actually build which was good; however I was still faced with the hurdle of redoing large parts of my project. 

After I had modified the build file, it was now time to consider redoing significant parts of my project. Considering I had already spent a large amount of time trying to get it to build in the first place; I gave up and decided to develop under WSL instead.

# The move to Fedora

When I first tried running the magefile under WSL with Ubuntu, something weird happened. The file had worked perfectly on Windows, however when I ran it under Ubuntu I got an error about a built-in function, `os.CopyFS()` (built-in way of recursively copying directories), not existing. It turned out that this method had only just been added in the most recent version of Golang, but Ubuntu was on a month of version of Golang. Because of this I moved to Fedora, which after using [this](https://www.linuxfordevices.com/tutorials/linux/install-fedora-on-windows) post to get a WSL version of Fedora working finally ran as it was supposed to.

![](/content/assets/developing%20on%20windows/goputer%20running.png "Goputer running under WSL. I'm not quite sure how to get rid of the default X11 window style yet.")

# Docker

After I had goputer running it was time to try and get my blog engine running.

This blog runs inside a Docker container, which meant I would have to get one running on Windows. Luckily Docker supports integration with WSL containers. All I had to do was download the Docker for Windows desktop app, then install it and finally [enable](https://learn.microsoft.com/en-us/windows/wsl/tutorials/wsl-containers) WSL integration. Then once I had everything running I noticed something out of the corner of my eye, Docker was using 2.5gb of memory, doing nothing. This was mostly the "VmmemWSL" process which is waht the containers where running under, but it still didn't make any sense. When running natively on Linux the overhead is much less and it tends to use the memory of the container plus a little overhead. This wasn't the same.

After reading through [this](https://github.com/microsoft/WSL/issues/4166) GitHub issue, I came across two possible solutions which could've worked:

1. I could [configure](https://learn.microsoft.com/en-us/windows/wsl/wsl-config#configure-global-options-with-wslconfig) memory limits for each WSL2 system using a `wsl.conf` file. ([credit](https://github.com/microsoft/WSL/issues/4166#issuecomment-2289616278))
2. Or I could use the Docker engine directly inside of the containers instead of through the VM. ([credit](https://github.com/microsoft/WSL/issues/4166#issuecomment-2273040075))

After a bit more digging I found Fedora WSL was using ~700mb of memory just on it's own, however this was mostly just the VSCode server I was using to develop on it. Because the excessive memory usage (sometimes upto ~5GB) was only happening when Docker itself was actually running, my laptop only had 16GB of RAM with no ability to add more without buying an entire 32GB of SODIMM modules, and running the Docker engine under WSL just seemed weird I decided to use the configuration files to just try to limit memory.

After adding these changes to the globally applied `.wslconfig` file,

```toml

[wsl2]

memory=4GB
swap=6GB

[experimental]

# Instantly frees cached memory.

autoMemoryReclaim="dropcache"

```

, the memory usage improved significantly.

# Conclusion

Once you manage to find your way under or over it's many hurdles, you can actually start to develop software on Windows. Would I do this again unless I had to? No. Did I at least find it to be a semi-fufilling experience. Not really. If anything it makes you wonder why Microsoft didn't just make WSL but the other way round (Wine essentially) and turn Windows into a Linux distro; only problem being that they wouldn't be able to make any money.