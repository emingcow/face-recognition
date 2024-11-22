<template>
    <div class="security-monitor">
        <!-- 顶部统计卡片 -->
        <el-row :gutter="20" class="stat-row">
            <el-col :span="6">
                <el-card shadow="hover" class="stat-card">
                    <div class="stat-content">
                        <div class="stat-icon warning">
                            <el-icon>
                                <Warning />
                            </el-icon>
                        </div>
                        <div class="stat-info">
                            <div class="stat-value">{{ todayAlerts }}</div>
                            <div class="stat-label">今日警报</div>
                        </div>
                    </div>
                </el-card>
            </el-col>
            <el-col :span="6">
                <el-card shadow="hover" class="stat-card">
                    <div class="stat-content">
                        <div class="stat-icon success">
                            <el-icon>
                                <VideoCamera />
                            </el-icon>
                        </div>
                        <div class="stat-info">
                            <div class="stat-value">{{ onlineCameras }}/{{ totalCameras }}</div>
                            <div class="stat-label">在线摄像头</div>
                        </div>
                    </div>
                </el-card>
            </el-col>
            <el-col :span="6">
                <el-card shadow="hover" class="stat-card">
                    <div class="stat-content">
                        <div class="stat-icon primary">
                            <el-icon>
                                <Location />
                            </el-icon>
                        </div>
                        <div class="stat-info">
                            <div class="stat-value">{{ activeAreas }}</div>
                            <div class="stat-label">活动区域</div>
                        </div>
                    </div>
                </el-card>
            </el-col>
            <el-col :span="6">
                <el-card shadow="hover" class="stat-card">
                    <div class="stat-content">
                        <div class="stat-icon info">
                            <el-icon>
                                <Timer />
                            </el-icon>
                        </div>
                        <div class="stat-info">
                            <div class="stat-value">{{ uptime }}</div>
                            <div class="stat-label">系统运行时间</div>
                        </div>
                    </div>
                </el-card>
            </el-col>
        </el-row>

        <!-- 主要内容区 -->
        <div class="monitor-content">
            <!-- 左侧摄像头网格 -->
            <div class="camera-section">
                <div class="section-header">
                    <div class="header-left">
                        <h2>实时监控</h2>
                    </div>
                    <div class="header-right">
                        <el-button type="primary" size="small" @click="refreshCameras">
                            <el-icon>
                                <Refresh />
                            </el-icon>
                            刷新
                        </el-button>
                    </div>
                </div>

                <div class="camera-grid">
                    <el-card v-for="camera in cameras" :key="camera.id" class="camera-card"
                        :class="{ 'alert': camera.alert }">
                        <div class="camera-header">
                            <span class="camera-name">
                                <el-icon>
                                    <VideoCamera />
                                </el-icon>
                                {{ camera.name }}
                            </span>
                            <el-tag :type="camera.status === 'online' ? 'success' : 'danger'" size="small">
                                {{ camera.status === 'online' ? '在线' : '离线' }}
                            </el-tag>
                        </div>
                        <div class="camera-feed">
                            <video :ref="'video-' + camera.id" autoplay loop muted
                                :class="{ 'alert-flash': camera.alert }">
                                <source :src="camera.stream" type="video/mp4">
                            </video>
                            <div class="camera-overlay" v-if="camera.alert">
                                <el-icon class="alert-icon">
                                    <Warning />
                                </el-icon>
                                <span class="alert-text">检测到异常行为</span>
                            </div>
                            <div class="camera-controls">
                                <el-button-group>
                                    <el-button type="primary" circle @click="toggleFullscreen(camera)">
                                        <el-icon>
                                            <FullScreen />
                                        </el-icon>
                                    </el-button>
                                    <el-button type="warning" circle @click="showPlayback(camera)">
                                        <el-icon>
                                            <VideoPlay />
                                        </el-icon>
                                    </el-button>
                                    <el-button type="danger" circle @click="handleEmergency(camera)">
                                        <el-icon>
                                            <AlarmClock />
                                        </el-icon>
                                    </el-button>
                                </el-button-group>
                            </div>
                        </div>
                    </el-card>
                </div>
            </div>

            <!-- 右侧警报面板 -->
            <div class="alert-section">
                <el-card class="alert-card">
                    <template #header>
                        <div class="alert-header">
                            <div class="header-title">
                                <el-icon>
                                    <Warning />
                                </el-icon>
                                实时警报
                            </div>
                            <el-tag type="danger" effect="dark" v-if="activeAlerts.length">
                                {{ activeAlerts.length }}个活动警报
                            </el-tag>
                        </div>
                    </template>

                    <el-tabs>
                        <el-tab-pane label="实时警报">
                            <el-scrollbar height="calc(100vh - 400px)">
                                <div class="alert-list">
                                    <div v-for="alert in activeAlerts" :key="alert.id" class="alert-item"
                                        :class="alert.level">
                                        <div class="alert-time">{{ alert.time }}</div>
                                        <div class="alert-content">
                                            <el-icon class="alert-icon">
                                                <Warning />
                                            </el-icon>
                                            <span>{{ alert.message }}</span>
                                        </div>
                                        <div class="alert-location">
                                            <el-icon>
                                                <Location />
                                            </el-icon>
                                            {{ alert.location }}
                                        </div>
                                        <div class="alert-actions">
                                            <el-button-group>
                                                <el-button type="primary" size="small" @click="handleAlert(alert)">
                                                    处理
                                                </el-button>
                                                <el-button type="info" size="small" @click="ignoreAlert(alert)">
                                                    忽略
                                                </el-button>
                                            </el-button-group>
                                        </div>
                                    </div>
                                </div>
                            </el-scrollbar>
                        </el-tab-pane>
                        <el-tab-pane label="历史记录">
                            <el-timeline>
                                <el-timeline-item v-for="record in alertHistory" :key="record.id" :type="record.status"
                                    :timestamp="record.time">
                                    {{ record.message }}
                                </el-timeline-item>
                            </el-timeline>
                        </el-tab-pane>
                    </el-tabs>
                </el-card>
            </div>
        </div>

        <!-- 全屏摄像头对话框 -->
        <el-dialog v-model="fullscreenDialog" :title="selectedCamera?.name" width="90%" :fullscreen="true"
            custom-class="camera-dialog" destroy-on-close>
            <div class="fullscreen-camera">
                <video ref="fullscreenVideo" autoplay loop muted>
                    <source :src="selectedCamera?.stream" type="video/mp4">
                </video>
                <div class="fullscreen-controls">
                    <el-button-group>
                        <el-button type="warning" @click="showPlayback(selectedCamera)">
                            <el-icon>
                                <VideoPlay />
                            </el-icon>
                            回放
                        </el-button>
                        <el-button type="danger" @click="handleEmergency(selectedCamera)">
                            <el-icon>
                                <AlarmClock />
                            </el-icon>
                            报警
                        </el-button>
                    </el-button-group>
                </div>
            </div>
        </el-dialog>
    </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import {
    Warning,
    FullScreen,
    VideoPlay,
    AlarmClock,
    VideoCamera,
    Location,
    Timer
} from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

// 摄像头数据
interface Camera {
    id: string
    name: string
    status: 'online' | 'offline'
    stream: string
    alert: boolean
}

// 警报数据
interface Alert {
    id: string
    level: 'warning' | 'danger'
    message: string
    time: string
    location: string
}

// 模拟摄像头数据
const cameras = ref<Camera[]>([
    {
        id: 'cam1',
        name: '前门监控',
        status: 'online',
        stream: '/video/stream1.mp4',
        alert: false
    },
    {
        id: 'cam2',
        name: '后门监控',
        status: 'online',
        stream: '/video/stream2.mp4',
        alert: true
    },
    {
        id: 'cam3',
        name: '大厅监控',
        status: 'offline',
        stream: '/video/stream3.mp4',
        alert: false
    },
    {
        id: 'cam4',
        name: '停车场监控',
        status: 'online',
        stream: '/video/stream4.mp4',
        alert: false
    }
])

// 活动警报
const activeAlerts = ref<Alert[]>([
    {
        id: 'alert1',
        level: 'warning',
        message: '检测到可疑人员聚集',
        time: '2分钟前',
        location: '前门区域'
    },
    {
        id: 'alert2',
        level: 'danger',
        message: '检测到未授权进入',
        time: '5分钟前',
        location: '后门区域'
    }
])

// 统计数据
const todayAlerts = ref(15)
const onlineCameras = ref(3)
const totalCameras = ref(4)
const activeAreas = ref(8)

// 全屏对话框控制
const fullscreenDialog = ref(false)
const selectedCamera = ref<Camera | null>(null)

// 处理全屏显示
const toggleFullscreen = (camera: Camera) => {
    selectedCamera.value = camera
    fullscreenDialog.value = true
}

// 显示回放
const showPlayback = (camera: Camera) => {
    ElMessage.info(`正在加载 ${camera.name} 的回放记录...`)
}

// 处理紧急情况
const handleEmergency = (camera: Camera) => {
    ElMessage.warning(`已发送紧急警报：${camera.name}`)
}

// 处理警报
const handleAlert = (alert: Alert) => {
    ElMessage.success(`正在处理警报：${alert.message}`)
    // 从活动警报中移除
    activeAlerts.value = activeAlerts.value.filter(a => a.id !== alert.id)
}

// 忽略警报
const ignoreAlert = (alert: Alert) => {
    ElMessage.info(`已忽略警报：${alert.message}`)
    // 从活动警报中移除
    activeAlerts.value = activeAlerts.value.filter(a => a.id !== alert.id)
}

// 模拟实时更新
setInterval(() => {
    // 随机更新摄像头状态
    cameras.value.forEach(camera => {
        if (Math.random() > 0.95) {
            camera.alert = !camera.alert
            if (camera.alert) {
                activeAlerts.value.unshift({
                    id: `alert${Date.now()}`,
                    level: Math.random() > 0.5 ? 'warning' : 'danger',
                    message: '检测到异常行为',
                    time: '刚刚',
                    location: camera.name
                })
            }
        }
    })
}, 5000)
</script>

<style scoped>
.security-monitor {
    padding: 20px;
    height: calc(100vh - 84px);
    display: flex;
    flex-direction: column;
    gap: 20px;
}

.stat-row {
    margin-bottom: 12px;
}

.stat-card {
    height: 100px;
    margin-bottom: 16px;
    transition: all 0.3s ease;
}

.stat-card:hover {
    transform: translateY(-5px);
}

.stat-content {
    padding: 12px;
    display: flex;
    align-items: center;
    gap: 16px;
}

.stat-icon {
    width: 40px;
    height: 40px;
    border-radius: 8px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 20px;
}

.stat-icon.warning {
    background: #fef9e7;
    color: #e6a23c;
}

.stat-icon.success {
    background: #f0f9eb;
    color: #67c23a;
}

.stat-icon.primary {
    background: #ecf5ff;
    color: #409eff;
}

.stat-icon.info {
    background: #f4f4f5;
    color: #909399;
}

.stat-info {
    flex: 1;
}

.stat-value {
    font-size: 20px;
    font-weight: bold;
    color: #303133;
    line-height: 1;
    margin-bottom: 2px;
}

.stat-label {
    font-size: 12px;
    color: #909399;
}

.monitor-content {
    display: flex;
    gap: 16px;
    height: calc(100vh - 140px);
}

.camera-section {
    flex: 1;
    display: flex;
    flex-direction: column;
    gap: 16px;
    min-width: 0;
}

.section-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 12px;
}

.header-left {
    display: flex;
    align-items: center;
    gap: 8px;
}

.header-left h2 {
    font-size: 16px;
    margin: 0;
}

.header-right {
    display: flex;
    align-items: center;
    gap: 8px;
}

.camera-grid {
    flex: 1;
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    grid-template-rows: repeat(2, minmax(350px, 450px));
    gap: 16px;
    overflow: auto;
}

.camera-card {
    transition: all 0.3s ease;
    height: 100%;
    display: flex;
    flex-direction: column;
}

.camera-card:hover {
    transform: scale(1.02);
}

.camera-card.alert {
    border: 2px solid #f56c6c;
}

.camera-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 8px;
}

.camera-name {
    display: flex;
    align-items: center;
    gap: 4px;
}

.camera-feed {
    position: relative;
    flex: 1;
    min-height: 350px;
    max-height: 450px;
    background: #000;
    border-radius: 4px;
    overflow: hidden;
}

.camera-feed video {
    width: 100%;
    height: 100%;
    object-fit: cover;
}

.camera-overlay {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: rgba(245, 108, 108, 0.2);
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    color: #fff;
}

.camera-controls {
    position: absolute;
    bottom: 8px;
    left: 50%;
    transform: translateX(-50%);
    z-index: 10;
    opacity: 0;
    transition: opacity 0.3s;
}

.camera-feed:hover .camera-controls {
    opacity: 1;
}

.camera-controls .el-button {
    padding: 6px;
}

.alert-section {
    width: 350px;
    display: flex;
    flex-direction: column;
    position: relative;
}

.alert-card {
    height: calc(100vh - 280px);
    display: flex;
    flex-direction: column;
}

.alert-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.header-title {
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 16px;
    font-weight: bold;
}

.alert-list {
    display: flex;
    flex-direction: column;
    gap: 8px;
}

.alert-item {
    padding: 8px;
    border-radius: 8px;
    background: #f5f7fa;
    transition: all 0.3s;
    font-size: 12px;
}

.alert-item:hover {
    transform: translateX(5px);
}

.alert-item.warning {
    border-left: 4px solid #e6a23c;
}

.alert-item.danger {
    border-left: 4px solid #f56c6c;
}

.alert-time {
    font-size: 12px;
    color: #909399;
    margin-bottom: 4px;
}

.alert-content {
    display: flex;
    align-items: center;
    gap: 8px;
    margin-bottom: 4px;
}

.alert-location {
    display: flex;
    align-items: center;
    gap: 4px;
    font-size: 12px;
    color: #606266;
    margin-bottom: 8px;
}

.alert-actions {
    display: flex;
    justify-content: flex-end;
}

.fullscreen-camera {
    height: calc(100vh - 100px);
    position: relative;
    width: 100%;
}

.fullscreen-camera video {
    width: 100%;
    height: 100%;
    object-fit: contain;
    background: #000;
}

.fullscreen-controls {
    bottom: 16px;
    left: 50%;
    padding: 12px;
    background: rgba(0, 0, 0, 0.5);
    border-radius: 8px;
    position: absolute;
    transform: translateX(-50%);
}

/* 动画效果 */
.alert-flash {
    animation: flash 2s infinite;
}

@keyframes flash {

    0%,
    100% {
        opacity: 1;
    }

    50% {
        opacity: 0.5;
    }
}

@media screen and (max-width: 1400px) {
    .stat-row {
        margin-bottom: 12px;
    }

    .stat-card {
        height: 80px;
    }

    .camera-grid {
        height: calc(100vh - 250px);
    }

    .alert-card {
        height: calc(100vh - 250px);
    }
}

@media screen and (max-width: 1200px) {
    .monitor-content {
        flex-direction: column;
    }

    .alert-section {
        width: 100%;
        height: 300px;
    }

    .alert-card {
        height: 100%;
    }
}
</style>