<script setup>
  import { RouterLink } from 'vue-router';
</script>
<template>
  <div class="container mx-auto p-4 max-w-4xl">
    <span class="font-bold text-lg bg-gray-100 rounded-md px-2 py-1 mb-4 inline-block w-full text-center">
      Planilla del Proyecto
    </span>
    <form class="card bg-base-100 shadow-xl border border-gray-200 rounded-lg">
      <div class="card-body space-y-4">
        
        <!-- Código de Serie (generado automáticamente) -->
        <div class="form-control w-full">
          <label class="label">
            <span class="label-text">Código de Serie</span>
          </label>
          <input 
            type="text" 
            id="series_code" 
            class="input input-bordered w-full bg-gray-100" 
            placeholder="PSL-PS-2024-0000"
            disabled
          />
          <label class="label">
            <span class="label-text-alt">Se genera automáticamente al guardar</span>
          </label>
        </div>

        <!-- Fecha de Emisión y Estado - Grid 2 columnas -->
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div class="form-control w-full">
            <label class="label">
              <span class="label-text">Fecha de Emisión</span>
            </label>
            <input
              id="issue_date"
              type="date"
              class="input input-bordered w-full"
            />
          </div>

          <div class="form-control w-full">
            <label class="label">
              <span class="label-text">Estado *</span>
            </label>
            <select id="status" class="select select-bordered w-full">
              <option value="IN_PROGRESS">EN EJECUCIÓN</option>
              <option value="INVOICED">FACTURADO</option>
              <option value="CANCELLED">CANCELADO</option>
            </select>
          </div>
        </div>

        <!-- Período de Facturación - Grid 2 columnas -->
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div class="form-control w-full">
            <label class="label">
              <span class="label-text">Fecha Inicio Período *</span>
            </label>
            <input
              id="period_start"
              type="date"
              class="input input-bordered w-full"
            />
          </div>

          <div class="form-control w-full">
            <label class="label">
              <span class="label-text">Fecha Fin Período *</span>
            </label>
            <input
              id="period_end"
              type="date"
              class="input input-bordered w-full"
            />
          </div>
        </div>

        <!-- Tipo de Servicio -->
        <div class="form-control w-full">
          <label class="label">
            <span class="label-text">Tipo de Servicio *</span>
          </label>
          <select id="service_type" class="select select-bordered w-full">
            <option value="ALQUILER">ALQUILER</option>
            <option value="MANTENIMIENTO">MANTENIMIENTO</option>
            <option value="ALQUILER Y MANTENIMIENTO">ALQUILER Y MANTENIMIENTO</option>
          </select>
        </div>

        <!-- Divisor -->
        <div class="divider">Cantidades</div>

        <!-- Galones, Barriles y M³ - Grid 3 columnas -->
        <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div class="form-control w-full">
            <label class="label">
              <span class="label-text">Total Galones</span>
            </label>
            <input
              id="total_gallons"
              type="number"
              min="0"
              placeholder="0"
              class="input input-bordered w-full"
            />
          </div>

          <div class="form-control w-full">
            <label class="label">
              <span class="label-text">Total Barriles</span>
            </label>
            <input
              id="total_barrels"
              type="number"
              min="0"
              placeholder="0"
              class="input input-bordered w-full"
            />
          </div>

          <div class="form-control w-full">
            <label class="label">
              <span class="label-text">Total Metros Cúbicos</span>
            </label>
            <input
              id="total_cubic_meters"
              type="number"
              min="0"
              placeholder="0"
              class="input input-bordered w-full"
            />
          </div>
        </div>

        <!-- Divisor -->
        <div class="divider">Referencias</div>

        <!-- Referencia PO Cliente y Contacto - Grid 2 columnas -->
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div class="form-control w-full">
            <label class="label">
              <span class="label-text">Referencia PO Cliente</span>
            </label>
            <input
              id="client_po_reference"
              type="text"
              placeholder="Número de orden de compra del cliente"
              class="input input-bordered w-full"
            />
          </div>

          <div class="form-control w-full">
            <label class="label">
              <span class="label-text">Referencia de Contacto</span>
            </label>
            <input
              id="contact_reference"
              type="text"
              placeholder="Nombre del contacto"
              class="input input-bordered w-full"
            />
          </div>
        </div>

        <!-- Teléfono y Disposición Final - Grid 2 columnas -->
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div class="form-control w-full">
            <label class="label">
              <span class="label-text">Teléfono de Contacto</span>
            </label>
            <input
              id="contact_phone_reference"
              type="tel"
              placeholder="0000-0000"
              class="input input-bordered w-full"
            />
          </div>

          <div class="form-control w-full">
            <label class="label">
              <span class="label-text">Disposición Final</span>
            </label>
            <input
              id="final_disposition_reference"
              type="text"
              placeholder="Referencia de disposición final"
              class="input input-bordered w-full"
            />
          </div>
        </div>

        <!-- Referencia de Factura -->
        <div class="form-control w-full">
          <label class="label">
            <span class="label-text">Referencia de Factura</span>
          </label>
          <input
            id="invoice_reference"
            type="text"
            placeholder="Número de factura relacionada"
            class="input input-bordered w-full"
          />
        </div>

        <!-- Divisor -->
        <div class="divider">Montos</div>

        <!-- Subtotal, IVA y Total - Grid 3 columnas -->
        <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div class="form-control w-full">
            <label class="label">
              <span class="label-text">Subtotal *</span>
            </label>
            <input
              id="subtotal"
              type="number"
              step="0.01"
              min="0"
              placeholder="0.00"
              class="input input-bordered w-full"
            />
          </div>

          <div class="form-control w-full">
            <label class="label">
              <span class="label-text">IVA (12%) *</span>
            </label>
            <input
              id="tax_amount"
              type="number"
              step="0.01"
              min="0"
              placeholder="0.00"
              class="input input-bordered w-full bg-gray-50"
              readonly
            />
            <label class="label">
              <span class="label-text-alt">Se calcula automáticamente</span>
            </label>
          </div>

          <div class="form-control w-full">
            <label class="label">
              <span class="label-text font-bold">Total *</span>
            </label>
            <input
              id="total"
              type="number"
              step="0.01"
              min="0"
              placeholder="0.00"
              class="input input-bordered w-full font-bold bg-gray-50"
              readonly
            />
            <label class="label">
              <span class="label-text-alt">Se calcula automáticamente</span>
            </label>
          </div>
        </div>

        <!-- Notas - Ancho completo -->
        <div class="form-control w-full">
          <label class="label">
            <span class="label-text">Notas</span>
          </label>
          <textarea
            id="notes"
            rows="3"
            placeholder="Notas adicionales sobre esta planilla"
            class="textarea textarea-bordered w-full"
          />
        </div>

        <!-- Divisor final -->
        <div class="divider"></div>

        <!-- Botones de Acción -->
        <div class="flex flex-col-reverse sm:flex-row gap-3 sm:justify-end">
          <RouterLink to="/project" class="btn btn-ghost">
            Cancelar
          </RouterLink>
          <button type="submit" class="btn btn-primary">
            Crear Planilla
          </button>
        </div>
      </div>
    </form>
  </div>
</template>