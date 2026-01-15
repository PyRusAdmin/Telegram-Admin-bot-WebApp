//кнопка назад
const tg = window.Telegram.WebApp;
tg.BackButton.show();
tg.BackButton.onClick(() => {
    tg.expand(); // Убедимся, что expand() сработает
    setTimeout(() => {
        window.history.back();
    }, 0);
});
