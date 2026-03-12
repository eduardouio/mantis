<script setup>
import { ref, computed, onMounted } from 'vue';
import { UseResourcesStore } from '@/stores/ResourcesStore';

const props = defineProps({
  label: {
    type: String,
    default: 'Recurso'
  },
  placeholder: {
    type: String,
    default: 'Buscar recurso...'
  },
  excludeIds: {
    type: Array,
    default: () => [] 
  }
});

const emit = defineEmits(['resource-selected']);

const resourcesStore = UseResourcesStore();
const searchQuery = ref('');
const showDropdown = ref(false);

const availableResources = computed(() => {
  const list = resourcesStore.resourcesAvailable || resourcesStore.resources;
  if (Array.isArray(list)) return list;
  if (list && typeof list === 'object') return Object.values(list);
  return [];
});

onMounted(async () => {
  console.log('mounted AutocompleteResource');
  await resourcesStore.fetchResourcesAvailable();
});

const filteredResources = computed(() => {
  let resources = availableResources.value;

  // Filtrar recursos ya seleccionados (solo los disponibles que ya fueron elegidos)
  if (props.excludeIds.length > 0) {
    resources = resources.filter(resource => !props.excludeIds.includes(resource.id));
  }

  // Filtrar por búsqueda (por código de equipo)
  if (searchQuery.value) {
    resources = resources.filter((resource) =>
      (resource.code || '')
        .toLowerCase()
        .includes(searchQuery.value.toLowerCase())
    );
  }

  // Ordenar: disponibles primero, ocupados después
  return [...resources].sort((a, b) => {
    if (a.available === b.available) return 0;
    return a.available ? -1 : 1;
  });
});

const handleInput = () => {
  showDropdown.value = true;
};

const selectResource = (resource) => {
  searchQuery.value = '';
  resourcesStore.setSelectedResource(resource.id);
  showDropdown.value = false;
  emit('resource-selected', resource);
};

const handleBlur = () => {
  setTimeout(() => {
    showDropdown.value = false;
  }, 200);
};
</script>
<template>
  <div class="form-control w-full relative">
    <label class="label" v-if="label">
      <span class="label-text">{{ label }}</span>
    </label>
    <input
      type="text"
      v-model="searchQuery"
      @input="handleInput"
      @focus="showDropdown = true"
      @blur="handleBlur"
      :placeholder="placeholder"
      class="input input-bordered w-full"
    />
    <div
      v-if="showDropdown && filteredResources.length > 0"
      class="absolute z-10 w-full mt-1 bg-base-100 shadow-lg rounded-lg max-h-60 overflow-auto top-full"
    >
      <ul class="menu p-0">
        <li
          v-for="resource in filteredResources"
          :key="resource.id"
          @mousedown="resource.available ? selectResource(resource) : null"
        >
          <a
            class="flex items-center justify-between gap-2 py-2 px-3"
            :class="resource.available ? 'hover:bg-base-200 cursor-pointer' : 'opacity-60 cursor-default bg-red-50'"
          >
            <span>{{ resource.display_name || resource.title }}</span>
            <span v-if="resource.available" class="badge badge-sm badge-success">Disponible</span>
            <span v-else class="flex items-center gap-1">
              <span class="badge badge-sm badge-error">Ocupado</span>
              <a
                v-if="resource.assigned_project"
                :href="resource.assigned_project.url"
                class="link link-primary text-xs font-semibold"
                @mousedown.stop
                target="_blank"
              >
                {{ resource.assigned_project.partner_name }}
                <span v-if="resource.assigned_project.location">- {{ resource.assigned_project.location }}</span>
              </a>
            </span>
          </a>
        </li>
      </ul>
    </div>
  </div>
</template>