import axios from 'axios'
import { config } from './config'

const axiosCustomApi = axios.create({
    baseURL: config.ui_url || 'http://localhost:8000'
})

export default axiosCustomApi;