// Funciones para manejar citas
document.addEventListener('DOMContentLoaded', function() {
    // Agregar event listeners a todos los botones de ver detalles
    document.querySelectorAll('.btn-ver-detalles').forEach(function(btn) {
        btn.addEventListener('click', function() {
            verDetallesCita(this.dataset.citaId);
        });
    });

    // Agregar event listeners a todos los botones de actualizar estado
    document.querySelectorAll('.btn-actualizar-estado').forEach(function(btn) {
        btn.addEventListener('click', function() {
            actualizarEstadoCita(this.dataset.citaId, this.dataset.estado);
        });
    });

    // Agregar event listeners a todos los botones de cancelar cita
    document.querySelectorAll('.btn-cancelar-cita').forEach(function(btn) {
        btn.addEventListener('click', function() {
            cancelarCita(this.dataset.citaId);
        });
    });
});

function verDetallesCita(citaId) {
    // Aquí iría la lógica para cargar los detalles de la cita
    fetch(`/api/citas/${citaId}/`)
        .then(response => response.json())
        .then(data => {
            const modal = document.getElementById('detallesCitaModal');
            const content = document.getElementById('detallesCitaContent');
            content.innerHTML = generarContenidoModalCita(data);
            new bootstrap.Modal(modal).show();
        })
        .catch(error => console.error('Error:', error));
}

function actualizarEstadoCita(citaId, nuevoEstado) {
    if (confirm('¿Está seguro de que desea actualizar el estado de la cita?')) {
        fetch(`/api/citas/${citaId}/actualizar-estado/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify({ estado: nuevoEstado })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                window.location.reload();
            } else {
                alert('Error al actualizar el estado de la cita');
            }
        })
        .catch(error => console.error('Error:', error));
    }
}

function cancelarCita(citaId) {
    if (confirm('¿Está seguro de que desea cancelar esta cita?')) {
        fetch(`/api/citas/${citaId}/cancelar/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                window.location.reload();
            } else {
                alert('Error al cancelar la cita');
            }
        })
        .catch(error => console.error('Error:', error));
    }
}

function generarContenidoModalCita(cita) {
    return `
        <div class="modal-body">
            <p><strong>Fecha:</strong> ${cita.fecha}</p>
            <p><strong>Hora:</strong> ${cita.hora}</p>
            <p><strong>Doctor:</strong> ${cita.doctor_nombre}</p>
            <p><strong>Paciente:</strong> ${cita.paciente_nombre}</p>
            <p><strong>Motivo:</strong> ${cita.motivo}</p>
            <p><strong>Estado:</strong> ${cita.estado}</p>
        </div>
    `;
}

// Función auxiliar para obtener el token CSRF
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
} 