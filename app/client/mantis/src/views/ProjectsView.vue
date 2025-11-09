<script setup>
import TabResources from '@/components/projects/TabResources.vue'
import TabSheetProject from '@/components/projects/TabSheetProject.vue'
import TabCalendar from '@/components/projects/TabCalendar.vue'
</script>

<template>
  <div>
    <div id="project-app" class="w-[90%] mx-auto p-4 bg-white rounded-2xl shadow-md border border-blue-300 border-t-[15px] border-t-blue-300">
      <div class="flex justify-between items-center border-b-blue-500 border-b pb-1 mb-3">
        <h1 class="text-xl font-semibold text-blue-500">Ficha de Proyecto</h1>
        <div class="text-gray-500">
          <span class="badge badge-success">
            Abierto
          </span>
        </div>
      </div>

      <!-- Información del Proyecto -->
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        <!-- Columna 1 -->
        <div class="space-y-2">
          <div class="flex items-center gap-2 py-1 border-b border-gray-200">
            <i class="las la-hashtag text-blue-500"></i>
            <span class="text-xs text-gray-500 w-32">ID Proyecto:</span>
            <span class="font-semibold text-sm">#1</span>
          </div>
          <div class="flex items-center gap-2 py-1 border-b border-gray-200">
            <i class="las la-building text-blue-500"></i>
            <span class="text-xs text-gray-500 w-32">Cliente:</span>
            <span class="font-semibold text-sm">
              <a href="#" class="link link-hover">
                Cliente Ejemplo
              </a>
            </span>
          </div>
          <div class="flex items-center gap-2 py-1 border-b border-gray-200">
            <i class="las la-map-marker text-blue-500"></i>
            <span class="text-xs text-gray-500 w-32">Ubicación:</span>
            <span class="font-semibold text-sm">Ubicación del Proyecto</span>
          </div>
          <div class="flex items-center gap-2 py-1 border-b border-gray-200">
            <i class="las la-info-circle text-blue-500"></i>
            <span class="text-xs text-gray-500 w-32">Estado:</span>
            <span class="badge badge-sm badge-success">
              Abierto
            </span>
          </div>
        </div>

        <!-- Columna 2 -->
        <div class="space-y-2">
          <div class="flex items-center gap-2 py-1 border-b border-gray-200">
            <i class="las la-calendar-check text-blue-500"></i>
            <span class="text-xs text-gray-500 w-32">Fecha Inicio:</span>
            <span class="font-semibold text-sm">01/01/2025</span>
          </div>
          <div class="flex items-center gap-2 py-1 border-b border-gray-200">
            <i class="las la-calendar-times text-blue-500"></i>
            <span class="text-xs text-gray-500 w-32">Fecha Fin:</span>
            <span class="font-semibold text-sm">08/04/2025</span>
          </div>
          <div class="flex items-center gap-2 py-1 border-b border-gray-200">
            <i class="las la-hourglass-half text-blue-500"></i>
            <span class="text-xs text-gray-500 w-32">Duración:</span>
            <span class="font-semibold text-sm">97 días</span>
          </div>
          <div class="flex items-center gap-2 py-1 border-b border-gray-200">
            <i class="las la-dollar-sign text-blue-500"></i>
            <span class="text-xs text-gray-500 w-32">Valor Total:</span>
            <span class="font-semibold text-sm text-green-600">$97,485.00</span>
          </div>
        </div>

        <!-- Columna 3 -->
        <div class="space-y-2">
          <div class="flex items-center gap-2 py-1 border-b border-gray-200">
            <i class="las la-user text-blue-500"></i>
            <span class="text-xs text-gray-500 w-32">Contacto:</span>
            <span class="font-semibold text-sm">Juan García</span>
          </div>
          <div class="flex items-center gap-2 py-1 border-b border-gray-200">
            <i class="las la-phone text-blue-500"></i>
            <span class="text-xs text-gray-500 w-32">Teléfono:</span>
            <span class="font-semibold text-sm">+34 612 345 678</span>
          </div>
          <div class="flex items-center gap-2 py-1 border-b border-gray-200">
            <i class="las la-envelope text-blue-500"></i>
            <span class="text-xs text-gray-500 w-32">Email:</span>
            <span class="font-semibold text-sm">juan@example.com</span>
          </div>
          <div class="flex items-center gap-2 py-1 border-b border-gray-200">
            <i class="las la-sticky-note text-blue-500"></i>
            <span class="text-xs text-gray-500 w-32">Notas:</span>
            <span class="font-semibold text-sm">Notas del proyecto ejemplo</span>
          </div>
        </div>
      </div>

      <!-- Tabs para organizar el contenido -->
      <div role="tablist" class="tabs tabs-lifted mt-4 bg-gray-100 border border-blue-100 p-1">
        <input type="radio" name="project_tabs" role="tab" class="tab bg-red-300" aria-label="Equipos Asignados" checked />
        <div role="tabpanel" class="tab-content bg-base-100 border-base-300 rounded-box p-4">
          <TabResources />
        </div>

        <input type="radio" name="project_tabs" role="tab" class="tab bg-blue-300" aria-label="Órdenes de Trabajo" />
        <div role="tabpanel" class="tab-content bg-base-100 border-base-300 rounded-box p-4">
          <TabSheetProject />
        </div>

        <input type="radio" name="project_tabs" role="tab" class="tab bg-orange-300" aria-label="Calendario Mantenimientos" />
        <div role="tabpanel" class="tab-content bg-base-100 border-base-300 rounded-box p-4">
          <TabCalendar />
        </div>
      </div>

      <!-- Botones de acción -->
      <div class="mt-8 pt-6 border-t">
        <div class="flex flex-wrap justify-center gap-3">
          <button class="btn btn-primary btn-sm">
            <i class="las la-plus text-xl"></i>
            Nuevo Proyecto
          </button>
          <button class="btn btn-primary btn-sm">
            <i class="las la-edit text-xl"></i>
            Editar Proyecto
          </button>
          <button class="btn btn-primary btn-sm">
            <i class="las la-trash text-xl"></i>
            Eliminar Proyecto
          </button>
          <button class="btn btn-primary btn-sm">
            <i class="las la-arrow-left text-xl"></i>
            Volver al Listado
          </button>
        </div>
      </div>
    </div>
  </div>
</template>