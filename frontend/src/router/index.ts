import { createRouter, createWebHistory } from 'vue-router'
import FaceRegister from '../views/FaceRegister.vue'
import FaceRecognition from '../views/FaceRecognition.vue'
import SecurityMonitor from '../views/SecurityMonitor.vue'
import AccessControl from '../views/AccessControl.vue'
import RegisterHistory from '../views/RegisterHistory.vue'

const routes = [
    {
        path: '/',
        redirect: '/register'
    },
    {
        path: '/register',
        name: 'FaceRegister',
        component: FaceRegister,
        meta: {
            title: '人脸信息录入',
            icon: 'User'
        }
    },
    {
        path: '/recognition',
        name: 'FaceRecognition',
        component: FaceRecognition,
        meta: {
            title: '身份识别',
            icon: 'Search'
        }
    },
    // {
    //     path: '/monitor',
    //     name: 'SecurityMonitor',
    //     component: SecurityMonitor,
    //     meta: {
    //         title: '安防监控',
    //         icon: 'VideoCamera'
    //     }
    // },
    // {
    //     path: '/access',
    //     name: 'AccessControl',
    //     component: AccessControl,
    //     meta: {
    //         title: '门禁管理',
    //         icon: 'Lock'
    //     }
    // },
    {
        path: '/register-history',
        name: 'RegisterHistory',
        component: RegisterHistory,
        meta: {
            title: '录入历史',
            icon: 'Timer'
        }
    }
]

const router = createRouter({
    history: createWebHistory(),
    routes
})

export default router 