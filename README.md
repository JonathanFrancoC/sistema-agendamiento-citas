# Sistema de Agendamiento de Citas Médicas

Este es un sistema web desarrollado con Django para la gestión y agendamiento de citas médicas. Permite a los pacientes agendar citas con doctores según su especialidad, y a los doctores gestionar sus horarios y citas.

## 🚀 Características

- **Registro y Autenticación de Usuarios**
  - Registro diferenciado para pacientes y doctores
  - Validación de documentos para doctores
  - Sistema de autenticación seguro

- **Panel de Administración**
  - Gestión de usuarios
  - Verificación de doctores
  - Monitoreo de citas

- **Funcionalidades para Pacientes**
  - Búsqueda de doctores por especialidad
  - Agendamiento de citas
  - Visualización de historial de citas
  - Cancelación de citas

- **Funcionalidades para Doctores**
  - Gestión de horarios disponibles
  - Visualización de citas programadas
  - Gestión de perfil profesional
  - Carga de documentos (licencia y certificaciones)

## 🛠️ Tecnologías Utilizadas

- Python 3.x
- Django 5.2
- SQLite (Base de datos)
- HTML/CSS/JavaScript
- Bootstrap 5

## 📋 Requisitos Previos

- Python 3.x instalado
- pip (gestor de paquetes de Python)
- Entorno virtual (recomendado)

## 🔧 Instalación

1. Clona el repositorio:
```bash
git clone https://github.com/JonathanFrancoC/tarea-profe-mike.git
cd tarea-profe-mike
```

2. Crea y activa un entorno virtual:
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

3. Instala las dependencias:
```bash
pip install -r requirements.txt
```

4. Realiza las migraciones:
```bash
python manage.py migrate
```

5. Crea un superusuario (opcional):
```bash
python manage.py createsuperuser
```

6. Inicia el servidor:
```bash
python manage.py runserver
```

## 🚀 Uso

1. Accede a la aplicación en `http://localhost:8000`
2. Regístrate como paciente o doctor
3. Inicia sesión con tus credenciales

### Para Pacientes
- Busca doctores por especialidad
- Agenda citas en horarios disponibles
- Visualiza y gestiona tus citas

### Para Doctores
- Configura tu perfil y horarios
- Gestiona tus citas programadas
- Sube documentos necesarios

### Para Administradores
- Accede al panel de administración en `http://localhost:8000/admin`
- Gestiona usuarios y permisos
- Verifica documentos de doctores

## 📁 Estructura del Proyecto

```
tarea-profe-mike/
├── agendamiento/          # Aplicación principal
│   ├── migrations/        # Migraciones de la base de datos
│   ├── templates/        # Plantillas HTML
│   ├── static/          # Archivos estáticos
│   ├── forms.py         # Formularios
│   ├── models.py        # Modelos de datos
│   ├── urls.py          # URLs de la aplicación
│   └── views.py         # Vistas
├── citas_web/           # Configuración del proyecto
│   ├── settings.py      # Configuraciones
│   ├── urls.py          # URLs principales
│   └── wsgi.py          # Configuración WSGI
├── media/              # Archivos subidos por usuarios
├── static/             # Archivos estáticos globales
├── manage.py           # Script de gestión de Django
└── requirements.txt    # Dependencias del proyecto
```

## 🔐 Configuración de Seguridad

- CSRF protection habilitada
- Manejo seguro de archivos media
- Validación de formularios
- Autenticación requerida para acciones sensibles

## 👥 Contribución

Si deseas contribuir al proyecto:

1. Haz un Fork del repositorio
2. Crea una rama para tu característica (`git checkout -b feature/AmazingFeature`)
3. Realiza tus cambios y haz commit (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT - mira el archivo [LICENSE.md](LICENSE.md) para detalles

## ✒️ Autores

* **Jonathan Franco** - *Desarrollo Inicial* - [JonathanFrancoC](https://github.com/JonathanFrancoC)

## 📞 Soporte

Para soporte y preguntas, por favor abre un issue en el repositorio. 