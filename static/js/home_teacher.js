// Archivo JS para profesor

// Instancias de dia y semana
const day = document.getElementById("day");
const week = document.getElementById("week");
const dayList = document.getElementById("day-info")
const weekList = document.getElementById("week-info")

// Evento tras pulsar el boton "Dia"
day.addEventListener("click", () => {
    if (dayList.classList.contains("hidden")) {
        dayList.classList.remove("hidden");
    }
    weekList.classList.add("hidden")
})

// Evento tras pulsar el boton "Semana"
week.addEventListener("click", () => {
    if (weekList.classList.contains("hidden")) {
        weekList.classList.remove("hidden");
    }
    dayList.classList.add("hidden")
})