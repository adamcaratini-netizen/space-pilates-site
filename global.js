   (function () {
        // Set tenant name here
        var TENANT_NAME = 'space.sandbox';

        var d = document;
        var sA = ['polyfills', 'js'];

        for (var i = 0; i < sA.length; i++) {
            var s = d.createElement('script');
            s.src = 'https://' + TENANT_NAME + '.marianaiframes.com/' + sA[i];
            s.setAttribute('data-timestamp', +new Date());
            (d.head || d.body).appendChild(s);
        }
    })();


//  Pages password protection  
const protectedPages = [
  "/account",
  "/register",
  "/buy-now",
  "/book-now"
];

const PASSWORD = "ipstudio";

(function () {
  const path = window.location.pathname.toLowerCase();

  const isProtected = protectedPages.some(page => path.includes(page));

  if (!isProtected) return;

  const unlocked = sessionStorage.getItem("site_unlocked");

  if (unlocked === "true") return;

  const entered = prompt("This page is protected.\n\nEnter the password:");

  if (entered === PASSWORD) {
    sessionStorage.setItem("site_unlocked", "true");
    return;
  }

  alert("Incorrect password.");

  window.location.href = "/";
})();