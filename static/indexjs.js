var video = document.getElementById("myVideo");
var btn = document.getElementById("myBtn");

function myFunction() {
    if (video.paused) {
        video.play();
        btn.innerHTML = "Pause";
    } else {
        video.pause();
        btn.innerHTML = "Play";
    }
}

// function myFunction2() {
//     var x = document.getElementById("myNavbar");
//     if (x.className === "navbar") {
//         x.className += " responsive";
//     } else {
//         x.className = "navbar";
//     }
// }