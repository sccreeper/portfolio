Title: EarthMC dashboard in SvelteKit
Summary: My experience integrating a 3rd party API with SvelteKit
Authour: Oscar Peace
Tags: Svelte
      SvelteKit
      Minecraft
Published: 1/1/1970

![](/content/assets/earthmc/final_product.png "The final product")

# Why?

Why not? Of course there is more too it than that however in this instance the main reason is that it is nice to be able to retrieve information about the server without actually being on it.


Now there are applications that do this already using the API, for example there is a [discord bot](https://emctoolkit.vercel.app/). Also the API doesn't return some useful information, mainly player skins and avatars.

However I,

1. Don't want to be alt-tabbing into Discord whenever I want to get more information than the server provides (I usually have a web browser open on my second monitor)
2. All I need to access it is a web browser I don't have to open Discord.
3. **I also want to learn the basics of SvelteKit**.

# EarthMC API

The EarthMC API in a nutshell is a REST-ful API that returns information about the server. Unfortunately there is no extensive documentation on the API apart from [the endpoints](https://earthmc.net/docs/api).

For this project I used the version 3 endpoints which aren't on the wiki yet. They are the same as v2 however the shape of the JSON objects is different.

For generating types that I could use easily in my code, I used a JSON to JSDoc converter because I wasn't dealing with having `[object Object]` and `undefined` turning up everywhere.

This made it pretty easy to implement views for towns, residents and players once I had developed a few basic general use components to build with though.

![](/content/assets/earthmc/nation_view.png "View for a nation")

# Things I like & dislike

Svelte itself is already a great framework (intuitive, easy to use, fast etc.), so SvelteKit's feature set works very well on top of it.

The file based routing system is nice, however the abundance of `+page.svelte`, `+page.server.js` etc. files can cause a migraine after a while especially if you're tired and forget which file you're working on (if you use a tree view in your editor this gets very confusing). 

It takes a bit of getting used too if you're used to just pure single page app based Svelte or that could just be me (I'm currently working on migrating my [music streaming app](https://github.com/sccreeper/chime) from Svelte to SvelteKit). However, the documentation is good and any problems I had could be solved with it and a bit of googling most of the time.

This isn't really a problem with Svelte or SvelteKit as such, but the userbase is still quite small compared to something like React or NextJS (just compare the weekly downloads on npm), so when looking for solutions to problems online there is a much more limited pool of answers to choose from. I think this is just an early adopters tax more than anything else though.

The developer tooling and hot reload (thank you Vite) is a very nice thing to have as well. Being able to run `npm run dev` and watch my app update in the browser as I keep adjusting styles or JS code is definitely something I am going to take for granted from now on.

SvelteKit has several [stores](https://svelte.dev/docs/svelte-store) (if you are unfamiliar with Svelte these are essentially variables which can be updated from anywhere and show the changes anywhere). Unfortunately as far I know there is no way to have a store synced on the client and server, as cool as that would be. However on the client-side SvelteKit provides several stores which can be useful for determining the state of certain aspects of your application.

One such (and very basic) example is the `$navigating` store. It is a boolean which is set to true whenever your app is changing routes (i.e. navigating). This is helpful for adding nice little features like a loading bar:

```svelte

<!-- Obviously a real example would have styles etc. -->

{#if $navigating}

<div>
loading...
</div>

{/if}


```

A full list of stores is available [here](https://kit.svelte.dev/docs/modules#$app-stores).

# Svelte + HTMX?

Having used HTMX a bit as well I kept asking myself, "Would this be easier to implement in HTMX?", whilst I was developing the app.

Deep down what I think I really want, as nice as SvelteKit is, is something that mixes [HTMX](https://htmx.org/) and Svelte together as opposed to Svelte and SSR. Svelte as a template language and HTMX to manage state and requests on the client? Yes please.

Maybe I would keep the file system based routing as well. If I didn't want to use Svelte I could experiment with using [_hyperscript](https://github.com/bigskysoftware/_hyperscript) a scripting language developed by the HTMX people instead. 

# Deployment

Deployment was very easy as SvelteKit offers multiple adapters which essentially build your code to run on different platforms/runtimes.

I chose the [Cloudflare pages](https://kit.svelte.dev/docs/adapter-cloudflare) adapter as that was what I would be hosting on.

Cloudflare also a has GitHub actions hook as well meaning that whenever I pushed to my repo it would build (provided I had no errors etc.) and deploy automatically onto Cloudflare.

# Conclusion

In conclusion this was a very nice development experience and in the future I would definitely consider using SvelteKit again (as previously mentioned I'm already using it to redevelop my music streaming server).

If you want to look at the dashboard it is located [here](https://emc.oscarcp.net/).