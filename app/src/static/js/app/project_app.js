const app = Vue.createApp({
    data(){
        return {
            project: project,
            allEquimpents: free_equipment.map(el=> el),
            projectEquipment: project_equipment,
            CsrfToken: csrf_token,
            deleteUrl: deleteUrl,
            url: urlBase,
            successUrl: successUrl,
            selectedEquipment:[],
            currentEquipment: null,
            currentProjectEquipment: null,
            show_selected: false,
            showAllEquipment: true,
        }
    },
    methods:{
        asignEquipment(item){
            this.showAllEquipment = true;
            this.allEquimpents = this.allEquimpents.map((el)=>{
                if(el.id === item.id){
                    el.is_selected = !item.is_selected;
                    el.start_date = this.project.start_date;
                    el.end_date = this.project.end_date;
                }
                return el;
            });
            this.selectedEquipment = this.allEquimpents.filter(
                el=>el.is_selected
            );

            setTimeout(() => {
                this.show_selected = true;
            }, 200);
        },
        costFormat(value){
            value = parseFloat(value); 
            return value.toFixed(2);
        },
        setEquipment(item){
            this.currentEquipment = item;
            this.showAllEquipment = false;
            console.log(this.currentEquipment);
        },
        isValidItem(item){
            console.log(item);
            if (item.cost_rent === 0 && item.cost_manteinance === 0){
                return true;
            }
            return false;
        },
        sendData(){
            data = {
                'id_project': this.project.id,
                'equipments': this.allEquimpents.filter(
                    el=>el.is_selected
                )
            }
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
                console.log(data);
                if (data.status === 201){
                    this.projectEquipment = this.projectEquipment.filter((itm)=>{
                        console.log(item);
                        console.log(itm);
                        return itm.id_equipment_project !== item.id_equipment_project;
                    });
                }
                })
        },
    },
    mounted() {
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