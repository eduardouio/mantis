// Seteo inicial de la aplicacion
var free_equipment = free_equipment.map((itm) => {
    return {
        id: itm.pk,
        ...itm.fields
    }
});

var project_resource = project_resource.map((itm) => {
   let resourseItem = JSON.parse(itm.resourse_item);
   let projectResource = JSON.parse(itm.project_resource);
   
   resourseItem = resourseItem.map((i)=>{
      return {
         id: i.pk,
         ...i.fields
      }
   });
   projectResource = projectResource.map((i)=>{
      return {
         id: i.pk,
         ...i.fields
      }
   });
    return {
      resourceItem : resourseItem[0],
      projectResource : projectResource[0],
      is_selected: false,
    }
});

var project = project.map((itm) => {
    return {
        id: itm.pk,
        is_selected: false,
        ...itm.fields
    }
})[0];


// Creacion de la aplicacion
const app = Vue.createApp({
    data(){
        return {
            project: project,
            allEquimpents: free_equipment.map(el=> el),
            projectEquipment: project_resource,
            filteredAllEquipment: [],
            filteredProjectEquipment: [],
            CsrfToken: csrf_token,
            deleteUrl: deleteUrl,
            updateUrl: updateUrl,
            url: urlBase,
            successUrl: successUrl,
            selectedEquipment:null,
            currentEquipment: null,
            currentProjectEquipment: null,
            show_selected: false,
            showAllEquipment: true,
            showLoader: true,
            queryFilterFree: '',
            queryFilterProject: '',
            tabClass: {
                'active': 'nav-link bg-gray bg-gradient border rounded-1',
                'inactive': 'nav-link link-dark',
            },
            tab_show: {
                tab_detail: true,
                tab_equipments: false,
                tab_work_order: false,
            }
        }
    },
    methods:{
        showTab(tab){
            this.tab_show = {
                tab_detail: false,
                tab_equipments: false,
                tab_work_order: false,
            }
            this.tab_show[tab] = true;
           
        },
        asignEquipment(item){
            const newItem = {
                resourceItem : item,
                projectResource : {
                    id: 0,
                    notes: '',
                    is_active: true,
                    project: this.project.id,
                    resource_item: item.id,
                    cost: 0.0,
                    cost_manteinance:0.0,
                    mantenance_frequency: 'SEMANAL',
                    times_mantenance: 1,
                    start_date: this.project.start_date,
                    end_date: this.project.end_date,
                },
                is_selected: false,
            }
            
            this.allEquimpents = this.allEquimpents.filter(
                el=>el.id !== item.id
            );
            this.projectEquipment.push(newItem);
            this.sendData(newItem);
            // completamos los arreglo filtrados
            this.filteredAllEquipment = this.allEquimpents.map(el=>el);
            this.filteredProjectEquipment = this.projectEquipment.map(el=>el);
        },
        removeEquipment(item){
            this.projectEquipment = this.projectEquipment.filter(
                el => el.resourceItem.id !== item.resourceItem.id
            );
            this.allEquimpents.push(item.resourceItem);

            // completamos los arreglo filtrados
            this.filteredAllEquipment = this.allEquimpents.map(el=>el);
            this.filteredProjectEquipment = this.projectEquipment.map(el=>el);
        },
        filterFreeEquipment(){
            if (this.queryFilterFree === ''){
                this.filteredAllEquipment = this.allEquimpents.map(el=>el);
                return;
            }
            // filter by name and code
            this.filteredAllEquipment = this.allEquimpents.filter(
                el => el.name.toLowerCase().includes(this.queryFilterFree.toLowerCase()) 
                || 
                el.code.toLowerCase().includes(this.queryFilterFree.toLowerCase())
            );
        },
        filterProjectEquipments(){
            if (this.queryFilterProject === ''){
                this.filteredProjectEquipment = this.projectEquipment.map(el=>el);
                return;
            }
            // filter by name and code
            this.filteredProjectEquipment = this.projectEquipment.filter(
                el => el.resourceItem.name.toLowerCase().includes(this.queryFilterProject.toLowerCase()) 
                || 
                el.resourceItem.code.toLowerCase().includes(this.queryFilterProject.toLowerCase())
            );
        },
        costFormat(value){
            if (value === '' || value === null || value === 0){
                return '0.00';
            }
            value = parseFloat(value); 
            return value.toFixed(2);
        },
        isValidItem(item){
            if (item.cost_rent === 0 && item.cost_manteinance === 0){
                return true;
            }
            return false;
        },
        sendData(newItem){

            data = {
                'id_project': this.project.id,
                ...newItem.projectResource
            }

            console.log(data);
            return;
            fetch(this.url,{
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.CsrfToken,
                },
                body: JSON.stringify(data)
            }).then(
                response => response.json())
            .then(data => {
                console.log(data);
                if (data.status === 201){
                    window.location.reload();
                }
            })
            .catch(error => {
                alert("Ocurrio un error al enviar los datos");
                console.error('Error:', error);
            })
        },
        deleteEquipment(item){
            if (!item.confirm_delete){
                item.confirm_delete = true;
                return;
            }

            fetch(this.deleteUrl,{
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.CsrfToken,
                },
                body: JSON.stringify(item)
            }).then(
                response => response.json()
            ).then((data) => {
                if (data.status === 201){
                    this.projectEquipment = this.projectEquipment.filter((itm)=>{
                        return itm.id_equipment_project !== item.id_equipment_project;
                    });
                }
                })
        },
        updateProjectEquipment(item){
            console.log(item);
            return;
            fetch(this.updateUrl,{
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.CsrfToken,
                },
                body: JSON.stringify(this.currentProjectEquipment)
            }).then(
                response => response.json()
            ).then((data) => {
                if (data.status === 201){
                    this.projectEquipment = this.projectEquipment.map((itm)=>{
                        if (itm.id_equipment_project === this.currentProjectEquipment.id_equipment_project){
                            itm = this.currentProjectEquipment;
                        }
                        return itm;
                    });
                }
            }).catch(error => {
                alert("Ocurrio un error al enviar los datos");
                console.error('Error:', error);
            });
        },
        formatDate(date){
            if (!date){
                return '';
            }
            const myDate = new Date(date);
            const day = String(myDate.getDate()).padStart(2, '0');
            const month = String(myDate.getMonth() + 1).padStart(2, '0');
            const year = myDate.getFullYear();
            const strDate = `${day}/${month}/${year}`;
            return strDate;
        },
    },
    mounted() {
        console.log('vue app mounted');
        this.showLoader = false;
        this.filteredAllEquipment = this.allEquimpents.map(el=>el);
        this.filteredProjectEquipment = this.projectEquipment.map(el=>el);
    },
    computed: {
       ceroExist(){
           have_cero = this.selectedEquipment.filter(
               el=>el.cost_rent === 0 && el.cost_manteinance === 0 
           );
            return have_cero.length > 0;
       }
    },
});
app.config.compilerOptions.delimiters = ['[[', ']]'];
const vm = app.mount('#app');