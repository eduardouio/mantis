"""
Script de prueba para demostrar la integración de StatusResourceItem 
con ResourceItemDetailView

Este script muestra cómo la clase StatusResourceItem se integra 
con la vista de presentación de recursos.
"""

from equipment.models.ResourceItem import ResourceItem
from common.StatusResourceItem import StatusResourceItem


def demo_integration():
    """Demostrar la integración completa del análisis de estado."""
    
    print("=== DEMO: INTEGRACIÓN StatusResourceItem + Vista ===\n")
    
    # Simular obtención de equipo (como en la vista)
    try:
        equipment = ResourceItem.objects.first()
        if not equipment:
            print("No hay equipos en la base de datos para la demo")
            return
        
        print(f"Analizando equipo: {equipment.name} [{equipment.code}]")
        print("=" * 50)
        
        # Esto es lo que hace la vista en _get_equipment_status_analysis
        analyzer = StatusResourceItem(equipment)
        status_report = analyzer.get_status_report()
        
        # Información que se pasa al template
        context_data = {
            'status_analysis': status_report,
            'equipment_completeness': {
                'is_complete': status_report['completeness']['is_complete'],
                'completion_percentage': status_report['completeness']['completion_percentage'],
                'missing_items': status_report['completeness']['missing_items'],
                'missing_count': len(status_report['completeness']['missing_items']),
            },
            'equipment_availability': {
                'status': status_report['availability']['status'],
                'current_location': status_report['availability']['current_location'],
                'commitment_date': status_report['availability']['commitment_date'],
                'release_date': status_report['availability']['release_date'],
            },
            'project_analysis': status_report.get('project_info'),
            'rental_analysis': status_report.get('rental_info'),
            'inconsistencies_analysis': {
                'found': status_report['inconsistencies']['found'],
                'needs_update': status_report['inconsistencies']['needs_update'],
                'count': len(status_report['inconsistencies']['found']),
            },
            'recommendations': status_report['recommendations'],
        }
        
        # Mostrar información como aparecería en el template
        print_template_data(context_data)
        
    except Exception as e:
        print(f"Error en la demo: {e}")


def print_template_data(context):
    """Imprimir datos como aparecerían en el template."""
    
    completeness = context['equipment_completeness']
    availability = context['equipment_availability']
    inconsistencies = context['inconsistencies_analysis']
    
    print("📊 ESTADO DE COMPLETITUD")
    print(f"   Completo: {'✅ SÍ' if completeness['is_complete'] else '❌ NO'}")
    print(f"   Porcentaje: {completeness['completion_percentage']}%")
    if completeness['missing_count'] > 0:
        print(f"   Faltan: {completeness['missing_count']} elementos")
        for item in completeness['missing_items']:
            print(f"     - {item['label']}")
    print()
    
    print("🏷️ DISPONIBILIDAD")
    print(f"   Estado: {availability['status']}")
    if availability['current_location']:
        print(f"   Ubicación: {availability['current_location']}")
    if availability['commitment_date']:
        print(f"   Fecha ocupación: {availability['commitment_date']}")
    if availability['release_date']:
        print(f"   Fecha liberación: {availability['release_date']}")
    print()
    
    print("⚠️ CONSISTENCIA DE DATOS")
    if inconsistencies['needs_update']:
        print(f"   ❌ REQUIERE ATENCIÓN ({inconsistencies['count']} problemas)")
        for issue in inconsistencies['found']:
            print(f"     • {issue['type']}: {issue['description']}")
    else:
        print("   ✅ DATOS CONSISTENTES")
    print()
    
    print("💡 RECOMENDACIONES")
    for rec in context['recommendations']:
        print(f"   • {rec}")
    print()
    
    if context['project_analysis']:
        print("🏗️ INFORMACIÓN DEL PROYECTO")
        project = context['project_analysis']
        print(f"   Cliente: {project['partner_name']}")
        print(f"   Contacto: {project['contact_name']}")
        print(f"   Ubicación: {project['location']}")
        print(f"   Estado: {'Cerrado' if project['is_closed'] else 'Activo'}")
        if project.get('rent_cost'):
            print(f"   Costo renta: ${project['rent_cost']}")
        print()
    
    if context['rental_analysis']:
        print("💰 INFORMACIÓN DE RENTA")
        rental = context['rental_analysis']
        print(f"   Estado: {rental['rental_status']}")
        print(f"   Cliente: {rental['project_partner']}")
        if rental.get('remaining_days') is not None:
            print(f"   Días restantes: {rental['remaining_days']}")
        print()


def demo_template_classes():
    """Demostrar las clases CSS que se aplicarían en el template."""
    
    print("=== DEMO: CLASES CSS PARA EL TEMPLATE ===\n")
    
    # Ejemplos de diferentes estados
    scenarios = [
        {
            'name': 'Equipo Completo y Disponible',
            'completeness': {'is_complete': True, 'completion_percentage': 100},
            'inconsistencies': {'needs_update': False, 'count': 0},
            'availability': 'DISPONIBLE'
        },
        {
            'name': 'Equipo Incompleto',
            'completeness': {'is_complete': False, 'completion_percentage': 75},
            'inconsistencies': {'needs_update': False, 'count': 0},
            'availability': 'DISPONIBLE'
        },
        {
            'name': 'Equipo con Inconsistencias',
            'completeness': {'is_complete': True, 'completion_percentage': 100},
            'inconsistencies': {'needs_update': True, 'count': 2},
            'availability': 'RENTADO'
        }
    ]
    
    for scenario in scenarios:
        print(f"📋 {scenario['name']}")
        print("   Clases CSS aplicadas:")
        
        # Simular lógica de clases CSS
        completeness = scenario['completeness']
        inconsistencies = scenario['inconsistencies']
        
        # Clase de completitud
        completeness_class = 'text-green-600' if completeness['is_complete'] else 'text-red-600'
        print(f"     Completitud: {completeness_class}")
        
        # Clase de inconsistencias
        inconsistencies_class = 'text-red-600' if inconsistencies['needs_update'] else 'text-green-600'
        print(f"     Inconsistencias: {inconsistencies_class}")
        
        # Badge general
        if completeness['is_complete'] and not inconsistencies['needs_update']:
            overall_badge = 'badge-success'
            status_text = "✓ ESTADO OK"
        elif inconsistencies['needs_update']:
            overall_badge = 'badge-error'
            status_text = "⚠ REQUIERE ATENCIÓN"
        else:
            overall_badge = 'badge-warning'
            status_text = "⚡ INCOMPLETO"
        
        print(f"     Badge general: {overall_badge}")
        print(f"     Texto mostrado: '{status_text}'")
        print()


def demo_ajax_integration():
    """Demostrar cómo funcionaría la corrección automática via AJAX."""
    
    print("=== DEMO: INTEGRACIÓN AJAX PARA CORRECCIÓN AUTOMÁTICA ===\n")
    
    equipment = ResourceItem.objects.first()
    if not equipment:
        print("No hay equipos para la demo")
        return
    
    print(f"Equipo: {equipment.name}")
    
    # Análisis inicial
    analyzer = StatusResourceItem(equipment)
    initial_report = analyzer.get_status_report()
    
    print("Estado inicial:")
    if initial_report['inconsistencies']['needs_update']:
        print(f"  ❌ {len(initial_report['inconsistencies']['found'])} inconsistencias encontradas")
        for inc in initial_report['inconsistencies']['found']:
            print(f"     • {inc['type']}")
    else:
        print("  ✅ Sin inconsistencias")
    
    # Simular corrección automática (lo que haría el endpoint AJAX)
    if initial_report['inconsistencies']['needs_update']:
        print("\n🔧 Aplicando corrección automática...")
        update_result = analyzer.update_equipment_status()
        
        if update_result['updated']:
            print(f"  ✅ {update_result['message']}")
            for update in update_result['updates_made']:
                print(f"     • {update}")
            
            # Estado después de la corrección
            final_report = analyzer.get_status_report()
            print("\nEstado después de la corrección:")
            if final_report['inconsistencies']['needs_update']:
                print(f"  ⚠️ Aún quedan {len(final_report['inconsistencies']['found'])} problemas")
            else:
                print("  ✅ Todos los problemas corregidos")
        else:
            print(f"  ℹ️ {update_result['message']}")
    
    print()


if __name__ == "__main__":
    """
    Ejecutar demos de integración.
    
    Ejecutar desde Django shell:
    python manage.py shell
    >>> exec(open('demo_integration.py').read())
    
    O copiar y pegar las funciones individuales.
    """
    
    print("StatusResourceItem + ResourceItemDetailView Integration Demo")
    print("=" * 60)
    
    try:
        demo_integration()
        print("\n" + "=" * 60 + "\n")
        demo_template_classes()
        print("\n" + "=" * 60 + "\n")
        demo_ajax_integration()
    except Exception as e:
        print(f"Error ejecutando demo: {e}")
        print("Asegúrate de ejecutar esto desde el shell de Django:")
        print("python manage.py shell")
        print(">>> exec(open('demo_integration.py').read())")