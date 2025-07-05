document.addEventListener('DOMContentLoaded', function() {
    // Verificar si Vue está cargado
    if (typeof Vue === 'undefined') {
        console.error('Vue.js no está cargado. Asegúrate de incluir Vue.js en tu plantilla base.');
        return;
    }

    // Inicializar la aplicación Vue
    const app = Vue.createApp({
        delimiters: ['${', '}'],
        data() {
            return {
                filter: 'all',
                loading: {
                    equipos: true,
                    proyectos: true,
                    tecnicos: true,
                    mantenimientos: true,
                    planillas: true,
                    vehiculos: true
                },
                categories: [
                    { id: 'equipos', label: 'Equipos' },
                    { id: 'proyectos', label: 'Proyectos' },
                    { id: 'tecnicos', label: 'Técnicos' },
                    { id: 'mantenimientos', label: 'Mantenimientos' },
                    { id: 'planillas', label: 'Planillas' },
                    { id: 'vehiculos', label: 'Vehículos' }
                ],
                counters: {
                    equipos: { total: 0, disponibles: 0 },
                    proyectos: { total: 0, activos: 0 },
                    tecnicos: { total: 0, enServicio: 0 },
                    mantenimientos: { total: 0, proyectos: 0 },
                    planillas: { total: 0, pendientes: 0 },
                    vehiculos: { total: 0, enServicio: 0 }
                }
            };
        },
        methods: {
            setFilter(filter) {
                this.filter = filter;
                // Opcional: Guardar la preferencia de filtro en localStorage
                localStorage.setItem('dashboardFilter', filter);
            },
            async fetchData() {
                try {
                    // Simular carga de datos (reemplazar con llamadas reales a tu API)
                    await new Promise(resolve => setTimeout(resolve, 800));
                    
                    // Datos de ejemplo (reemplazar con datos reales de tu API)
                    this.counters = {
                        equipos: { total: 51, disponibles: 13 },
                        proyectos: { total: 5, activos: 5 },
                        tecnicos: { total: 25, enServicio: 10 },
                        mantenimientos: { total: 201, proyectos: 12 },
                        planillas: { total: 25, pendientes: 12 },
                        vehiculos: { total: 14, enServicio: 2 }
                    };
                    
                    // Detener la animación de carga
                    Object.keys(this.loading).forEach(key => {
                        this.loading[key] = false;
                    });
                    
                } catch (error) {
                    console.error('Error al cargar los datos:', error);
                    // Opcional: Mostrar mensaje de error al usuario
                }
            },
            animateCounters() {
                // Agregar animación a los contadores
                const elements = document.querySelectorAll('.animate-count');
                elements.forEach(element => {
                    const target = parseInt(element.textContent);
                    let current = 0;
                    const duration = 1000; // 1 segundo
                    const increment = target / (duration / 16); // 60fps
                    
                    const updateCount = () => {
                        current += increment;
                        if (current < target) {
                            element.textContent = Math.floor(current);
                            requestAnimationFrame(updateCount);
                        } else {
                            element.textContent = target;
                        }
                    };
                    
                    updateCount();
                });
            }
        },
        mounted() {
            // Cargar datos al montar el componente
            this.fetchData();
            
            // Cargar filtro guardado (si existe)
            const savedFilter = localStorage.getItem('dashboardFilter');
            if (savedFilter) {
                this.filter = savedFilter;
            }
            
            // Agregar animación a los contadores cuando los datos estén listos
            this.$nextTick(() => {
                setTimeout(() => {
                    this.animateCounters();
                }, 100);
            });
        }
    });

    // Ocultar loader y montar la aplicación Vue solo si no está ya montada
    const container = document.getElementById('dashboard');
    if (container && !container.__vue_app__) {
        // ocultar loader
        const loader = document.getElementById('page-loader');
        if (loader) loader.style.display = 'none';
        app.mount(container);
    }
});