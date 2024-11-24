<template>
    <div class="face-register">
        <!-- 顶部统计卡片 -->
        <el-row :gutter="20" class="stat-row">
            <el-col :span="8">
                <el-card shadow="hover" class="stat-card">
                    <div class="stat-content">
                        <div class="stat-icon primary">
                            <el-icon>
                                <User />
                            </el-icon>
                        </div>
                        <div class="stat-info">
                            <div class="stat-value animate__animated animate__fadeInUp">256</div>
                            <div class="stat-label">已录入人数</div>
                        </div>
                    </div>
                </el-card>
            </el-col>
            <el-col :span="8">
                <el-card shadow="hover" class="stat-card">
                    <div class="stat-content">
                        <div class="stat-icon success">
                            <el-icon>
                                <Plus />
                            </el-icon>
                        </div>
                        <div class="stat-info">
                            <div class="stat-value animate__animated animate__fadeInUp">15</div>
                            <div class="stat-label">今日新增</div>
                        </div>
                    </div>
                </el-card>
            </el-col>
            <el-col :span="8">
                <el-card shadow="hover" class="stat-card">
                    <div class="stat-content">
                        <div class="stat-icon warning">
                            <el-icon>
                                <DataLine />
                            </el-icon>
                        </div>
                        <div class="stat-info">
                            <div class="stat-value animate__animated animate__fadeInUp">99.9%</div>
                            <div class="stat-label">录入成功率</div>
                        </div>
                    </div>
                </el-card>
            </el-col>
        </el-row>

        <!-- 主要内容区 -->
        <div class="main-content">
            <el-card class="main-card">
                <div class="register-container">

                    <div class="right-section">
                        <!-- 个人信息表单 -->
                        <div class="form-section">
                            <div class="step-hint">
                                <el-tag type="primary" effect="plain">
                                    <el-icon><InfoFilled /></el-icon>
                                    第一步：请输入个人信息
                                </el-tag>
                            </div>

                            <div class="form-header">
                                <h2>个人信息</h2>
                                <el-progress type="circle" :percentage="formProgress" :width="40"></el-progress>
                            </div>

                            <el-form 
                                :model="registerForm" 
                                :rules="formRules" 
                                ref="formRef" 
                                label-position="top"
                            >
                                <el-form-item 
                                    label="姓名" 
                                    prop="name" 
                                    required
                                >
                                    <el-input 
                                        v-model="registerForm.name" 
                                        placeholder="请输入姓名"
                                        @input="updateFormProgress"
                                    >
                                        <template #prefix>
                                            <el-icon><User /></el-icon>
                                        </template>
                                    </el-input>
                                </el-form-item>
                                
                                <el-form-item 
                                    label="工号/学号" 
                                    prop="id" 
                                    required
                                >
                                    <el-input 
                                        v-model="registerForm.id" 
                                        placeholder="请输入工号/学号"
                                        @input="updateFormProgress"
                                    >
                                        <template #prefix>
                                            <el-icon><Document /></el-icon>
                                        </template>
                                    </el-input>
                                </el-form-item>
                            </el-form>
                        </div>

                        <!-- 最近录入记录 -->
                        <div class="recent-records">
                            <div class="section-header">
                                <h3>最近录入</h3>
                                <el-button link type="primary" @click="refreshRecords">
                                    <el-icon>
                                        <Refresh />
                                    </el-icon>
                                </el-button>
                            </div>
                            <el-scrollbar height="150px">
                                <div class="recent-list">
                                    <div v-for="record in recentRecords" :key="record.id"
                                        class="recent-item animate__animated animate__fadeInRight"
                                        :style="{ animationDelay: `${record.index * 0.1}s` }">
                                        <el-avatar :size="32" :src="record.avatar"></el-avatar>
                                        <div class="record-info">
                                            <div class="record-name">{{ record.name }}</div>
                                            <div class="record-time">{{ record.time }}</div>
                                        </div>
                                        <el-tag size="small" type="success">已录入</el-tag>
                                    </div>
                                </div>
                            </el-scrollbar>
                        </div>
                    </div>


                    <!-- 左侧摄像头区域 -->
                    <div class="camera-section">
                        <div class="step-hint img_upload">
                            <el-tag type="success" effect="plain">
                                <el-icon><Camera /></el-icon>
                                第二步：请上传照片
                            </el-tag>
                        </div>

                        <div class="camera-wrapper">
                            <video ref="videoRef" :class="{ 'video-active': isVideoActive }" autoplay></video>
                            <canvas ref="canvasRef" style="display: none;"></canvas>

                            <!-- 人脸检测框 -->
                            <div class="face-detection-frame" v-if="isVideoActive && !capturedImage">
                                <div class="detection-corners"></div>
                                <div class="detection-status">
                                    {{ faceDetected ? '人脸已检测' : '请将人脸对准框内' }}
                                </div>
                            </div>

                            <div class="camera-overlay" v-if="!isVideoActive">
                                <el-upload class="upload-area" drag :auto-upload="false" :show-file-list="false"
                                    :on-change="handleFileChange">
                                    <div class="upload-content animate__animated animate__pulse animate__infinite">
                                        <el-icon class="camera-icon">
                                            <Upload />
                                        </el-icon>
                                        <div class="upload-text">
                                            <h3>点击或拖拽上传图片</h3>
                                            <p>支持 JPG/PNG 格式</p>
                                        </div>
                                    </div>
                                </el-upload>
                            </div>

                            <div class="capture-overlay" v-if="capturedImage">
                                <img :src="capturedImage" alt="已捕获的图像" />
                            </div>
                        </div>

                        <div class="camera-controls">
                            <el-button-group>
                                <el-button type="primary" @click="startCamera"
                                    :class="{ 'pulse-button': !isVideoActive }">
                                    <el-icon>
                                        <VideoCamera />
                                    </el-icon>
                                    开启摄像头
                                </el-button>
                                <el-button type="success" @click="handleRegister" :loading="loading">
                                    <el-icon>
                                        <Upload />
                                    </el-icon>
                                    人脸录入
                                </el-button>
                                <el-button type="danger" :disabled="!isVideoActive" @click="stopCamera">
                                    <el-icon>
                                        <VideoPause />
                                    </el-icon>
                                    关闭摄像头
                                </el-button>
                            </el-button-group>
                        </div>
                    </div>

                    <!-- 右侧内容区域 -->
                    
                </div>
            </el-card>
        </div>

        <!-- 录入成功动画 -->
        <div class="success-animation" v-if="showSuccessAnimation">
            <div class="success-icon animate__animated animate__zoomIn">
                <el-icon>
                    <CircleCheckFilled />
                </el-icon>
            </div>
            <div class="success-message animate__animated animate__fadeInUp">
                录入成功
            </div>
        </div>
    </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, onUnmounted } from 'vue'
import { ElMessage } from 'element-plus'
import {
    VideoCamera,
    VideoPause,
    Upload,
    UserFilled,
    Document,
    User,
    Plus,
    DataLine,
    Refresh,
    CircleCheckFilled,
    InfoFilled,
    Camera
} from '@element-plus/icons-vue'
import axios from 'axios'

// 组件状态
const videoRef = ref<HTMLVideoElement | null>(null)
const canvasRef = ref<HTMLCanvasElement | null>(null)
const isVideoActive = ref(false)
const capturedImage = ref('')
const selectedFile = ref<File | null>(null)
const loading = ref(false)

// 表单数据
const registerForm = reactive({
    name: '',
    id: ''
})

// 添加新的响应式状态
const faceDetected = ref(false)
const formProgress = ref(0)
const showSuccessAnimation = ref(false)
const recentRecords = ref([
    {
        id: 1,
        name: '张三',
        time: '2分钟前',
        avatar: 'https://cube.elemecdn.com/0/88/03b0d39583f48206768a7534e55bcpng.png',
        index: 0
    },
    // ... 更多记录
])

// 添加表单引用
const formRef = ref()

// 添加表单验证规则
const formRules = {
    name: [
        { required: true, message: '请输入姓名', trigger: 'blur' },
        { min: 2, max: 20, message: '长度在 2 到 20 个字符', trigger: 'blur' }
    ],
    id: [
        { required: true, message: '请输入工号/学号', trigger: 'blur' },
        { min: 5, max: 20, message: '长度在 5 到 20 个字符', trigger: 'blur' }
    ]
}

// 文件上传处理
const handleFileChange = (uploadFile: any) => {
    const file = uploadFile.raw || uploadFile
    if (file) {
        selectedFile.value = file
        const reader = new FileReader()
        reader.onload = (e) => {
            capturedImage.value = e.target?.result as string
        }
        reader.readAsDataURL(file)
    }
}

// 开启摄像头
const startCamera = async () => {
    try {
        const stream = await navigator.mediaDevices.getUserMedia({
            video: true,
            audio: false
        })
        if (videoRef.value) {
            videoRef.value.srcObject = stream
            isVideoActive.value = true
            capturedImage.value = ''
            selectedFile.value = null
        }
    } catch (error) {
        ElMessage.error('无法访问摄像头，请确保已授权')
    }
}

// 关闭摄像头
const stopCamera = () => {
    const stream = videoRef.value?.srcObject as MediaStream
    if (stream) {
        stream.getTracks().forEach(track => track.stop())
        if (videoRef.value) {
            videoRef.value.srcObject = null
        }
        isVideoActive.value = false
    }
}

// 捕获图像
const captureImage = () => {
    if (!videoRef.value || !canvasRef.value) return null

    const context = canvasRef.value.getContext('2d')
    if (!context) return null

    canvasRef.value.width = videoRef.value.videoWidth
    canvasRef.value.height = videoRef.value.videoHeight
    context.drawImage(videoRef.value, 0, 0)

    return new Promise<string>((resolve) => {
        canvasRef.value!.toBlob((blob) => {
            if (blob) {
                selectedFile.value = new File([blob], 'capture.jpg', { type: 'image/jpeg' })
                const reader = new FileReader()
                reader.onload = (e) => {
                    capturedImage.value = e.target?.result as string
                    resolve(capturedImage.value)
                }
                reader.readAsDataURL(blob)
            }
        }, 'image/jpeg')
    })
}

// 更新表单进度
const updateFormProgress = () => {
    let progress = 0
    if (registerForm.name) progress += 50
    if (registerForm.id) progress += 50
    formProgress.value = progress
}

// 刷新记录
const refreshRecords = () => {
    recentRecords.value = recentRecords.value.map(record => ({
        ...record,
        index: Math.random()
    }))
}

// 模拟人脸检测
let detectionInterval: number
onMounted(() => {
    detectionInterval = setInterval(() => {
        if (isVideoActive.value && !capturedImage.value) {
            faceDetected.value = Math.random() > 0.3
        }
    }, 500)
})

onUnmounted(() => {
    clearInterval(detectionInterval)
})

// 注册处理
const handleRegister = async () => {
    // 先验证表单
    await formRef.value.validate((valid: boolean) => {
        if (!valid) {
            ElMessage.warning('请填写完整的个人信息')
            return false
        }
    })

    loading.value = true
    try {
        if (!selectedFile.value && !isVideoActive.value) {
            ElMessage.error('请选择图片或使用摄像头拍照')
            return
        }

        if (isVideoActive.value) {
            const imageData = await captureImage()
            if (!imageData) {
                ElMessage.error('图片捕获失败')
                return
            }
        }

        if (!selectedFile.value) {
            ElMessage.error('未获取到图片')
            return
        }

        const formData = new FormData()
        formData.append('name', registerForm.name)
        formData.append('id', registerForm.id)
        formData.append('image', selectedFile.value)

        const response = await axios.post('http://localhost:8001/api/register', formData, {
            headers: {
                'Content-Type': 'multipart/form-data'
            }
        })

        if (response.data.success) {
            showSuccessAnimation.value = true
            setTimeout(() => {
                showSuccessAnimation.value = false
            }, 2000)

            // 添加到最近记录
            recentRecords.value.unshift({
                id: Date.now(),
                name: registerForm.name,
                time: '刚刚',
                avatar: 'https://cube.elemecdn.com/0/88/03b0d39583f48206768a7534e55bcpng.png',
                index: 0
            })

            ElMessage.success('人脸信息录入成功！')
            stopCamera()
            selectedFile.value = null
            capturedImage.value = ''
            registerForm.name = ''
            registerForm.id = ''
        } else {
            ElMessage.error(response.data.message || '录入失败，请重试')
        }
    } catch (error: any) {
        console.error('Registration error:', error)
        ElMessage.error(error.response?.data?.message || '服务器错误，请稍后重试')
    } finally {
        loading.value = false
    }
}
</script>

<style scoped>

.img_upload {
    margin-top: 12px;
}

.register-container {
    display: grid;
    grid-template-columns: 2fr 1fr;
    gap: 12px;
    padding: 12px;
    height: calc(64vh);
}

.camera-section {
    display: flex;
    flex-direction: column;
    gap: 10px;
    height: 100%;
}

.camera-wrapper {
    position: relative;
    aspect-ratio: 16/9;
    background: #f5f7fa;
    border-radius: 8px;
    overflow: hidden;
    box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
    height: calc(100% - 80px);
}

.camera-overlay {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    display: flex;
    align-items: center;
    justify-content: center;
}

.upload-content {
    text-align: center;
}

.camera-icon {
    font-size: 48px;
    margin-bottom: 16px;
    color: #909399;
}

.upload-text h3 {
    margin: 10px 0;
    color: #606266;
}

.upload-text p {
    color: #909399;
}

.video-active {
    width: 100%;
    height: 100%;
    object-fit: cover;
}

.capture-overlay {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    display: flex;
    align-items: center;
    justify-content: center;
}

.capture-overlay img {
    width: 100%;
    height: 100%;
    object-fit: contain;
    background: #f5f7fa;
    padding: 10px;
}

.camera-controls {
    display: flex;
    justify-content: center;
    gap: 16px;
}

.form-section {
    flex: 0.7;
    min-height: 250px;
    padding: 12px;
    background: #fff;
    border-radius: 8px;
    box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
    overflow: auto;
}

.form-section h2 {
    margin-bottom: 10px;
    color: #303133;
}

:deep(.el-upload-dragger) {
    width: 100%;
    height: 100%;
    background: transparent;
    border: none;
    display: flex;
    align-items: center;
    justify-content: center;
}

:deep(.el-upload-dragger:hover) {
    background: rgba(255, 255, 255, 0.1);
}

.stat-row {
    margin-bottom: 20px;
}

.stat-card {
    transition: all 0.3s ease;
}

.stat-card:hover {
    transform: translateY(-5px);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.stat-content {
    display: flex;
    align-items: center;
    gap: 16px;
    /* padding: 20px; */
}

.stat-icon {
    width: 48px;
    height: 48px;
    border-radius: 8px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 24px;
}

.stat-icon.primary {
    background: #ecf5ff;
    color: #409eff;
}

.stat-icon.success {
    background: #f0f9eb;
    color: #67c23a;
}

.stat-icon.warning {
    background: #fdf6ec;
    color: #e6a23c;
}

.face-detection-frame {
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    width: 200px;
    height: 200px;
    border: 2px solid #409EFF;
    border-radius: 8px;
    animation: scan 2s infinite;
}

@keyframes scan {
    0% {
        border-color: #409EFF;
        box-shadow: 0 0 0 0 rgba(64, 158, 255, 0.4);
    }

    50% {
        border-color: #67C23A;
        box-shadow: 0 0 0 10px rgba(64, 158, 255, 0);
    }

    100% {
        border-color: #409EFF;
        box-shadow: 0 0 0 0 rgba(64, 158, 255, 0);
    }
}

.detection-status {
    position: absolute;
    bottom: -30px;
    left: 50%;
    transform: translateX(-50%);
    background: rgba(0, 0, 0, 0.7);
    color: white;
    padding: 4px 12px;
    border-radius: 4px;
    font-size: 14px;
}

.form-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
}

:deep(.el-form-item) {
    margin-bottom: 12px;
}

.recent-card {
    margin-top: 20px;
}

.recent-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.recent-list {
    display: flex;
    flex-direction: column;
    gap: 12px;
}

.recent-item {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 8px;
    border-radius: 8px;
    transition: all 0.3s ease;
}

.recent-item:hover {
    background: #f5f7fa;
    transform: translateX(5px);
}

.record-info {
    flex: 1;
}

.record-name {
    font-weight: bold;
    margin-bottom: 4px;
}

.record-time {
    font-size: 12px;
    color: #909399;
}

.success-animation {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(0, 0, 0, 0.8);
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    z-index: 9999;
}

.success-icon {
    font-size: 80px;
    color: #67C23A;
    margin-bottom: 20px;
}

.success-message {
    font-size: 24px;
    color: white;
}

.pulse-button {
    animation: pulse 2s infinite;
}

@keyframes pulse {
    0% {
        box-shadow: 0 0 0 0 rgba(64, 158, 255, 0.4);
    }

    70% {
        box-shadow: 0 0 0 10px rgba(64, 158, 255, 0);
    }

    100% {
        box-shadow: 0 0 0 0 rgba(64, 158, 255, 0);
    }
}

.right-section {
    display: flex;
    flex-direction: column;
    gap: 16px;
    height: 100%;
}

.recent-records {
    flex: 1;
    padding: 16px;
    background: #fff;
    border-radius: 8px;
    box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
    display: flex;
    flex-direction: column;
    overflow: hidden;
    min-height: 150px;
}

.recent-records .el-scrollbar {
    flex: 1;
    height: auto !important;
    overflow-y: auto;
}

.section-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 12px;
    flex-shrink: 0;
}

.section-header h3 {
    margin: 0;
    font-size: 16px;
    color: #303133;
}

.step-hint {
    margin-bottom: 10px;
}

.step-hint .el-tag {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 8px 12px;
    font-size: 14px;
}

.form-section {
    position: relative;
}

.camera-section {
    position: relative;
}
</style>