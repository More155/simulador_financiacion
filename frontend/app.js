let clienteActualCuit = null;
        const API_URL = "http://localhost:8000";

        // Funciones para controlar el Modal
        function mostrarModalError(mensaje) {
            document.getElementById("modalMensajeError").innerText = mensaje;
            document.getElementById("modalError").classList.remove("hidden");
        }

        function cerrarModalError() {
            document.getElementById("modalError").classList.add("hidden");
        }

        // Cargar marcas al iniciar la página
        window.addEventListener("DOMContentLoaded", async () => {
            try {
                let res = await fetch(`${API_URL}/api/marcas`);
                let marcas = await res.json();
                let select = document.getElementById("selectMarca");
                marcas.forEach(m => {
                    let opt = document.createElement("option");
                    opt.value = m;
                    opt.textContent = m;
                    select.appendChild(opt);
                });
            } catch (err) {
                console.error("Error al cargar marcas:", err);
            }
        });

        async function cargarBancos() {
            let marca = document.getElementById("selectMarca").value;
            let bancoSelect = document.getElementById("selectBanco");
            bancoSelect.innerHTML = '<option value="">Seleccione banco...</option>';
            document.getElementById("selectLinea").innerHTML = '<option value="">Seleccione línea...</option>';
            document.getElementById("selectPlazo").innerHTML = '<option value="">Seleccione plazo...</option>';

            if (!marca) return;

            let res = await fetch(`${API_URL}/api/bancos/${encodeURIComponent(marca)}`);
            let bancos = await res.json();
            bancos.forEach(b => {
                let opt = document.createElement("option");
                opt.value = b;
                opt.textContent = b;
                bancoSelect.appendChild(opt);
            });
        }

        async function cargarLineas() {
            let marca = document.getElementById("selectMarca").value;
            let banco = document.getElementById("selectBanco").value;
            let lineaSelect = document.getElementById("selectLinea");
            lineaSelect.innerHTML = '<option value="">Seleccione línea...</option>';
            document.getElementById("selectPlazo").innerHTML = '<option value="">Seleccione plazo...</option>';

            if (!marca || !banco) return;

            let res = await fetch(`${API_URL}/api/lineas?marca=${encodeURIComponent(marca)}&banco=${encodeURIComponent(banco)}`);
            let lineas = await res.json();
            lineas.forEach(l => {
                let opt = document.createElement("option");
                opt.value = l;
                opt.textContent = l;
                lineaSelect.appendChild(opt);
            });
        }

        async function cargarPlazos() {
            let marca = document.getElementById("selectMarca").value;
            let banco = document.getElementById("selectBanco").value;
            let linea = document.getElementById("selectLinea").value;
            let plazoSelect = document.getElementById("selectPlazo");
            plazoSelect.innerHTML = '<option value="">Seleccione plazo...</option>';

            if (!marca || !banco || !linea) return;

            let res = await fetch(`${API_URL}/api/plazos?marca=${encodeURIComponent(marca)}&banco=${encodeURIComponent(banco)}&nombre_tasa=${encodeURIComponent(linea)}`);
            let plazos = await res.json();
            plazos.forEach(p => {
                let opt = document.createElement("option");
                opt.value = p;
                opt.textContent = `${p} Meses`;
                plazoSelect.appendChild(opt);
            });
        }

       async function buscarCliente() {
    let cuitInput = document.getElementById("inputCuit").value.trim();
    const resultadoDiv = document.getElementById("resultadoCliente");
    const seccionSimulador = document.getElementById("seccionSimulador");
    const avisoSimulador = document.getElementById("estadoSimuladorAviso");

    if (!cuitInput) {
        mostrarModalError("Por favor ingrese un CUIT o CUIL válido para realizar la búsqueda.");
        return;
    }

    try {
        let res = await fetch(`${API_URL}/api/cliente/${cuitInput}`);
        if (!res.ok) {
            mostrarModalError("Cliente no encontrado en la base de datos de la Central de Deudores.");
            resultadoDiv.classList.add("hidden");
            seccionSimulador.classList.add("opacity-60", "pointer-events-none");
            return;
        }

        let cliente = await res.json();
        clienteActualCuit = cliente.cuit_cuil;

        document.getElementById("resNombre").innerText = cliente.nombre_apellido;
        document.getElementById("resCuit").innerText = cliente.cuit_cuil;
        document.getElementById("resAntiguedad").innerText = cliente.antiguedad_laboral_meses;
        document.getElementById("resScore").innerText = cliente.score_nosis;
        document.getElementById("resCuotaMax").innerText = "$" + (cliente.cuota_maxima_afectable ?? 0).toLocaleString("es-AR");
        document.getElementById("resIngresos").innerText = "$" + (cliente.ingreso_mensual_neto ?? 0).toLocaleString("es-AR");
        
        let compromisosVal = cliente.compromisos_mensuales ?? 0;
        document.getElementById("resCompromisos").innerText = "$" + compromisosVal.toLocaleString("es-AR");

        const badgeBcra = document.getElementById("badgeBcra");
        let sitBcra = cliente.situacion_bcras ?? cliente.situacion_bcra ?? 1;
        
        if (sitBcra >= 3) {
            badgeBcra.className = "px-2.5 py-1 rounded-full text-xs font-bold bg-rose-100 text-rose-800";
            badgeBcra.innerText = `Situación ${sitBcra} (Riesgo Alto)`;
        } else if (sitBcra == 2) {
            badgeBcra.className = "px-2.5 py-1 rounded-full text-xs font-bold bg-amber-100 text-amber-800";
            badgeBcra.innerText = `Situación 2 (Seguimiento)`;
        } else {
            badgeBcra.className = "px-2.5 py-1 rounded-full text-xs font-bold bg-emerald-100 text-emerald-800";
            badgeBcra.innerText = `Situación ${sitBcra} (Normal)`;
        }

        resultadoDiv.classList.remove("hidden");
        seccionSimulador.classList.remove("opacity-60", "pointer-events-none");
        avisoSimulador.className = "text-xs bg-indigo-100 text-indigo-800 px-3 py-1 rounded-full font-medium";
        avisoSimulador.innerHTML = `<i class="fa-solid fa-circle-check mr-1"></i> Cliente cargado - Listo`;

    } catch (err) {
        console.error(err);
        mostrarModalError("Error al conectar con la API de FastAPI.");
    }
}
        async function realizarSimulacion() {
            if (!clienteActualCuit) return;

            const datos = {
                cuit: clienteActualCuit,
                precio_vehiculo: parseFloat(document.getElementById("inputPrecio").value) || 0,
                anticipo: parseFloat(document.getElementById("inputAnticipo").value) || 0,
                marca: document.getElementById("selectMarca").value,
                banco: document.getElementById("selectBanco").value,
                nombre_tasa: document.getElementById("selectLinea").value,
                plazo: parseInt(document.getElementById("selectPlazo").value) || 0
            };

            // Validación rápida de selectores vacíos en el frontend
            if (!datos.marca || !datos.banco || !datos.nombre_tasa || !datos.plazo) {
                mostrarModalError("Debe completar todos los selectores de la línea de crédito (Marca, Banco, Tasa y Plazo) antes de simular.");
                return;
            }

            try {
                let res = await fetch(`${API_URL}/api/simular`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(datos)
                });

                if (!res.ok) {
                    let err = await res.json();
                    // LANZA EL MODAL CON EL MENSAJE EXACTO QUE DEVUELVE PYTHON (Ej: "El anticipo debe ser menor...")
                    mostrarModalError(err.detail || "Ocurrió un error en los parámetros de la simulación.");
                    return;
                }

                let resultado = await res.json();

                // Si todo sale bien, muestra los resultados financieros abajo
                document.getElementById("resultadoSimulacion").classList.remove("hidden");
                document.getElementById("resMontoFinanciar").innerText = "$" + resultado.monto_a_financiar.toLocaleString("es-AR");
                document.getElementById("resCuotaMensual").innerText = "$" + resultado.cuota_mensual.toLocaleString("es-AR");
                document.getElementById("resQuebranto").innerText = "$" + resultado.quebranto_pesos.toLocaleString("es-AR");
                document.getElementById("resMontoMax").innerText = "$" + resultado.monto_maximo_permitido.toLocaleString("es-AR");
                document.getElementById("resRelacionIngreso").innerText = `Cuota/Ingreso: ${resultado.relacion_cuota_ingreso_pct}%`;

                const contenedorAptitud = document.getElementById("contenedorAptitud");
                const iconoApto = document.getElementById("iconoApto");
                const tituloApto = document.getElementById("tituloApto");
                const listaMotivos = document.getElementById("listaMotivos");
                listaMotivos.innerHTML = "";

                if (resultado.apto) {
                    contenedorAptitud.className = "p-4 rounded-xl border bg-emerald-50 border-emerald-200 text-emerald-900";
                    iconoApto.className = "fa-solid fa-circle-check text-emerald-600 text-lg";
                    tituloApto.innerText = "Operación Apta y Viable";
                    let li = document.createElement("li");
                    li.innerText = "Cumple con todos los parámetros crediticios y capacidad de pago.";
                    listaMotivos.appendChild(li);
                } else {
                    contenedorAptitud.className = "p-4 rounded-xl border bg-rose-50 border-rose-200 text-rose-900";
                    iconoApto.className = "fa-solid fa-circle-xmark text-rose-600 text-lg";
                    tituloApto.innerText = "Operación Rechazada";
                    resultado.motivos_rechazo.forEach(motivo => {
                        let li = document.createElement("li");
                        li.innerText = motivo;
                        listaMotivos.appendChild(li);
                    });
                }

            } catch (err) {
                console.error(err);
                mostrarModalError("Error crítico de conexión al intentar comunicarse con el servidor.");
            }
        }