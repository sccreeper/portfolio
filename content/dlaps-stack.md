Title: DLAPS stack
Summary: How I deploy most of my projects
Authour: Oscar Peace
Tags: Other
      Development
      Stacks
Published: 27/06/2025

Most of my "online" projects (including this blog) use what I call the DLAPS stack which can be summarised as the following:

- **D**ocker
- **L**inux
- **A**pache
- **P**rogram
- **S**QLite

Alternatively if deploying straight onto bare metal the SLAPS stack also works and rolls off the tongue much better. However, because most deployments don't use that it'll have to be DLAPS. Essentially it is a variation of the classic [LAMP stack](https://en.wikipedia.org/w/index.php?title=LAMP_(software_bundle)&oldid=1295099813) but using SQLite instead of MySQL and Docker as a virtualisation layer.

Why Docker? Because it runs anywhere and you can run anything in it. Not to sound too much like their marketing copy but it's true. Also great for avoiding testing in prod.

Linux technically occurs in two places in this stack. That is, whatever bare metal machine Docker and Apache are running on and in whatever Docker container(s) are running. The most honest reason for using it is quite frankly why would you ever use anything else on a server (at least definitely not Windows), also the widest adoption, most support etc.

Any reverse proxy could fulfill the role of Apache (nginx, Caddy, etc.), however I have the most experience with Apache so it'll have to stay that way. Like I said earlier this was based on the LAMP stack so I have to be somewhat faithful to the original when coming up with a formal *de jure* version of it.

As for the program part this could really be anything. It doesn't have to communicate with the internet as such, thus the Apache part would then be redundant. The reason for choosing program over Python or Perl etc. is because I also write Go - [goputer](https://github.com/sccreeper/goputer) and [Chime](https://github.com/sccreeper/chime). While only the latter is internet based I do want to write some more Go based web stuff in the future (probably using [templ](https://github.com/a-h/templ)), or even any other language.

Finally, SQLite. Probably the best database out there. If anything I was doing needed maybe a slightly larger feature-set I would probably switch to PostgresSQL seeming as that's what I've been taught to use at university. SQLite is lightweight, easy to deploy, and could probably run on a little Arduino (a [library](https://github.com/siara-cc/esp32_arduino_sqlite3_lib) exists for running it on an ESP32, which is a slightly beefier micro-controller) with some minor changes. TLDR; it runs literally everywhere and is good for the vast majority of use cases.

To conclude in a world of "serverless" this and that it's nice to have something that's deployable on a real machine, because lets face it that Cloudflare free tier (which admittedly I use myself for my [EarthMC dashboard](https://emc.oscarcp.net/)) isn't going to last once your app starts getting traction and you need actual performance, not that that'll ever happen anyway so you might as well stick to a tiny VPS and call it a day.