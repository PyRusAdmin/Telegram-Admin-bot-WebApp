document.addEventListener("DOMContentLoaded", function() {
    const burgerMenuIcon = document.getElementById("burgerMenuIcon");
    const burgerMenu = document.getElementById("burgerMenu");

    if (burgerMenuIcon && burgerMenu) {
        burgerMenuIcon.addEventListener("click", () => {
            burgerMenu.classList.toggle("open");
        });

        // Закрытие при клике на ссылку
        burgerMenu.querySelectorAll("a").forEach((link) => {
            link.addEventListener("click", () => {
                burgerMenu.classList.remove("open");
            });
        });
    }
});