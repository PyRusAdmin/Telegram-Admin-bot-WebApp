const tg = window.Telegram.WebApp;

document.addEventListener("DOMContentLoaded", () => {

    tg.expand();
    tg.BackButton.show();

    tg.BackButton.onClick(() => {
        tg.expand();
        setTimeout(() => window.history.back(), 0);
    });

    const user = tg.initDataUnsafe?.user || {};
    const user_id = user.id;

    // Если нужно использовать user_id глобально, сделайте его глобальным
    window.TELEGRAM_USER_ID = user_id;
});
