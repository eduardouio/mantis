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
  
  // Filtrar solo recursos disponibles (available === true)
  resources = resources.filter(resource => resource.available === true);
  
  // Filtrar recursos ya seleccionados
  if (props.excludeIds.length > 0) {
    resources = resources.filter(resource => !props.excludeIds.includes(resource.id));
  }
  
  // Filtrar por búsqueda
  if (!searchQuery.value) {
    return resources;
  }
  return resources.filter((resource) =>
    (resource.display_name || resource.title || '')
      .toLowerCase()
      .includes(searchQuery.value.toLowerCase())
  );
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
      <ul class="menu">
        <li
          v-for="resource in filteredResources"
          :key="resource.id"
          @mousedown="selectResource(resource)"
        >
          <a class="hover:bg-base-200">{{ resource.display_name || resource.title }}</a>
        </li>
      </ul>
    </div>
  </div>
</template>