// menu.js или добавить в существующий JS-файл

document.addEventListener("DOMContentLoaded", () => {
    const tg = window.Telegram?.WebApp;

    // Функция для безопасного получения user_id
    function getTelegramUserId() {
        if (!tg) {
            console.error("Telegram WebApp is not available");
            return null;
        }
        const user = tg.initDataUnsafe?.user || {};
        const user_id = user?.id;
        if (!user_id) {
            console.error("User ID not found in Telegram WebApp initData");
            return null;
        }
        return user_id;
    }

    // Настройка динамической ссылки на /formation-groups
    const formationGroupsLink = document.getElementById('formation-groups-menu-link');
    if (formationGroupsLink) {
        const user_id = getTelegramUserId();

        if (user_id) {
            // Устанавливаем правильный href с user_id
            formationGroupsLink.href = `/formation-groups?user_id=${user_id}`;
            // Убираем обработчик onclick, если он был добавлен ранее как заглушка
            formationGroupsLink.onclick = null;
        } else {
            // Если user_id не найден, делаем ссылку неактивной
            formationGroupsLink.href = 'javascript:void(0)';
            formationGroupsLink.onclick = function(e) {
                e.preventDefault();
                alert("Ошибка идентификации. Пожалуйста, откройте приложение из Telegram.");
                console.warn("Formation groups link disabled due to missing user_id");
            };
            formationGroupsLink.classList.add('disabled'); // Опционально
        }
    }
});