<template>
  <div class="space-y-3">
    <div class="flex justify-between items-center">
      <h2 class="text-lg font-semibold text-gray-800 flex items-center gap-2">
        <i class="las la-calendar text-red-600 text-xl"></i>
        Calendario de Mantenimientos
      </h2>
      <div class="join">
        <button class="btn btn-xs join-item btn-outline">Mes</button>
        <button class="btn btn-xs join-item btn-outline">Cronograma</button>
        <button class="btn btn-xs join-item btn-active">Semana</button>
      </div>
    </div>

    <!-- Vista de grilla semanal -->
    <div class="card bg-base-100 shadow border">
      <div class="card-body p-3">
        <div class="flex justify-between items-center mb-3">
          <h3 class="font-semibold text-base">Semana del 5 al 11 de Agosto 2025</h3>
          <div class="join">
            <button class="btn btn-xs join-item">
              <i class="las la-chevron-left"></i>
            </button>
            <button class="btn btn-xs join-item">Hoy</button>
            <button class="btn btn-xs join-item">
              <i class="las la-chevron-right"></i>
            </button>
          </div>
        </div>

        <div class="overflow-x-auto">
          <table class="table table-xs w-full border">
            <thead>
              <tr class="bg-base-200">
                <th class="sticky left-0 bg-base-200 z-10 w-48">Equipo</th>
                <th class="text-center min-w-[120px]">
                  <div class="font-bold">LUN</div>
                  <div class="text-xs font-normal">05 Ago</div>
                </th>
                <th class="text-center min-w-[120px]">
                  <div class="font-bold">MAR</div>
                  <div class="text-xs font-normal">06 Ago</div>
                </th>
                <th class="text-center min-w-[120px]">
                  <div class="font-bold">MIÉ</div>
                  <div class="text-xs font-normal">07 Ago</div>
                </th>
                <th class="text-center min-w-[120px]">
                  <div class="font-bold">JUE</div>
                  <div class="text-xs font-normal">08 Ago</div>
                </th>
                <th class="text-center min-w-[120px]">
                  <div class="font-bold">VIE</div>
                  <div class="text-xs font-normal">09 Ago</div>
                </th>
                <th class="text-center min-w-[120px]">
                  <div class="font-bold text-blue-600">SÁB</div>
                  <div class="text-xs font-normal text-blue-600">10 Ago</div>
                </th>
                <th class="text-center min-w-[120px]">
                  <div class="font-bold text-error">DOM</div>
                  <div class="text-xs font-normal text-error">11 Ago</div>
                </th>
              </tr>
            </thead>
            <tbody>
              <!-- Lavamanos LAV-001 -->
              <tr class="hover">
                <td class="sticky left-0 bg-base-100 z-10 font-medium">
                  <div class="flex items-center gap-2">
                    <i class="las la-toilet text-blue-500"></i>
                    <div>
                      <div class="font-semibold text-xs">LAV-001</div>
                      <div class="text-xs text-gray-500">Lavamanos</div>
                    </div>
                  </div>
                </td>
                <td class="text-center bg-blue-50">
                  <div class="badge badge-primary badge-xs">Limpieza</div>
                  <div class="text-xs text-gray-600">08:00</div>
                </td>
                <td class="text-center"></td>
                <td class="text-center bg-blue-50">
                  <div class="badge badge-primary badge-xs">Limpieza</div>
                  <div class="text-xs text-gray-600">08:00</div>
                </td>
                <td class="text-center"></td>
                <td class="text-center bg-blue-50">
                  <div class="badge badge-primary badge-xs">Limpieza</div>
                  <div class="text-xs text-gray-600">08:00</div>
                </td>
                <td class="text-center"></td>
                <td class="text-center"></td>
              </tr>

              <!-- Batería Sanitaria BSH-002 -->
              <tr class="hover">
                <td class="sticky left-0 bg-base-100 z-10 font-medium">
                  <div class="flex items-center gap-2">
                    <i class="las la-bath text-green-500"></i>
                    <div>
                      <div class="font-semibold text-xs">BSH-002</div>
                      <div class="text-xs text-gray-500">Batería Sanitaria</div>
                    </div>
                  </div>
                </td>
                <td class="text-center"></td>
                <td class="text-center"></td>
                <td class="text-center bg-green-50">
                  <div class="badge badge-secondary badge-xs">Mantenimiento</div>
                  <div class="text-xs text-gray-600">10:00</div>
                </td>
                <td class="text-center"></td>
                <td class="text-center"></td>
                <td class="text-center"></td>
                <td class="text-center"></td>
              </tr>

              <!-- Planta Tratamiento PTA-003 -->
              <tr class="hover">
                <td class="sticky left-0 bg-base-100 z-10 font-medium">
                  <div class="flex items-center gap-2">
                    <i class="las la-industry text-yellow-600"></i>
                    <div>
                      <div class="font-semibold text-xs">PTA-003</div>
                      <div class="text-xs text-gray-500">Planta Tratamiento</div>
                    </div>
                  </div>
                </td>
                <td class="text-center"></td>
                <td class="text-center"></td>
                <td class="text-center"></td>
                <td class="text-center"></td>
                <td class="text-center bg-yellow-50">
                  <div class="badge badge-warning badge-xs">Revisión</div>
                  <div class="text-xs text-gray-600">14:00</div>
                </td>
                <td class="text-center"></td>
                <td class="text-center"></td>
              </tr>

              <!-- Tanque Almacenamiento TNK-004 -->
              <tr class="hover">
                <td class="sticky left-0 bg-base-100 z-10 font-medium">
                  <div class="flex items-center gap-2">
                    <i class="las la-database text-purple-500"></i>
                    <div>
                      <div class="font-semibold text-xs">TNK-004</div>
                      <div class="text-xs text-gray-500">Tanque Almacenamiento</div>
                    </div>
                  </div>
                </td>
                <td class="text-center"></td>
                <td class="text-center bg-purple-50">
                  <div class="badge badge-info badge-xs">Inspección</div>
                  <div class="text-xs text-gray-600">09:00</div>
                </td>
                <td class="text-center"></td>
                <td class="text-center"></td>
                <td class="text-center"></td>
                <td class="text-center"></td>
                <td class="text-center"></td>
              </tr>

              <!-- Bomba de Agua BOM-005 -->
              <tr class="hover">
                <td class="sticky left-0 bg-base-100 z-10 font-medium">
                  <div class="flex items-center gap-2">
                    <i class="las la-tint text-cyan-500"></i>
                    <div>
                      <div class="font-semibold text-xs">BOM-005</div>
                      <div class="text-xs text-gray-500">Bomba de Agua</div>
                    </div>
                  </div>
                </td>
                <td class="text-center bg-cyan-50">
                  <div class="badge badge-accent badge-xs">Lubricación</div>
                  <div class="text-xs text-gray-600">07:00</div>
                </td>
                <td class="text-center"></td>
                <td class="text-center"></td>
                <td class="text-center bg-cyan-50">
                  <div class="badge badge-accent badge-xs">Lubricación</div>
                  <div class="text-xs text-gray-600">07:00</div>
                </td>
                <td class="text-center"></td>
                <td class="text-center"></td>
                <td class="text-center"></td>
              </tr>

              <!-- Generador GEN-006 -->
              <tr class="hover">
                <td class="sticky left-0 bg-base-100 z-10 font-medium">
                  <div class="flex items-center gap-2">
                    <i class="las la-bolt text-orange-500"></i>
                    <div>
                      <div class="font-semibold text-xs">GEN-006</div>
                      <div class="text-xs text-gray-500">Generador Eléctrico</div>
                    </div>
                  </div>
                </td>
                <td class="text-center"></td>
                <td class="text-center"></td>
                <td class="text-center"></td>
                <td class="text-center"></td>
                <td class="text-center"></td>
                <td class="text-center bg-orange-50">
                  <div class="badge badge-warning badge-xs">Prueba</div>
                  <div class="text-xs text-gray-600">11:00</div>
                </td>
                <td class="text-center"></td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- Leyenda -->
        <div class="mt-4 flex flex-wrap gap-3 text-xs">
          <div class="flex items-center gap-1">
            <div class="badge badge-primary badge-xs"></div>
            <span>Limpieza</span>
          </div>
          <div class="flex items-center gap-1">
            <div class="badge badge-secondary badge-xs"></div>
            <span>Mantenimiento</span>
          </div>
          <div class="flex items-center gap-1">
            <div class="badge badge-warning badge-xs"></div>
            <span>Revisión</span>
          </div>
          <div class="flex items-center gap-1">
            <div class="badge badge-info badge-xs"></div>
            <span>Inspección</span>
          </div>
          <div class="flex items-center gap-1">
            <div class="badge badge-accent badge-xs"></div>
            <span>Lubricación</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
