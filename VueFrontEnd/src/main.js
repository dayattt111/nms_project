import './assets/main.css'

import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import axios from 'axios'

// Setup axios defaults
axios.defaults.baseURL = 'http://localhost:5000/api'

const app = createApp(App)

app.use(router)

app.mount('#app')
