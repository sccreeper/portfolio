const turnstileTargetId = "turnstile"

function turnstileInit() {
  let turnstileTarget = document.getElementById(turnstileTargetId);

  console.log("Running turnstile init")

  if (turnstileTarget) {

    console.log("TS target exists");

    turnstile.ready(function () {

        turnstile.render(`#${turnstileTargetId}`, {
          sitekey: window.cfSiteKey,
          "response-field-name": 'turnstile',
      }); 

    });

  }
}

turnstileInit();
document.addEventListener("htmx:afterSwap", turnstileInit);
