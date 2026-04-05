document.addEventListener("DOMContentLoaded", () => {
    const hero = document.querySelector(".hero-image img");
    if (hero) {
        setTimeout(() => {
            hero.style.transform = "translateY(0)";
            hero.style.opacity = "1";
        }, 200);
    }
});