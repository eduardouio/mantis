const app = Vue.createApp({
    data(){
        return {
            technicals: technicals,
            vehicles: vehicles,
            url : url_update,
            csrftoken: csrf_token,
            parnerId: partner_id,
        }
    },
    methods:{
        saveItem(item, type){
            item.is_registered = !item.is_registered
            const action = item.is_registered ? 'add' : 'remove'
            let data = {
                'partner_id': this.parnerId,
                'type': type,
                'action': action,
                ...item

            }
            fetch(this.url, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.csrftoken,
                },
                body: JSON.stringify(data)
            })
        }
    },
    mounted() {
        console.dir(technicals)
    },
    computed:{
        
    },  
})

app.config.compilerOptions.delimiters = ['[[', ']]'];
const vm = app.mount('#app');
