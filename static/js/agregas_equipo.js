document.addEventListener("DOMContentLoaded", function () {
  const contextos = window.contextosData || {};
  const ramaSelect = document.getElementById("rama");
  const clubSelect = document.getElementById("club");

  const clubOpcionesOriginales = clubSelect.innerHTML;

  ramaSelect.addEventListener("change", function () {
    const ramaElegida = this.value;

    clubSelect.innerHTML = clubOpcionesOriginales;
    clubSelect.removeAttribute("readonly");
    clubSelect.removeAttribute("disabled");

    let clubCongelado = null;
    for (const key in contextos) {
      const ctx = contextos[key];
      if (ctx.rama === ramaElegida) {
        clubCongelado = ctx.club;
        break;
      }
    }

    if (clubCongelado) {
      clubSelect.innerHTML = `<option value="${clubCongelado}" selected>${clubCongelado}</option>`;
      clubSelect.setAttribute("readonly", "readonly");
      clubSelect.setAttribute("disabled", "disabled");
    }
  });
});
