const tg = window.Telegram.WebApp;

document.addEventListener("DOMContentLoaded", () => {

    tg.expand();
    tg.BackButton.show();

    tg.BackButton.onClick(() => {
        tg.expand();
        setTimeout(() => window.history.back(), 0);
    });

    const user = tg.initDataUnsafe?.user || {};
    const card = document.getElementById("usercard");
    const greeting = document.createElement("h2");
    const userName = user.first_name || user.username || "пользователь";

    greeting.innerText = `👋 Приветствую, ${userName}!`;
    greeting.style.textAlign = "center";
    greeting.style.marginBottom = "30px";
    card.appendChild(greeting);
});
