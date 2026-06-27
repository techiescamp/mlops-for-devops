import axios from 'axios'
import { config } from './config'

const axiosCustomApi = axios.create({
    baseURL: config.ui_url
})

export default axiosCustomApi;