import globals from "./globals";

// Constants

const b_day = new Date("September 29, 2005 00:00:00");
const favicon_light = new URL("../assets/favicon_light.png", import.meta.url);
const favicon_dark = new URL("../assets/favicon_dark.png", import.meta.url);

// Logic Functions

function DoSlideshow(index) {

    // Increment index

    if (globals.slide_shows[index].index+1 > globals.slide_shows[index].max) {
        globals.slide_shows[index].index = 0
    } else {
        globals.slide_shows[index].index++;
    }

    //Set src

    var el = document.getElementById(globals.slide_shows[index].id);

    document.getElementById(globals.slide_shows[index].img_id).src = el.children[globals.slide_shows[index].index].getAttribute("srcset");

    setTimeout(DoSlideshow, 3000, index)
}

function MediaQueryChangeTheme(q) {
    if (q.matches) {
        document.getElementsByTagName("html")[0].classList.add("dark");
        document.getElementById("favicon").setAttribute("href", favicon_dark);
    } else {
        document.getElementsByTagName("html")[0].classList.remove("dark");
        document.getElementById("favicon").setAttribute("href", favicon_light);
    }
}

// Init code

//Set age

let age_el = document.getElementById("age");
let diff = Math.abs(new Date() - b_day);
let time = Math.floor(diff / 1000 / (3600 * 24 * 365));
age_el.innerHTML = time;

// Scrape from steam

// TODO move to workers

// let workshop_items = document.getElementsByClassName("sub-count");

// for (let i = 0; i < workshop_items.length; i++) {
    
//     fetch(workshop_items[i].getAttribute("data-url"), {mode: "no-cors", method: "GET"})
//     .then((response) => response.headers)
//     .then((data) => {

//         console.log(data)

//         let workshop_page = (new window.DOMParser()).parseFromString(data, "text/html");
//         workshop_items[i].innerHTML = workshop_page.getElementsByClassName("stats_table")[0].children[0].children[1].children[0].innerHTML;

//     })

// };

// Slideshow

let slide_show_els = document.getElementsByClassName("slide-show");

for (let i = 0; i < slide_show_els.length; i++) {

    globals.slide_shows.push({
        index: 0,
        max: slide_show_els[i].children.length-1, //-1, account for indexing at zero
        id: slide_show_els[i].id,
        img_id: slide_show_els[i].getAttribute("data-img-id"),
    });
    
    DoSlideshow(i);

}

// Theming

var theme = window.matchMedia("(prefers-color-scheme: dark)");
MediaQueryChangeTheme(theme)
theme.addListener(MediaQueryChangeTheme)

document.getElementById("theme-span").addEventListener("click", (e) => {

    if (document.getElementsByTagName("html")[0].classList.contains("dark")) {
        document.getElementsByTagName("html")[0].classList.remove("dark");
        document.getElementById("theme-span").textContent = "Theme: Light"
    } else {
        document.getElementsByTagName("html")[0].classList.add("dark");
        document.getElementById("theme-span").textContent = "Theme: Dark"
    }

})