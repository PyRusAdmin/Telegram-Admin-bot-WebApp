// admin.js

// Общая функция для заполнения select
function populateSelect(url, selectId) {
    fetch(url)
        .then((response) => response.json())
        .then((data) => {
            const select = document.getElementById(selectId);
            select.innerHTML = '<option value="">-- Выберите группу --</option>';

            // Проверяем, есть ли нужный ключ
            const groups = data.chat_title || data.groups || [];

            groups.forEach((group) => {
                const option = document.createElement("option");
                option.value = group.chat_title;
                option.textContent = group.chat_title;
                select.appendChild(option);
            });
        })
        .catch((err) => console.error(`Ошибка загрузки ${selectId}:`, err));
}

// При загрузке страницы
window.onload = () => {
    // Получаем user_id из глобальной переменной, переданной в шаблоне
    const userId = CURRENT_USER_ID;

    populateSelect(`/chat_title?user_id=${userId}`, "group-select"); // Выбор группы, для получения количества участников
    populateSelect("/chat_title", "groups-select");
    populateSelect("/chat_title", "groups-selected");
    populateSelect("/chat_title", "groups-selecteds");
    populateSelect("/chat_title", "groups-select-privilage");
};

// Получение количества участников групп / каналов
async function getParticipants() {

    const chat_title = document.getElementById("group-select").value.trim();
    if (!chat_title) {
        alert("Выберите группу из списка");
        return;
    }

    try {
        const response = await fetch(
            `/update-participants?chat_title=${encodeURIComponent(chat_title)}`
        );
        const data = await response.json();
        const statusEl = document.getElementById("participants-count");

        if (data.success) {
            statusEl.innerText = `Участников: ${data.participants_count}`;
            statusEl.className = "status success";
        } else {
            throw new Error("Ошибка получения данных");
        }
    } catch (error) {
        document.getElementById("participants-count").innerText =
            "Не удалось получить количество участников";
        document.getElementById("participants-count").className = "status error";
    }
}




