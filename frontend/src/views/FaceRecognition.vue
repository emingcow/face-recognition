<template>
    <div class="face-recognition">
        <!-- 顶部统计卡片 -->
        <el-row :gutter="20" class="stat-row">
            <el-col :span="8">
                <el-card shadow="hover" class="stat-card">
                    <div class="stat-content">
                        <div class="stat-icon primary animate__animated animate__bounceIn">
                            <el-icon>
                                <User />
                            </el-icon>
                        </div>
                        <div class="stat-info">
                            <div class="stat-value animate__animated animate__fadeInUp">128</div>
                            <div class="stat-label">今日访问人数</div>
                        </div>
                    </div>
                </el-card>
            </el-col>
            <el-col :span="8">
                <el-card shadow="hover" class="stat-card">
                    <div class="stat-content">
                        <div class="stat-icon success animate__animated animate__bounceIn"
                            style="animation-delay: 0.2s">
                            <el-icon>
                                <EyeIcon />
                            </el-icon>
                        </div>
                        <div class="stat-info">
                            <div class="stat-value animate__animated animate__fadeInUp" style="animation-delay: 0.2s">
                                1,234</div>
                            <div class="stat-label">识别总次数</div>
                        </div>
                    </div>
                </el-card>
            </el-col>
            <el-col :span="8">
                <el-card shadow="hover" class="stat-card">
                    <div class="stat-content">
                        <div class="stat-icon warning animate__animated animate__bounceIn"
                            style="animation-delay: 0.4s">
                            <el-icon>
                                <DataTrend />
                            </el-icon>
                        </div>
                        <div class="stat-info">
                            <div class="stat-value animate__animated animate__fadeInUp" style="animation-delay: 0.4s">
                                99.9%</div>
                            <div class="stat-label">识别准确率</div>
                        </div>
                    </div>
                </el-card>
            </el-col>
        </el-row>

        <!-- 主要内容区 -->
        <el-card class="main-card">
            <div class="recognition-container">
                <!-- 左侧摄像头区域 -->
                <div class="camera-section">
                    <div class="camera-container">
                        <video ref="videoRef" :class="{ 'video-active': isVideoActive }" autoplay></video>
                        <canvas ref="canvasRef" style="display: none;"></canvas>

                        <div class="camera-overlay" v-if="!isVideoActive && !capturedImage">
                            <el-upload class="upload-area" drag :auto-upload="false" :show-file-list="false"
                                :on-change="handleFileChange">
                                <div class="upload-content">
                                    <el-icon class="camera-icon">
                                        <Upload />
                                    </el-icon>
                                    <div class="upload-text">
                                        <h3>点击或拖拽上传图片</h3>
                                        <p>支持 JPG/PNG 格</p>
                                    </div>
                                </div>
                            </el-upload>
                        </div>

                        <div class="capture-overlay" v-if="capturedImage">
                            <img :src="capturedImage" alt="已捕获的图像" />
                        </div>

                        <!-- 识别结果展示 -->
                        <div class="result-overlay animate__animated animate__fadeIn" v-if="recognitionResult">
                            <el-result 
                                :icon="recognitionResult.success ? 'success' : 'error'"
                                :title="recognitionResult.success ? '识别成功' : '识别失败'"
                                :sub-title="recognitionResult.message"
                            >
                            </el-result>
                            
                            <!-- 添加烟花效果 -->
                            <div class="fireworks" v-if="recognitionResult.success">
                                <div class="firework"></div>
                                <div class="firework"></div>
                                <div class="firework"></div>
                            </div>
                        </div>

                        <!-- 添加人脸检测框动画 -->
                        <div class="face-detection-frame" 
                             v-if="isVideoActive" 
                             :class="{ 'face-detected': faceDetected }">
                        </div>
                    </div>

                    <div class="button-controls">
                        <el-button-group>
                            <el-button 
                                type="primary" 
                                @click="startCamera" 
                                :disabled="isModelLoading || isVideoActive"
                                :loading="isModelLoading"
                            >
                                <el-icon><VideoCamera /></el-icon>
                                开启摄像头
                            </el-button>
                            <el-button 
                                type="danger" 
                                @click="stopCamera" 
                                :disabled="!isVideoActive"
                            >
                                <el-icon><VideoPause /></el-icon>
                                关闭摄像头
                            </el-button>
                            
                            <!-- 识别和上传按钮 - 只在摄像头关闭且有图片时显示 -->
                            <template v-if="!isVideoActive">
                                <el-button 
                                    type="success" 
                                    @click="startRecognition" 
                                    :loading="loading"
                                    :disabled="!capturedImage"
                                >
                                    <el-icon><Search /></el-icon>
                                    开始识别
                                </el-button>
                                <el-button 
                                    @click="resetUpload"
                                    :disabled="!capturedImage"
                                >
                                    <el-icon><RefreshLeft /></el-icon>
                                    重新上传
                                </el-button>
                            </template>
                        </el-button-group>
                    </div>
                </div>

                <!-- 右侧识别记录 -->
                <div class="recognition-history">
                    <div class="section-header">
                        <h2>
                            <el-icon>
                                <Clock />
                            </el-icon>
                            识别记录
                        </h2>
                    </div>
                    <el-scrollbar height="400px">
                        <el-timeline>
                            <el-timeline-item v-for="(record, index) in recognitionHistory" :key="index"
                                :type="record.success ? 'success' : 'danger'" :timestamp="record.time" :hollow="true">
                                <div class="history-item">
                                    <el-tag :type="record.success ? 'success' : 'danger'" size="small">
                                        {{ record.success ? '识别成功' : '识别失败' }}
                                    </el-tag>
                                    <span class="history-message">{{ record.message }}</span>
                                </div>
                            </el-timeline-item>
                        </el-timeline>
                    </el-scrollbar>
                </div>
            </div>
        </el-card>
    </div>
</template>

<script setup lang="ts">
import { ref, onUnmounted, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import {
    VideoCamera,
    VideoPause,
    Upload,
    Clock,
    TrendCharts as DataTrend,
    User,
    View,
    Search,
    RefreshLeft,
} from '@element-plus/icons-vue'
import * as faceapi from 'face-api.js'
import axios from 'axios'

// 组件状态
const videoRef = ref<HTMLVideoElement | null>(null)
const canvasRef = ref<HTMLCanvasElement | null>(null)
const camera = ref<any>(null)
const isVideoActive = ref(false)
const capturedImage = ref('')
const selectedFile = ref<File | null>(null)
const loading = ref(false)
const faceDetected = ref(false)
const recognitionResult = ref<RecognitionResult | null>(null)
const recognitionHistory = ref<HistoryRecord[]>([])
const lastRecognitionTime = ref(Date.now())
const RECOGNITION_COOLDOWN = 2000  // 识别冷却时间（毫秒）
const isProcessing = ref(false)

// 添加这些状态定义
const isModelLoading = ref(false)
const faceDetector = ref<any>(null)
const detectionTimer = ref<number | null>(null)

// 定义类型
interface RecognitionResult {
  success: boolean
  message: string
  data?: any
}

interface HistoryRecord {
  time: string
  success: boolean
  message: string
}

// 添加日志函数
const log = (message: string, type: 'info' | 'error' | 'success' = 'info') => {
    console.log(`[Face Recognition] ${message}`)
    if (type === 'error') {
        ElMessage.error(message)
    } else if (type === 'success') {
        ElMessage.success(message)
    } else {
        ElMessage.info(message)
    }
}

// 修改初始化检测器函
const initFaceDetector = async () => {
    try {
        isModelLoading.value = true
        // const MODEL_URL = 'https://cdn.jsdelivr.net/npm/@vladmandic/face-api/model/'
        const MODEL_URL = '/models/face-api'
        await faceapi.nets.tinyFaceDetector.loadFromUri(MODEL_URL)
        return true
    } catch (error) {
        console.error('人脸检测初始化失败:', error)
        ElMessage.error('初始化失败，请刷新重试')
        return false
    } finally {
        isModelLoading.value = false
    }
}

// 人脸检测函数
const detectFace = async (): Promise<boolean> => {
    if (!videoRef.value) return false
    
    try {
        const detections = await faceapi.detectAllFaces(
            videoRef.value,
            new faceapi.TinyFaceDetectorOptions({ 
                inputSize: 416,
                scoreThreshold: 0.5  // 设置置信度阈值为 0.5
            })
        )
        
        faceDetected.value = detections.length > 0
        return faceDetected.value
    } catch (error) {
        console.error('人脸检测失败:', error)
        return false
    }
}

// 修改开启摄像头函数
const startCamera = async () => {
    try {
        isModelLoading.value = true
        
        if (!videoRef.value) return

        const stream = await navigator.mediaDevices.getUserMedia({ 
            video: { 
                width: 640,
                height: 480 
            } 
        })
        
        videoRef.value.srcObject = stream
        await new Promise((resolve) => {
            if (videoRef.value) {
                videoRef.value.onloadedmetadata = resolve
            }
        })
        
        isVideoActive.value = true
        capturedImage.value = ''
        selectedFile.value = null
        recognitionResult.value = null

        startFaceDetection()

    } catch (error) {
        console.error('摄像头访问错误:', error)
        ElMessage.error('无法访问摄像头')
    } finally {
        isModelLoading.value = false
    }
}

// 修改人脸检测循环
const startFaceDetection = () => {
    const detectLoop = async () => {
        if (!isVideoActive.value) return
        
        if (!isProcessing.value) {
            try {
                const hasFace = await detectFace()
                
                if (hasFace) {
                    const now = Date.now()
                    if (now - lastRecognitionTime.value >= RECOGNITION_COOLDOWN) {
                        isProcessing.value = true
                        lastRecognitionTime.value = now
                        await captureImage()
                        await startRecognition()
                    }
                }
            } catch (error) {
                console.error('检测错误:', error)
                isProcessing.value = false
            }
        }
        
        if (isVideoActive.value) {
            detectionTimer.value = requestAnimationFrame(detectLoop)
        }
    }
    
    detectLoop()
}

// 修改关闭摄像头函数
const stopCamera = () => {
    if (videoRef.value && videoRef.value.srcObject) {
        const stream = videoRef.value.srcObject as MediaStream
        stream.getTracks().forEach(track => track.stop())
        videoRef.value.srcObject = null
    }
    
    // 取消动画帧
    if (detectionTimer.value) {
        cancelAnimationFrame(detectionTimer.value)
        detectionTimer.value = null
    }
    
    isVideoActive.value = false
    faceDetected.value = false
}

// 修改组件卸载时的清理
onUnmounted(() => {
    stopCamera()
})

// 修改组件挂载函数，自动开启摄像头
onMounted(async () => {
    try {
        await initFaceDetector()
        await startCamera()
    } catch (error) {
        console.error('初始化失败:', error)
        ElMessage.error('初始化失败，请刷新重试')
    }
})

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

// 捕获图像
const captureImage = () => {
    if (!videoRef.value || !canvasRef.value) return null

    const context = canvasRef.value.getContext('2d')
    if (!context) return null

    // 保持 canvas 和视频相同的尺寸
    const videoWidth = videoRef.value.videoWidth
    const videoHeight = videoRef.value.videoHeight
    
    canvasRef.value.width = videoWidth
    canvasRef.value.height = videoHeight

    // 在绘制时保持比例
    context.drawImage(
        videoRef.value,
        0, 0,
        videoWidth,
        videoHeight
    )

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
        }, 'image/jpeg', 0.95)  // 添加质量参数
    })
}

// 开始识别
const startRecognition = async () => {
    if (!selectedFile.value) {
        ElMessage.error('未获取到图片')
        isProcessing.value = false  // 重要：确保重置处理状态
        return
    }

    loading.value = true
    try {
        const formData = new FormData()
        formData.append('image', selectedFile.value)

        const response = await axios.post('http://localhost:8001/api/recognize', formData, {
            headers: {
                'Content-Type': 'multipart/form-data'
            }
        })

        if (response.data.success) {
            recognitionResult.value = {
                success: true,
                message: `识别成功：${response.data.data.name}`,
                data: response.data.data
            }
            
            // 添加到历史记录
            recognitionHistory.value.unshift({
                time: new Date().toLocaleString(),
                success: true,
                message: recognitionResult.value.message
            })
            
            // 显示成功特效
            showSuccessEffect()
        } else {
            recognitionResult.value = {
                success: false,
                message: response.data.message || '无法识别，请重试'
            }
            // 添加到历史记录
            recognitionHistory.value.unshift({
                time: new Date().toLocaleString(),
                success: false,
                message: recognitionResult.value.message
            })
            
            log(recognitionResult.value.message, 'error')
        }
    } catch (error: any) {
        console.error('Recognition error:', error)
        recognitionResult.value = {
            success: false,
            message: error.response?.data?.message || '服务器错误，请稍后重试'
        }
        // 添加到历史记录
        recognitionHistory.value.unshift({
            time: new Date().toLocaleString(),
            success: false,
            message: recognitionResult.value.message
        })
        
        log(recognitionResult.value.message, 'error')
    } finally {
        // 无论成功失败，都重置所有相关状态
        loading.value = false
        isProcessing.value = false
        selectedFile.value = null
        capturedImage.value = ''
        
        // 延长结果显示时间到4秒
        setTimeout(() => {
            recognitionResult.value = null
        }, 3000)  // 从2000改为3000
    }
}

// 重置识别
const resetRecognition = () => {
    console.log('重置识别...') // 添加调试日志
    
    // 重置所有状态
    recognitionResult.value = null
    capturedImage.value = ''
    selectedFile.value = null
    loading.value = false
    
    // 如果摄像头是开启状态，保持开启
    if (isVideoActive.value) {
        // 重新开始视频流
        if (videoRef.value && videoRef.value.srcObject) {
            videoRef.value.play()
        }
    } else {
        // 如果摄像头未启，显示上传区域
        isVideoActive.value = false
    }
    
    console.log('重置完成') // 添加调试日志
}

// 加体检测逻辑
const livenessChecking = ref(false)
const detectionProgress = ref(0)
const currentPrompt = ref('')
const currentAction = ref('')

const actions = [
    { name: 'blink', prompt: '请眨眨眼' },
    { name: 'turn-left', prompt: '请向左转头' },
    { name: 'turn-right', prompt: '请右转头' },
    { name: 'nod', prompt: '请点头' }
]

const startLivenessCheck = async () => {
    livenessChecking.value = true
    for (const action of actions) {
        currentAction.value = action.name
        currentPrompt.value = action.prompt
        // 这里添加实际活体检测逻辑
        await new Promise(resolve => setTimeout(resolve, 2000))
        detectionProgress.value += 25
    }
    livenessChecking.value = false
    detectionProgress.value = 100
}

// 添加行为监测逻
const monitoringEnabled = ref(false)
const behaviorAlerts = ref([
    {
        level: 'warning',
        message: '检测到多人聚集',
        time: '2分钟前'
    },
    {
        level: 'danger',
        message: '检测到疑行为',
        time: '5分钟前'
    }
])

// 修改继识别的处理逻辑
const handleContinue = () => {
    console.log('继续识别...')
    
    // 重置所有状态
    recognitionResult.value = null
    capturedImage.value = ''
    selectedFile.value = null
    loading.value = false
}

// 修改识别成功后的特效
const showSuccessEffect = () => {
    // 1. 创建特效容器
    const effectContainer = document.createElement('div')
    effectContainer.className = 'success-effect-container'
    
    // 2. 创建成功图标
    const successIcon = document.createElement('div')
    successIcon.className = 'success-icon'
    successIcon.innerHTML = '<svg viewBox="0 0 52 52"><circle cx="26" cy="26" r="25" fill="none"/><path fill="none" d="M14.1 27.2l7.1 7.2 16.7-16.8"/></svg>'
    
    // 3. 创建粒子效果
    for (let i = 0; i < 20; i++) {
        const particle = document.createElement('div')
        particle.className = 'success-particle'
        effectContainer.appendChild(particle)
    }
    
    effectContainer.appendChild(successIcon)
    document.body.appendChild(effectContainer)
    
    // 4. 添加动画结束监听器
    setTimeout(() => {
        effectContainer.addEventListener('animationend', () => {
            document.body.removeChild(effectContainer)
        }, { once: true })
        effectContainer.classList.add('fade-out')
    }, 4000)  // 从2000改为4000
}

// 添加重置上传函数
const resetUpload = () => {
    capturedImage.value = ''
    selectedFile.value = null
    recognitionResult.value = null
}
</script>

<style scoped>
@import 'animate.css';

.face-recognition {
    padding: 20px;
    height: calc(100vh - 140px);
    display: flex;
    flex-direction: column;
}

.recognition-container {
    display: grid;
    grid-template-columns: 2fr 1fr;
    gap: 24px;
    padding: 24px;
    flex: 1;
    min-height: 0;
}

.camera-section {
    display: flex;
    flex-direction: column;
    height: 100%;
    min-height: 0;
}

.camera-container {
    position: relative;
    flex: 1;
    min-height: 300px;
    max-height: 400px;
    background: #f5f7fa;
    border-radius: 8px;
    overflow: hidden;
    margin-bottom: 0;
}

.video-active {
    width: 100%;
    height: 100%;
    object-fit: contain;
    max-height: 400px;
}

.face-detection-frame {
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    width: 200px;
    height: 200px;
    border: 2px solid #909399;  /* 默认灰色边框 */
    border-radius: 8px;
    transition: border-color 0.3s ease;
}

.face-detection-frame.face-detected {
    border-color: #67C23A;  /* 检测到人时显示绿色 */
    box-shadow: 0 0 10px rgba(103, 194, 58, 0.5);
}

.camera-controls {
    margin-top: 20px;
    display: flex;
    justify-content: center;
}

.recognition-history {
    display: flex;
    flex-direction: column;
    height: 80%;
    min-height: 0;
    padding: 20px;
    background: #fff;
    border-radius: 12px;
    box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
}

.section-header {
    display: flex;
    align-items: center;
    gap: 8px;
    margin-bottom: 16px;
    flex-shrink: 0;
}

.section-header h2 {
    font-size: 18px;
    font-weight: 600;
    margin: 0;
    display: flex;
    align-items: center;
    gap: 8px;
}

.recognition-history .el-scrollbar {
    flex: 1;
    height: auto !important;
    min-height: 0;
}

.el-timeline {
    padding: 0;
    margin: 0;
}

.history-item {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 4px 0;
}

.history-message {
    color: #606266;
    flex: 1;
    word-break: break-all;
}

@media screen and (max-height: 800px) {
    .recognition-history {
        padding: 16px;
    }
    
    .section-header {
        margin-bottom: 12px;
    }
    
    .section-header h2 {
        font-size: 16px;
    }
}

@media screen and (max-height: 600px) {
    .recognition-history {
        padding: 12px;
    }
    
    .section-header {
        margin-bottom: 8px;
    }
    
    .history-item {
        padding: 2px 0;
    }
}

.stats-section {
    margin-top: auto;
    padding: 20px 0;
}

.stat-card {
    transition: all 0.3s ease;
    background: #fff;
    border: none;
    overflow: hidden;
    position: relative;
}

.stat-card::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: linear-gradient(45deg, transparent, rgba(255, 255, 255, 0.5), transparent);
    transform: translateX(-100%);
    transition: transform 0.6s;
}

.stat-card:hover {
    transform: translateY(-5px);
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15);
}

.stat-card:hover::before {
    transform: translateX(100%);
}

.stat-content {
    display: flex;
    align-items: center;
    gap: 16px;
    padding: 20px;
}

.stat-icon {
    width: 48px;
    height: 48px;
    border-radius: 8px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 24px;
    flex-shrink: 0;
}

.stat-icon.primary {
    background: linear-gradient(135deg, #409eff, #2c5cff);
    color: white;
    box-shadow: 0 4px 12px rgba(64, 158, 255, 0.3);
}

.stat-icon.success {
    background: linear-gradient(135deg, #67c23a, #4caf50);
    color: white;
    box-shadow: 0 4px 12px rgba(103, 194, 58, 0.3);
}

.stat-icon.warning {
    background: linear-gradient(135deg, #e6a23c, #f57c00);
    color: white;
    box-shadow: 0 4px 12px rgba(230, 162, 60, 0.3);
}

.stat-info {
    flex: 1;
    display: flex;
    flex-direction: column;
    align-items: center;
    text-align: center;
}

.stat-value {
    font-size: 28px;
    font-weight: bold;
    color: #303133;
    margin-bottom: 4px;
}

.stat-label {
    font-size: 14px;
    color: #909399;
}

/* 加呼吸灯效果 */
@keyframes glow {

    0%,
    100% {
        box-shadow: 0 0 5px rgba(64, 158, 255, 0.5);
    }

    50% {
        box-shadow: 0 0 20px rgba(64, 158, 255, 0.8);
    }
}

.stat-icon {
    animation: glow 2s infinite;
}

.result-overlay {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: rgba(255, 255, 255, 0.95);
    display: flex;
    align-items: center;
    justify-content: center;
}

.pulse {
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

.liveness-detection {
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    width: 200px;
    height: 200px;
    background: rgba(255, 255, 255, 0.95);
    border-radius: 8px;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    text-align: center;
}

.detection-prompt {
    font-size: 16px;
    color: #303133;
    margin-bottom: 10px;
}

.action-guide {
    font-size: 24px;
    color: #409EFF;
    animation: blink 2s infinite;
}

@keyframes blink {
    0% {
        opacity: 1;
    }

    50% {
        opacity: 0;
    }

    100% {
        opacity: 1;
    }
}

.behavior-monitoring {
    margin-top: 20px;
}

.monitoring-card {
    background: #fff;
    border-radius: 12px;
    overflow: hidden;
    box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
}

.card-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 16px;
}

.behavior-list {
    padding: 16px;
}

.behavior-alert {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 8px;
    border-radius: 4px;
    margin-bottom: 8px;
}

.warning {
    background-color: #f5f7fa;
}

.danger {
    background-color: #fef2f2;
}

.time {
    font-size: 12px;
    color: #909399;
}

/* 添加统计卡片样式 */
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
    padding: 20px;
}

.stat-icon {
    width: 48px;
    height: 48px;
    border-radius: 8px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 24px;
    flex-shrink: 0;
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

.stat-info {
    flex: 1;
    display: flex;
    flex-direction: column;
    align-items: center;
    text-align: center;
}

.stat-value {
    font-size: 24px;
    font-weight: bold;
    color: #303133;
    margin-bottom: 4px;
    line-height: 1;
}

.stat-label {
    font-size: 14px;
    color: #909399;
    line-height: 1;
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
    background: #f5f7fa;
}

.upload-area {
    width: 100%;
    height: 100%;
    display: flex;
    align-items: center;
    justify-content: center;
}

:deep(.el-upload-dragger) {
    width: 100%;
    height: 100%;
    background: transparent;
    border: none;
    display: flex;
    flex-direction: column;
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

.capture-overlay {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: #f5f7fa;
}

.capture-overlay img {
    width: 100%;
    height: 100%;
    object-fit: contain;
}

.capture-controls {
    position: absolute;
    bottom: 20px;
    left: 0;
    right: 0;
    display: flex;
    justify-content: center;
    padding: 10px;
    background: rgba(255, 255, 255, 0.9);
}

.capture-controls .el-button-group {
    display: flex;
    gap: 10px;
}

.capture-controls .el-button {
    min-width: 120px;
}

.controls {
    display: flex;
    flex-direction: column;
    gap: 12px;
    margin-bottom: 16px;
}

.button-group {
    display: flex;
    gap: 12px;
    justify-content: center;
    padding: 16px 0;
    background: #fff;
    border-radius: 8px;
    box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
    margin-top: 20px;
}

.button-group .el-button {
    min-width: 120px;
}

.register-form {
    display: flex;
    gap: 12px;
    justify-content: center;
    margin-bottom: 12px;
}

.result-container {
    margin-top: 30px;
}

/* 添加响应式布局 */
@media screen and (max-height: 800px) {
    .camera-container {
        min-height: 275px;
        max-height: 350px;
    }
    
    .video-active {
        max-height: 350px;
    }
    
    .button-controls {
        height: 60px;
        padding: 8px;
    }
}

@media screen and (max-height: 600px) {
    .camera-container {
        min-height: 220px;
        max-height: 300px;
    }
    
    .video-active {
        max-height: 300px;
    }
    
    .button-controls {
        height: 50px;
        padding: 4px;
    }
}

.recognition-history .el-scrollbar {
    flex: 1;
    height: auto !important;
}

/* 添加按钮组样式 */
.button-controls {
    position: relative;
    display: flex;
    justify-content: center;
    padding: 10px;
    margin-top: 20px;
}

.button-controls .el-button-group {
    display: flex;
    gap: 8px;
}

.button-controls .el-button {
    min-width: 120px;
    height: 40px;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 5px;
}

/* 确保按组在摄像头开启时仍然可见 */
.camera-container {
    position: relative;
    flex: 1;
    min-height: 300px;
    max-height: 400px;
    background: #f5f7fa;
    border-radius: 8px;
    overflow: hidden;
    margin-bottom: 0;
}

/* 响应式布局优 */
@media screen and (max-height: 800px) {
    .button-controls {
        padding: 12px;
        min-height: 60px;
    }
    
    .button-controls .el-button {
        height: 36px;
    }
}

@media screen and (max-height: 600px) {
    .button-controls {
        padding: 8px;
        min-height: 50px;
    }
    
    .button-controls .el-button {
        height: 32px;
        min-width: 100px;
    }
}

/* 添加识别成功特效样式 */
.success-animation {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    pointer-events: none;
}

/* 扫描线动画 */
.scan-line {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 2px;
    background: linear-gradient(90deg, transparent, #67C23A, transparent);
    animation: scan 2s linear infinite;
}

@keyframes scan {
    0% {
        transform: translateY(0);
    }
    50% {
        transform: translateY(100%);
    }
    100% {
        transform: translateY(0);
    }
}

/* 脉冲圈动画 */
.pulse-circle {
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    width: 200px;
    height: 200px;
    border-radius: 50%;
    border: 2px solid #67C23A;
    animation: pulse 2s ease-out infinite;
}

@keyframes pulse {
    0% {
        transform: translate(-50%, -50%) scale(0.8);
        opacity: 1;
        border-color: #67C23A;
    }
    100% {
        transform: translate(-50%, -50%) scale(2);
        opacity: 0;
        border-color: transparent;
    }
}

/* 成功图标画 */
.success-icon {
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    width: 80px;
    height: 80px;
    background: #67C23A;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    animation: glow 2s ease-in-out infinite;
}

.success-check {
    font-size: 40px;
    color: white;
}

@keyframes glow {
    0%, 100% {
        box-shadow: 0 0 20px rgba(103, 194, 58, 0.6);
    }
    50% {
        box-shadow: 0 0 40px rgba(103, 194, 58, 0.8);
    }
}

/* 结果卡片动画 */
.result-overlay {
    background: rgba(255, 255, 255, 0.95);
    backdrop-filter: blur(8px);
    animation: fadeInOut 1s ease-in-out forwards;
}

@keyframes fadeInOut {
    0% {
        opacity: 0;
    }
    20% {
        opacity: 1;
    }
    80% {
        opacity: 1;
    }
    100% {
        opacity: 0;
    }
}

/* 添加全屏成功特效 */
.success-effect {
    position: fixed;
    top: 0;
    left: 0;
    width: 100vw;
    height: 100vh;
    background: radial-gradient(circle, rgba(103, 194, 58, 0) 0%, rgba(103, 194, 58, 0.2) 100%);
    z-index: 9999;
    animation: success-pulse 1s ease-out forwards;
    pointer-events: none;
}

@keyframes success-pulse {
    0% {
        transform: scale(0);
        opacity: 0;
    }
    50% {
        opacity: 1;
    }
    100% {
        transform: scale(2);
        opacity: 0;
    }
}

/* 修改识别结果样式 */
.result-overlay {
    background: rgba(255, 255, 255, 0.95);
    backdrop-filter: blur(8px);
    animation: fadeInOut 1s ease-in-out forwards;
}

@keyframes fadeInOut {
    0% {
        opacity: 0;
    }
    20% {
        opacity: 1;
    }
    80% {
        opacity: 1;
    }
    100% {
        opacity: 0;
    }
}

/* 添加人脸检测框动画 */
.face-detection-frame {
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    width: 200px;
    height: 200px;
    border: 2px solid #909399;
    border-radius: 8px;
    transition: all 0.3s ease;
}

.face-detection-frame.face-detected {
    border-color: #67C23A;
    box-shadow: 0 0 20px rgba(103, 194, 58, 0.5);
    animation: pulse 2s infinite;
}

@keyframes pulse {
    0% {
        box-shadow: 0 0 0 0 rgba(103, 194, 58, 0.5);
    }
    70% {
        box-shadow: 0 0 0 20px rgba(103, 194, 58, 0);
    }
    100% {
        box-shadow: 0 0 0 0 rgba(103, 194, 58, 0);
    }
}

/* 添加按钮组特效样式 */
.button-controls {
    position: relative;
    display: flex;
    justify-content: center;
    padding: 16px;
    margin-top: 20px;
}

.button-controls .el-button-group {
    display: flex;
    gap: 8px;
}

.button-controls .el-button {
    min-width: 120px;
    height: 40px;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 5px;
}

/* 成功特效样式 */
.success-effect-container {
    position: fixed;
    top: 0;
    left: 0;
    width: 100vw;
    height: 100vh;
    display: flex;
    align-items: center;
    justify-content: center;
    background: rgba(0, 0, 0, 0.8);
    z-index: 9999;
    animation: fadeIn 0.3s ease-out;
}

.success-icon {
    width: 100px;
    height: 100px;
    position: relative;
    animation: iconScale 0.5s ease-out forwards;
}

.success-icon svg {
    width: 100%;
    height: 100%;
    stroke: #67C23A;
    stroke-width: 2;
    stroke-dasharray: 180;
    stroke-dashoffset: 180;
    animation: drawCheck 1s ease-out forwards;
}

.success-particle {
    position: absolute;
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background: #67C23A;
    pointer-events: none;
}

@keyframes drawCheck {
    to {
        stroke-dashoffset: 0;
    }
}

@keyframes iconScale {
    0% {
        transform: scale(0);
    }
    50% {
        transform: scale(1.2);
    }
    100% {
        transform: scale(1);
    }
}

@keyframes fadeIn {
    from {
        opacity: 0;
    }
    to {
        opacity: 1;
    }
}

.fade-out {
    animation: fadeOut 0.3s ease-out forwards;
}

@keyframes fadeOut {
    to {
        opacity: 0;
    }
}

/* 粒子动画 */
.success-particle {
    animation: particleAnimation 1s ease-out forwards;
}

@keyframes particleAnimation {
    0% {
        transform: translate(0, 0) scale(1);
        opacity: 1;
    }
    100% {
        transform: translate(
            calc(random(100) * 1px - 50px),
            calc(random(100) * 1px - 50px)
        ) scale(0);
        opacity: 0;
    }
}
</style>