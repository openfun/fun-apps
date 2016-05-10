(function() {
    var cookieName = 'acceptCookieFun';
    var cookieValue = "on";
    var cookieDuration = 365;

    function removeDiv(event) {
        event.preventDefault();
        var element = document.getElementById('cookie-banner');
        element.parentNode.removeChild(element);
        var date = new Date();
        // Cookie expires after six months
        date.setTime(date.getTime() + (cookieDuration*180*24*60*60*1000));
        var expires = "; expires=" + date.toGMTString();
        document.cookie = cookieName + "=" + cookieValue + expires + "; path=/";
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
        if(checkCookie(cookieName) != cookieValue) {
            addCookieBanner();
            document.getElementsByClassName('cookie-banner-button')[0].addEventListener("click", removeDiv);
            animateBanner();
        }
    }

    window.addEventListener("load", manageCookieBanner);
})();
