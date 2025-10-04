# Guía Rápida - Ejecutar Tests de API de Recursos en Proyectos

## 🚀 Ejecutar Todos los Tests

```bash
cd /Users/eduardo/Repositorios/mantis/app/src

# Ejecutar todos los tests de recursos en proyectos
pytest tests/api/test_AddResourceProjectAPI.py \
       tests/api/test_DeleteResourceProjectAPI.py \
       tests/api/test_ResourcesAvailableAPI.py -v

# Con salida más detallada
pytest tests/api/test_*Resource*.py -vv

# Con captura de prints
pytest tests/api/test_*Resource*.py -v -s
```

## 📊 Ejecutar con Reporte de Cobertura

```bash
# Generar reporte HTML
pytest tests/api/test_*Resource*.py \
       --cov=api.projects \
       --cov-report=html \
       --cov-report=term

# Ver el reporte
open htmlcov/index.html
```

## 🎯 Ejecutar Tests Específicos

### Solo AddResourceProjectAPI
```bash
pytest tests/api/test_AddResourceProjectAPI.py -v

# Un test específico
pytest tests/api/test_AddResourceProjectAPI.py::TestAddResourceProjectAPI::test_add_resource_success -v
```

### Solo DeleteResourceProjectAPI
```bash
pytest tests/api/test_DeleteResourceProjectAPI.py -v

# Un test específico
pytest tests/api/test_DeleteResourceProjectAPI.py::TestDeleteResourceProjectAPI::test_delete_resource_success -v
```

### Solo ResourcesAvailableAPI
```bash
pytest tests/api/test_ResourcesAvailableAPI.py -v

# Un test específico
pytest tests/api/test_ResourcesAvailableAPI.py::TestResourcesAvailableAPI::test_get_all_available_resources -v
```

## 🔍 Ejecutar con Filtros

```bash
# Solo tests que contengan "success" en el nombre
pytest tests/api/test_*Resource*.py -k "success" -v

# Solo tests de validación (error)
pytest tests/api/test_*Resource*.py -k "invalid" -v

# Excluir tests lentos (si los marcamos)
pytest tests/api/test_*Resource*.py -m "not slow" -v
```

## 🐛 Debug de Tests

```bash
# Detener en el primer fallo
pytest tests/api/test_*Resource*.py -x

# Mostrar variables locales en fallos
pytest tests/api/test_*Resource*.py -l

# Modo debug completo
pytest tests/api/test_*Resource*.py -vv -s --tb=long

# Con pdb (debugger)
pytest tests/api/test_AddResourceProjectAPI.py --pdb
```

## 📈 Estadísticas y Reportes

```bash
# Duración de cada test
pytest tests/api/test_*Resource*.py -v --durations=10

# Resumen corto
pytest tests/api/test_*Resource*.py -q

# Solo estadísticas (sin ejecutar)
pytest tests/api/test_*Resource*.py --collect-only
```

## 🔄 Ejecutar en Paralelo (más rápido)

```bash
# Instalar pytest-xdist primero
pip install pytest-xdist

# Ejecutar con 4 workers
pytest tests/api/test_*Resource*.py -n 4

# Auto-detectar número de CPUs
pytest tests/api/test_*Resource*.py -n auto
```

## 📝 Generar Reportes Personalizados

```bash
# Reporte JUnit XML (para CI/CD)
pytest tests/api/test_*Resource*.py --junitxml=report.xml

# Reporte HTML bonito (requiere pytest-html)
pip install pytest-html
pytest tests/api/test_*Resource*.py --html=report.html --self-contained-html
```

## ✅ Verificar Código Antes de Commit

```bash
# Tests + linting
pytest tests/api/test_*Resource*.py -v && \
flake8 api/projects/*.py tests/api/test_*Resource*.py

# Solo verificar sintaxis (no ejecutar)
python -m py_compile tests/api/test_*.py
```

## 🎭 Mock y Fixtures

```bash
# Ver fixtures disponibles
pytest --fixtures tests/api/test_AddResourceProjectAPI.py

# Ver setup/teardown
pytest tests/api/test_AddResourceProjectAPI.py --setup-show
```

## 💾 Guardar Resultados

```bash
# Guardar salida en archivo
pytest tests/api/test_*Resource*.py -v > test_results.txt 2>&1

# Solo fallos en archivo
pytest tests/api/test_*Resource*.py -v --tb=short > failures.txt 2>&1
```

## 🔧 Configuración Recomendada

Crear archivo `pytest.ini` en la raíz del proyecto:

```ini
[pytest]
DJANGO_SETTINGS_MODULE = peisol.settings
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = 
    -v
    --strict-markers
    --tb=short
    --disable-warnings
markers =
    slow: marks tests as slow
    integration: marks tests as integration tests
    unit: marks tests as unit tests
```

## 📋 Checklist Pre-Commit

```bash
# 1. Ejecutar todos los tests
pytest tests/api/test_*Resource*.py -v

# 2. Verificar cobertura mínima (80%)
pytest tests/api/test_*Resource*.py --cov=api.projects --cov-fail-under=80

# 3. Verificar estilo de código
flake8 api/projects/ --max-line-length=100

# 4. Ejecutar solo tests rápidos primero
pytest tests/api/test_*Resource*.py -k "not slow" -v

# 5. Si todo pasa, ejecutar suite completa
pytest tests/api/ -v
```

## 🎯 Casos de Uso Comunes

### Desarrollo de nueva funcionalidad
```bash
# Ejecutar solo el test que estás desarrollando
pytest tests/api/test_AddResourceProjectAPI.py::TestAddResourceProjectAPI::test_add_resource_success -v -s
```

### Antes de hacer PR
```bash
# Suite completa con cobertura
pytest tests/api/test_*Resource*.py -v --cov=api.projects --cov-report=term-missing
```

### Debug de un fallo
```bash
# Ejecutar con máximo detalle
pytest tests/api/test_DeleteResourceProjectAPI.py::TestDeleteResourceProjectAPI::test_delete_resource_success -vv -s --tb=long -l
```

### CI/CD Pipeline
```bash
# Formato para integración continua
pytest tests/api/test_*Resource*.py \
       --junitxml=junit.xml \
       --cov=api.projects \
       --cov-report=xml \
       --cov-report=term
```

## 🚨 Troubleshooting

### Error: "No module named 'api'"
```bash
# Asegúrate de estar en el directorio correcto
cd /Users/eduardo/Repositorios/mantis/app/src
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

### Error: "Database locked"
```bash
# Usar base de datos en memoria para tests
pytest tests/api/test_*Resource*.py --reuse-db
```

### Tests muy lentos
```bash
# Ejecutar en paralelo
pytest tests/api/test_*Resource*.py -n auto
```

### Fallos intermitentes
```bash
# Ejecutar múltiples veces
pytest tests/api/test_*Resource*.py --count=3
```

---

## 📞 Contacto y Soporte

Si encuentras problemas:
1. Verifica que Django esté configurado correctamente
2. Asegúrate de tener todas las dependencias instaladas
3. Verifica que la base de datos de pruebas esté accesible
4. Revisa los logs en `logs/app.log`
