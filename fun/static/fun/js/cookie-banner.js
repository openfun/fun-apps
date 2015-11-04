var cookieName = 'acceptCookieFun';
var cookieValue = "on";
var cookieDuration = 365;
var cookieBannerHtml = "<h2>france-universite-numerique-mooc.fr utilise des cookies de mesure d'audience dans le but d\'am&eacute;liorer le service.</h2>" +
    "En naviguant sur notre site vous acceptez l\'installation et l\'utilisation des cookies sur votre ordinateur." +
    "<a href=\"#\">&gt; En savoir plus</a>" +
    "<a href=\"#\" class=\"cookie-banner-button\">J'accepte</a>";

function checkCookie(name) {
    var nameEQ = name + "=";
    var ca = document.cookie.split(';');
    for (var i=0;i < ca.length;i++) {
        var c = ca[i];
        while (c.charAt(0)==' ') {
            c = c.substring(1,c.length);
        }
        if (c.indexOf(nameEQ) === 0) {
            return c.substring(nameEQ.length,c.length);
        }
    }
    return null;
}

function removeDiv(event) {
    event.preventDefault();
    var element = document.getElementById('cookie-banner');
    element.parentNode.removeChild(element);
    var date = new Date();
    // Cookie expires after six months
    date.setTime(date.getTime() + (window.cookieDuration*180*24*60*60*1000));
    var expires = "; expires=" + date.toGMTString();
    document.cookie = window.cookieName + "=" + window.cookieValue + expires + "; path=/";
}

function addCookieBanner() {
    var divbanner = document.getElementById("cookie-banner");
    divbanner.style.display = "table";
}

function animateBanner(event) {
    var elem = document.getElementById("cookie-banner");
    var bottom = -80;

    function frame() {
      bottom++;  
      elem.style.bottom = bottom + 'px'; 
    
      if (bottom >= 0)  {
        clearInterval(id);
      }
    }
    var id = setInterval(frame, 4);
}

function manageCookieBanner(event) {
    if(checkCookie(window.cookieName) != window.cookieValue) {
        addCookieBanner();
        document.getElementsByClassName('cookie-banner-button')[0].addEventListener("click", removeDiv);
        animateBanner();
    }
}

window.addEventListener("load", manageCookieBanner);

