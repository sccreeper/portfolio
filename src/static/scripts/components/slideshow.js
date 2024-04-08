import { clamp } from "../util.js";

class Slide {
    /**
     * Slide class
     * @param {string} caption 
     * @param {string} src 
     */
    constructor(caption, src) {
        this.caption = caption;
        this.src = src;
    }
}

// Preloading function for slideshow.
// This is assumes that the slideshow is relatively short and we aren't sending 15+ images to the client.
function preloadImage(url) {

    let img = new Image();
    img.src = url;

}

class SlideshowElement extends HTMLElement {

    /**
     * @type {Slide[]}
     */
    slides;

    /**
     * @type {string}
     */
    currentSrc;

    constructor() {
        super();
    }

    nextSlide() {
        if (this.currentSlide+1 >= this.slides.length) {
            this.currentSlide = 0
        } else {
            this.currentSlide++
        }
    }

    get currentSlide() {
        return parseInt(this.getAttribute("currentslide"))
    }

    set currentSlide(val) {

        val = clamp(val, 0, this.slides.length-1)

        this.setAttribute("currentslide", val.toString())

        this.shadowRoot.querySelector("img").src = this.slides[this.currentSlide].src
        this.shadowRoot.querySelector("figcaption").innerText = this.slides[this.currentSlide].caption

        this._generateNumbers()

    }

    _generateNumbers() {

        const numbers = [];

        for (let i = 0; i < this.slides.length; i++) {
            
            if (i == this.currentSlide) {
                
                let current = document.createElement("b")
                current.innerText = (i+1).toString();

                numbers.push(current)

            } else {

                let normal = document.createElement("span")
                normal.innerText = (i+1).toString()
                normal.addEventListener("click", (e) => {
                    this.currentSlide = i;
                })

                numbers.push(normal)

            }
            
        }

        this.shadowRoot.getElementById("number-container").innerHTML = "";
        this.shadowRoot.getElementById("number-container").append(...numbers);

    }

    connectedCallback() {

        const shadow = this.attachShadow({mode: "open"});

        let slideElements = this.getElementsByTagName("slide")

        this.slides = [];

        for (let index = 0; index < slideElements.length; index++) {
            const element = slideElements[index];
            this.slides.push(new Slide(element.getAttribute("caption"), element.getAttribute("src")))

            preloadImage(this.slides[index].src);
        }

        const styles = document.createElement("link")
        styles.setAttribute("rel", "stylesheet")
        styles.href = "/static/slideshow-dist.css"
        

        const img = document.createElement("img")
        img.src = this.slides[0].src
        img.addEventListener("click", (e) => {
            this.nextSlide()
        })

        console.log(this.slides)

        const caption = document.createElement("figcaption")
        caption.innerText = this.slides[0].caption

        shadow.appendChild(styles)
        shadow.appendChild(img)
        shadow.appendChild(caption)

        // Add numbers to indicate current slide.

        const numberContainer = document.createElement("div")
        numberContainer.setAttribute("id", "number-container")
        shadow.appendChild(numberContainer)

        this.currentSrc = this.slides[0].src
        this.currentSlide = 0

    }

}

customElements.define("slide-show", SlideshowElement)