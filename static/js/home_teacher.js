const dayBtn = document.getElementById("day");
const weekBtn = document.getElementById("week");
const dayList = document.getElementById("day-info");
const weekList = document.getElementById("week-info");

// Grupos de clases definidos en un array
const activeClasses = ["bg-white", "text-rose-700", "shadow-sm"];
const inactiveClasses = ["bg-transparent", "text-gray-500"];

// Funcion auxiliar para actualizar estilos
function updateStyles(active, inactive) {
    active.classList.remove(...inactiveClasses);
    active.classList.add(...activeClasses);

    inactive.classList.remove(...activeClasses);
    inactive.classList.add(...inactiveClasses);
}

dayBtn.addEventListener("click", () => {
    updateStyles(dayBtn, weekBtn);
    
    dayList.classList.remove("hidden");
    weekList.classList.add("hidden");
});

weekBtn.addEventListener("click", () => {
    updateStyles(weekBtn, dayBtn);
    
    weekList.classList.remove("hidden");
    dayList.classList.add("hidden");
});