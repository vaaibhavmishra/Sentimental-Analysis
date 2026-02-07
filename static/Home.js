document.addEventListener("DOMContentLoaded", () => {
    const main = document.querySelector("main");
    setTimeout(() => {
        main.style.animation = "fadeIn 2s ease-in forwards";
    }, 2000); // 2-second delay
});
