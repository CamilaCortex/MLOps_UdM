# 🚀 MLOps - Machine Learning Operations

**Universidad de Medellín - Curso de MLOps**

Aprende a llevar tus modelos de machine learning desde el desarrollo hasta producción de manera profesional, escalable y reproducible.

## 👩‍🏫 Instructora

### 🌟 **[María Camila Durango](https://www.linkedin.com/in/mar%C3%ADa-camila-durango-999224202/)**

MLOps Engineer y Software Engineer con 7 años de experiencia en desarrollo de producto y soluciones de alta calidad. He trabajado extensivamente en la **creación de pipelines de ML** y arquitectura de sistemas de machine learning. Actualmente trabajo en **Bancolombia** donde me enfoco en el desarrollo de software y arquitectura de sistemas en producción de IA, últimamente he trabajado con GenAI y agentes Procode. Amo codear y compartir todo lo que he aprendido sobre MLOps, desarrollo de software y arquitectura de sistemas.

## 🎯 Objetivos del Curso

Al finalizar este curso, serás capaz de:

- ✅ Diseñar y desarrollar **pipelines de ML modulares y mantenibles**
- ✅ Implementar **tracking de experimentos** y versionado de modelos
- ✅ Orquestar **workflows complejos** con herramientas modernas
- ✅ Desplegar **modelos en producción** como servicios web escalables
- ✅ Monitorear y mantener **sistemas de ML en producción**
- ✅ Aplicar **best practices de MLOps** en proyectos reales

## 📚 Contenido del Curso

### 01. 🔧 Introducción a ML y Setup
**Duración:** 2 horas

**Aprenderás:**
- Configuración de entornos profesionales con Python
- Gestión de dependencias con `uv` y entornos virtuales
- Git para control de versiones
- Jupyter notebooks y desarrollo iterativo
- Best practices de desarrollo

**Proyecto:** Setup completo de entorno de desarrollo

---

### 02. 📊 Experiment Tracking con MLflow
**Duración:** 3 horas

**Aprenderás:**
- Tracking de experimentos y métricas
- Logging de parámetros, artifacts y modelos
- Comparación de múltiples runs
- Model Registry para versionado
- Integración con frameworks (XGBoost, scikit-learn)

**Proyecto:** Sistema de tracking para modelo de predicción de precios

---

### 03. 🔄 Orquestación con Prefect
**Duración:** 4 horas

**Aprenderás:**
- Diseño de pipelines con Flows y Tasks
- Retry logic y error handling
- Caching y optimización de ejecución
- Deployments con schedules (cron)
- Monitoreo en Prefect Cloud
- Arquitectura modular con Domain-Driven Design

**Proyecto:** Pipeline completo de predicción de duración de viajes en taxi NYC
- Carga y validación de datos
- Feature engineering reproducible
- Optimización de hiperparámetros con Optuna
- Logging de 20+ trials en MLflow
- Deployment automático cada 2 minutos

---

### 04. 🚀 Deployment de Modelos
**Duración:** 4 horas

**Aprenderás:**
- Creación de APIs REST con Flask/FastAPI
- Containerización con Docker
- Deployment en la nube
- Versionado de modelos en producción
- Testing de servicios ML

**Proyecto:** API de predicción deployada en contenedor

---

### 05. 📈 Monitoreo y Observabilidad
**Duración:** 3 horas

**Aprenderás:**
- Métricas de performance en producción
- Detección de data drift
- Logging y alertas
- Dashboards de monitoreo
- Estrategias de re-entrenamiento

**Proyecto:** Sistema de monitoreo completo

---

### 06. 🏗️ Proyecto Final Integrador
**Duración:** 4 horas

**Implementarás:**
- Pipeline end-to-end completo
- Desde ingesta de datos hasta deployment
- Monitoreo y mantenimiento
- Documentación profesional
- Presentación de resultados

## 🛠️ Stack Tecnológico

- **Python 3.11+** - Lenguaje principal
- **MLflow** - Experiment tracking y model registry
- **Prefect** - Orquestación de workflows
- **XGBoost** - Modelo de ML
- **Optuna** - Optimización de hiperparámetros
- **Flask/FastAPI** - APIs REST
- **Docker** - Containerización
- **Git** - Control de versiones
- **uv** - Gestor de dependencias moderno

## 📋 Prerequisitos

- Conocimientos básicos de Python
- Familiaridad con machine learning (scikit-learn)
- Conocimientos básicos de terminal/línea de comandos
- Git básico (clone, commit, push)

## 🚀 Quick Start

```bash
# Clonar el repositorio
git clone https://github.com/CamilaCortex/MLOps_UdM.git
cd MLOps_UdM

# Crear entorno virtual
python -m venv .venv
source .venv/bin/activate  # En Windows: .venv\Scripts\activate


# Explorar los módulos
cd 01-Intro-ML          # Empezar por aquí
cd 02-Experiment-Tracking
cd 03-Orchestrarion
cd 04-Deployment
cd 05-Monitoring
```

## 📖 Estructura del Repositorio

```
MLOps_UdM/
├── 01-Intro-ML/                    # Setup y fundamentos
├── 02-Experiment-Tracking/         # MLflow tracking
├── 03-Orchestrarion/               # Prefect pipelines
│   ├── 00-intro-prefect/          # Conceptos básicos
│   └── Prefect-pipelines/         # Proyecto NYC Taxi
├── 04-Deployment/                  # Deployment de modelos
├── 05-Monitoring/                  # Observabilidad
└── 06-Proyecto-Final/             # Integración completa
```

## 💡 Metodología de Aprendizaje

### 🎓 Aprendizaje Práctico
Cada módulo incluye:
- **Teoría fundamental** con ejemplos claros
- **Ejercicios hands-on** paso a paso
- **Proyectos reales** aplicables a la industria
- **Best practices** de la industria

### 🔄 Iteración Continua
- Empezar simple, iterar hacia complejidad
- Refactorizar código para mejorar calidad
- Aplicar principios de software engineering

### 🤝 Colaboración
- Código versionado en Git
- Documentación clara y completa
- Code reviews y feedback

## 🎯 Criterios de Éxito

Al finalizar el curso, deberías poder:

- ✅ Ejecutar pipelines de ML completos de forma automática
- ✅ Trackear y comparar experimentos en MLflow
- ✅ Deployar modelos como servicios web
- ✅ Monitorear modelos en producción
- ✅ Explicar decisiones de arquitectura
- ✅ Aplicar MLOps en proyectos propios

## 📚 Recursos Adicionales

### Documentación Oficial
- [MLflow Documentation](https://mlflow.org/docs/latest/index.html)
- [Prefect Documentation](https://docs.prefect.io/)
- [Optuna Documentation](https://optuna.readthedocs.io/)
- [XGBoost Documentation](https://xgboost.readthedocs.io/)

### Libros Recomendados
- "Designing Machine Learning Systems" - Chip Huyen
- "Machine Learning Engineering" - Andriy Burkov
- "Building Machine Learning Powered Applications" - Emmanuel Ameisen

### Comunidades
- [MLOps Community](https://mlops.community/)
- [Prefect Community](https://www.prefect.io/slack)

## 🤝 Contribuciones

Este repositorio es material educativo en constante evolución. Las sugerencias y mejoras son bienvenidas.

## 📧 Contacto

**Universidad de Medellín**  
Facultad de Ingeniería  
Curso de MLOps

---

**Desarrollado con ❤️ para estudiantes de MLOps**  
*Última actualización: Abril 2026*
