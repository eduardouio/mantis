#!/bin/bash

# Script para limpiar archivos de cache y migraciones temporales
# Uso: ./clean_cache.sh

echo "🧹 Limpiando archivos de cache de Python..."

# Eliminar archivos .pyc
find . -name "*.pyc" -delete

# Eliminar directorios __pycache__
find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true

# Eliminar archivos de cache de pytest
find . -name ".pytest_cache" -type d -exec rm -rf {} + 2>/dev/null || true

# Limpiar logs de Django
find . -name "*.log" -type f -delete 2>/dev/null || true

echo "✅ Limpieza completada"

# Opcional: Mostrar estado de git
if [ -d ".git" ]; then
    echo ""
    echo "📊 Estado de Git:"
    git status --porcelain
fi