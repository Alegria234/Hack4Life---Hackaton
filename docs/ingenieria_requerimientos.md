# 📊 Contexto del Problema

La dispersión de la información en el centro hospitalario afecta de forma directa el control y seguimiento de factores operativos críticos como:

* **Ocupación de camas:** Control y disponibilidad de camas por servicio.
* **Tiempos de espera:** Tiempos de ingreso a consulta y urgencias según el nivel de triage.
* **Uso de quirófanos:** Programación y disponibilidad de quirófanos libres.
* **Consumo de medicamentos:** Registro y rotación en recetario/farmacia.
* **Citas médicas:** Gestión y demanda de citas.

Esta fragmentación proviene de datos aislados en múltiples bases de datos no integradas (tales como *Historia Clínica*, *Farmacia* y *Admisiones*). Por lo que este escenario, surge la necesidad de optimizar el motor de búsqueda para consultas unificando en un aplicativo web. El objetivo es brindar agilidad en la atención de los pacientes, eficiencia operativa y claridad sobre cualquier tipo de consulta directiva u operativa.

---

## Ingeniería de Requerimientos

### Requerimientos Funcionales

| Código | Nombre | Descripción |
| :--- | :--- | :--- |
| **RF-01** | Carga de Datos | El sistema deberá contar con un inyector de datos a partir de archivos `.csv` o `.xlsx`, donde se validara la información antes de realizar cualquier tipo de operacion (filtrado de campos vacíos, valores nulos e incongruencias de datos). |
| **RF-02** | Agente LLM | El modelo LLM deberá procesar las peticiones del usuario convirtiéndolas a consultas SQL ejecutadas en un entorno controlado y limitado (consultas de lectura `SELECT` unicamente). |
| **RF-03** | Consultas | En caso de  indisponibilidad en la API que alberga el modelo LLM, el sistema deberá contar con un conjunto de preguntas frecuentes predefinidas asociadas a consultas SQL fijas para responder desde el backend. |
| **RF-04** | Dashboard Operativo | El dashboard estará orientado al personal administrativo para la visualización gráfica de los KPIs e indicadores críticos descritos en el contexto. |
| **RF-05** | Motor de Alertas | El sistema deberá generar alertas e indicadores con recomendaciones automáticas basadas en el estado de las métricas e inventarios (ej. stock crítico de medicamentos, alta saturación de camas) entre otros estados pertinentes. |
| **RF-06** | Página del Personal Médico | El personal médico podrá autenticarse mediante un login sencillo y realizar consultas conversacionales con el agente de IA en lenguaje natural sobre las necesidades operativas. |

### Requerimientos No Funcionales

| Código | Nombre | Descripción |
| :--- | :--- | :--- |
| **RNF-01** | Seguridad y Privacidad | Garantizar la anonimización total de los datos de los pacientes en las respuestas y vistas del sistema (sin exposición de datos PII como nombres o identificaciones). |
| **RNF-02** | Validación y Sanitización SQL | Comprobación y limpieza de las consultas SQL generadas por el modelo, previniendo ataques de inyección SQL y restringiendo cualquier operación de modificación de BD (`DROP`, `DELETE`, `UPDATE`, `INSERT`). |
| **RNF-03** | Rendimiento y Tiempos de Respuesta | Las consultas visuales del Dashboard deben responder en menos de 2 segundos y las interacciones conversacionales con el Agente de IA en menos de 5 segundos. |
| **RNF-04** | UX/UI y Usabilidad | La interfaz de usuario debe ser intuitiva, ágil y permitir una navegación clara entre los perfiles asignados. |
| **RNF-05** | Despliegue e Independencia | La ejecución del programa deberá realizarse en entornos controlados (local/virtualenv), manteniendo las configuraciones sensibles en variables de entorno `.env` de forma independiente. |

---

# 📊 Matriz de Trazabilidad de Requerimientos 

| ID Requerimiento | Nombre Requerimiento | Historia de Usuario / Épica (Scrum) | Criterios de Aceptación (Definition of Done) | Complejidad / Prioridad |
| :--- | :--- | :--- | :--- | :--- |
| **RF-01** | Carga de Datos | **US-01: Ingesta y Limpieza de Datos**<br>Como desarrollador backend, quiero un script/módulo que procese los CSVs hospitalarios para cargar datos limpios en la base de datos. | • Omisión o descarte de filas vacías y nulos en campos críticos.<br>• Creación automática de las tablas en la base de datos.<br>• Confirmación de carga con logs de salida. |  **Alta** |
| **RF-06** | Página del Personal Médico | **US-02: Autenticación de Perfiles Simples**<br>Como usuario del sistema, quiero ingresar credenciales para acceder a la vista que corresponde a mi rol (Médico u Operativo). | • Consulta directa a la tabla de usuarios local.<br>• Redirección correcta a la vista de médico (con chat) o directivo (dashboard solo lectura). | **Media** |
| **RF-04** | Dashboard Operativo | **US-03: Dashboard Analítico de KPIs Hospitalarios**<br>Como administrativo, quiero ver indicadores gráficos en tiempo real para tomar decisiones sobre ocupación y recursos. | • Visualización de métricas clave (camas ocupadas %, tiempos de triage, stock crítico de medicamentos).<br>• Carga e interacción gráfica en < 2 segundos (RNF-03). |  **Alta** |
| **RF-02** | Agente LLM | **US-04: Agente Conversacional NL2SQL**<br>Como personal médico, quiero realizar preguntas en lenguaje natural para consultar la base de datos sin escribir SQL. | • Generación de consultas `SELECT` válidas.<br>• Procesamiento de la pregunta y retorno del resultado en lenguaje natural / tabla en < 5 segundos (RNF-03). | **Alta** |
| **RNF-01**<br>**RNF-02** | Seguridad y Sanitización SQL | **US-05: Capa de Seguridad y Sanitización**<br>Como administrador del sistema, quiero asegurar que las consultas del LLM sean seguras y no alteren la base de datos ni expongan PII. | • Bloqueo de sentencias `DROP`, `DELETE`, `UPDATE`, `INSERT`.<br>• Ocultación/Anulamiento de datos sensibles de pacientes (PII) en los resultados. | **Alta** | 
| **RF-03** | Consultas de Contingencia (Fallback) | **US-06: Mecanismo de Fallback por Reglas/SQL Fijo**<br>Como usuario, quiero recibir respuestas a las 4 preguntas principales de la hackatón aunque la API de la IA no responda. | • Mapeo de 4 preguntas clave predefinidas a consultas SQL directas en el backend.<br>• Activación automática si el LLM falla o tarda más del tiempo límite. | **Alta** |
| **RF-05** | Motor de Alertas | **US-07: Módulo de Alertas Preventivas**<br>Como jefe de servicio, quiero recibir alertas sobre stock crítico de medicamentos o saturación de camas. | • Indicadores de alerta visual (color rojo/amarillo) en el Dashboard.<br>• Sugerencias automáticas adjuntas al resultado del chat. | **Media** |

---

## 2. Planificación de Sprints

### 🟢 Sprint 1: Base de Datos y Autenticación (Horas 0 - 2)
* **US-01 (RF-01):** Crear script de ingesta de CSVs con validación de nulos y vacíos.
* **US-02 (RF-06):** Configurar autenticación básica para la separación de perfiles (Médico vs. Administrativo).

### 🟡 Sprint 2: Core de IA, Backend y Seguridad (Horas 2 - 5)
* **US-04 (RF-02):** Implementar el motor NL2SQL para procesar peticiones en lenguaje natural.
* **US-05 (RNF-01, RNF-02):** Agregar middleware/filtro de sanitización SQL y anonimización de datos de pacientes.
* **US-06 (RF-03):** Construir el fallback de preguntas frecuentes predefinidas.

### 🔵 Sprint 3: Visualización, Alertas e Integración (Horas 5 - 8)
* **US-03 (RF-04):** Construir las tarjetas e indicadores gráficos del Dashboard Operativo.
* **US-07 (RF-05):** Añadir el motor de alertas visuales para stock de medicamentos y ocupación de camas.
* **Integración Final:** Pruebas end-to-end con las 4 consultas clave de la demo.