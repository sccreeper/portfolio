const turnstileTargetId = "turnstile"

let turnstileCount = 0;

function turnstileInit() {
  let turnstileTarget = document.getElementById(turnstileTargetId);

  console.log("Running turnstile init")

  if (turnstileTarget) {

    console.log("TS target exists");

    turnstile.ready(function () {
        turnstileCount++;

        if (turnstileCount <= 1) {
          turnstile.render(`#${turnstileTargetId}`, {
            sitekey: window.cfSiteKey,
            "response-field-name": 'turnstile',
        }); 
        }
    });

  }
}

turnstileInit();
document.addEventListener("htmx:afterSwap", turnstileInit);
