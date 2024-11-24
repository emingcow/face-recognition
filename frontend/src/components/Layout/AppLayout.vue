<template>
    <el-container class="layout-container">
        <el-aside width="200px" class="sidebar">
            <div class="logo">
                <el-icon>
                    <Monitor />
                </el-icon>
                <span>人脸识别系统</span>
            </div>
            <el-menu :default-active="activeRoute" class="sidebar-menu" router :collapse="false">
                <el-menu-item v-for="route in routes" :key="route.path" :index="route.path">
                    <el-icon>
                        <component :is="route.meta.icon" />
                    </el-icon>
                    <span>{{ route.meta.title }}</span>
                </el-menu-item>
            </el-menu>
        </el-aside>

        <el-container>
            <el-header class="header">
                <div class="header-left">
                    <el-breadcrumb>
                        <el-breadcrumb-item>首页</el-breadcrumb-item>
                        <el-breadcrumb-item>{{ currentRoute?.meta?.title }}</el-breadcrumb-item>
                    </el-breadcrumb>
                </div>
                <div class="header-right">
                    <el-button type="primary" link>
                        <el-icon>
                            <QuestionFilled />
                        </el-icon>
                        帮助
                    </el-button>
                </div>
            </el-header>

            <el-main class="main-content">
                <router-view v-slot="{ Component }">
                    <transition name="fade" mode="out-in">
                        <component :is="Component" />
                    </transition>
                </router-view>
            </el-main>
        </el-container>
    </el-container>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import {
    Monitor,
    QuestionFilled,
    User,
    Search,
    Setting
} from '@element-plus/icons-vue'

const route = useRoute()
const router = useRouter()

const routes = router.options.routes.filter(route => route.meta?.title)
const activeRoute = computed(() => route.path)
const currentRoute = computed(() => routes.find(r => r.path === route.path))
</script>

<style scoped>
.layout-container {
    height: 100vh;
}

.sidebar {
    background: #001529;
    color: white;
    overflow: hidden;
}

.logo {
    height: 60px;
    display: flex;
    align-items: center;
    padding: 0 20px;
    font-size: 18px;
    font-weight: bold;
    background: #002140;
    gap: 10px;
}

.logo .el-icon {
    font-size: 24px;
}

.sidebar-menu {
    border-right: none;
    background: #001529;
}

.header {
    background: white;
    border-bottom: 1px solid #eee;
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0 20px;
}

.main-content {
    background: #f0f2f5;
    padding: 20px;
}

.fade-enter-active,
.fade-leave-active {
    transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
    opacity: 0;
}

:deep(.el-menu) {
    background: #001529 !important;
}

:deep(.el-menu-item) {
    color: #fff !important;
}

:deep(.el-menu-item.is-active) {
    background: #1890ff !important;
}

:deep(.el-menu-item:hover) {
    background: #1890ff !important;
    opacity: 0.8;
}
</style>