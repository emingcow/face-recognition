<template>
    <div class="face-recognition">
        <el-card class="main-card">
            <template #header>
                <div class="card-header">
                    <span class="title">人脸识别系统</span>
                    <el-radio-group v-model="currentMode" class="mode-switch">
                        <el-radio-button value="register">人脸录入</el-radio-button>
                        <el-radio-button value="recognize">身份识别</el-radio-button>
                    </el-radio-group>
                </div>
            </template>

            <div class="camera-container">
                <video ref="videoRef" :class="{ 'video-active': isVideoActive }" autoplay></video>
                <canvas ref="canvasRef" style="display: none;"></canvas>

                <div class="camera-overlay" v-if="!isVideoActive">
                    <el-upload v-if="!isVideoActive" class="upload-area" drag :auto-upload="false"
                        :show-file-list="false" :on-change="handleFileChange">
                        <el-icon class="camera-icon">
                            <Upload />
                        </el-icon>
                        <div class="el-upload__text">
                            拖拽图片到此处或 <em>点击上传</em>
                        </div>
                    </el-upload>
                </div>

                <div class="capture-overlay" v-if="capturedImage">
                    <img :src="capturedImage" alt="已捕获的图像" />
                </div>
            </div>

            <div class="controls">
                <template v-if="currentMode === 'register'">
                    <el-form :model="registerForm" :rules="rules" ref="registerFormRef" class="register-form">
                        <el-form-item prop="name">
                            <el-input v-model="registerForm.name" placeholder="请输入姓名" class="name-input">
                                <template #prefix>
                                    <el-icon>
                                        <User />
                                    </el-icon>
                                </template>
                            </el-input>
                        </el-form-item>
                        <el-form-item prop="id">
                            <el-input v-model="registerForm.id" placeholder="请输入工号/学号" class="id-input">
                                <template #prefix>
                                    <el-icon>
                                        <Document />
                                    </el-icon>
                                </template>
                            </el-input>
                        </el-form-item>
                    </el-form>

                    <div class="button-group">
                        <el-button type="primary" @click="startCamera">
                            <el-icon>
                                <VideoPlay />
                            </el-icon>
                            开启摄像头
                        </el-button>

                        <el-button type="success" @click="handleRegister">
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
                    </div>
                </template>

                <template v-else>
                    <div class="button-group">
                        <el-button type="primary" @click="startCamera">
                            <el-icon>
                                <VideoPlay />
                            </el-icon>
                            开启摄像头
                        </el-button>

                        <el-button type="success" @click="startRecognition">
                            <el-icon>
                                <Search />
                            </el-icon>
                            {{ isVideoActive ? '拍照识别' : '开始识别' }}
                        </el-button>

                        <el-button type="danger" :disabled="!isVideoActive" @click="stopCamera">
                            <el-icon>
                                <VideoPause />
                            </el-icon>
                            关闭摄像头
                        </el-button>
                    </div>
                </template>
            </div>

            <!-- 识别结果展示 -->
            <div v-if="recognitionResult" class="result-container">
                <el-result :icon="recognitionResult.success ? 'success' : 'error'"
                    :title="recognitionResult.success ? '识别成功' : '识别失败'" :sub-title="recognitionResult.message">
                    <template #extra>
                        <el-button type="primary" @click="resetRecognition">继续识别</el-button>
                    </template>
                </el-result>
            </div>
        </el-card>
    </div>
</template>

<script lang="ts">
import { defineComponent, ref, reactive } from 'vue'
import { ElMessage } from 'element-plus'
import {
    VideoCamera, VideoPlay, VideoPause, Camera,
    Search, User, Upload, Document
} from '@element-plus/icons-vue'
import axios from 'axios'

interface RegisterForm {
    name: string
    id: string
}

interface RecognitionResult {
    success: boolean
    message: string
    data?: {
        name?: string
        id?: string
        confidence?: number
    }
}

export default defineComponent({
    name: 'FaceRecognition',
    components: {
        VideoCamera, VideoPlay, VideoPause,
        Camera, Search, User, Upload, Document
    },
    setup() {
        const currentMode = ref<'register' | 'recognize'>('register')
        const videoRef = ref<HTMLVideoElement | null>(null)
        const canvasRef = ref<HTMLCanvasElement | null>(null)
        const registerFormRef = ref()
        const isVideoActive = ref(false)
        const capturedImage = ref('')
        const selectedFile = ref<File | null>(null)
        const recognitionResult = ref<RecognitionResult | null>(null)
        const loading = ref(false)

        const registerForm = reactive<RegisterForm>({
            name: '',
            id: ''
        })

        const rules = {}

        const handleFileChange = (uploadFile: any) => {
            console.log('File selected:', uploadFile)
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
                    recognitionResult.value = null
                }
            } catch (error) {
                ElMessage.error('无法访问摄像头，请确保已授权限')
            }
        }

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

        const handleRegister = async () => {
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

                const config = {
                    headers: {
                        'Content-Type': 'multipart/form-data',
                    },
                }

                const response = await axios.post('http://localhost:8001/api/register', formData, config)

                if (response.data.success) {
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

        const startRecognition = async () => {
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
                formData.append('image', selectedFile.value)

                const config = {
                    headers: {
                        'Content-Type': 'multipart/form-data',
                    },
                }

                const response = await axios.post('http://localhost:8001/api/recognize', formData, config)

                if (response.data.success) {
                    recognitionResult.value = {
                        success: true,
                        message: `识别成功：${response.data.data.name}`,
                        data: response.data.data
                    }
                    stopCamera()
                } else {
                    recognitionResult.value = {
                        success: false,
                        message: response.data.message || '无法识别，请重试'
                    }
                }
            } catch (error: any) {
                console.error('Recognition error:', error)
                recognitionResult.value = {
                    success: false,
                    message: '服务器错误，请稍后重试'
                }
            } finally {
                loading.value = false
            }
        }

        const resetRecognition = () => {
            recognitionResult.value = null
            capturedImage.value = ''
            selectedFile.value = null
        }

        return {
            currentMode,
            videoRef,
            canvasRef,
            registerFormRef,
            registerForm,
            rules,
            isVideoActive,
            capturedImage,
            selectedFile,
            recognitionResult,
            loading,
            handleFileChange,
            startCamera,
            stopCamera,
            handleRegister,
            startRecognition,
            resetRecognition
        }
    }
})
</script>

<style scoped>
.face-recognition {
    padding: 20px;
    max-width: 800px;
    margin: 0 auto;
}

.main-card {
    background: #fff;
    border-radius: 8px;
}

.card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.title {
    font-size: 20px;
    font-weight: bold;
    color: #303133;
}

.camera-container {
    position: relative;
    width: 100%;
    height: 400px;
    background: #f5f7fa;
    border-radius: 8px;
    overflow: hidden;
    margin-bottom: 20px;
}

.upload-area {
    height: 100%;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
}

video {
    width: 100%;
    height: 100%;
    object-fit: cover;
    display: none;
}

.video-active {
    display: block;
}

.camera-overlay {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    background: #f5f7fa;
    color: #909399;
}

.camera-icon {
    font-size: 48px;
    margin-bottom: 16px;
}

.capture-overlay {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
}

.capture-overlay img {
    width: 100%;
    height: 100%;
    object-fit: contain;
    background: #f5f7fa;
}

.controls {
    display: flex;
    flex-direction: column;
    gap: 16px;
    margin-bottom: 20px;
}

.button-group {
    display: flex;
    gap: 16px;
    justify-content: center;
}

.register-form {
    display: flex;
    gap: 16px;
    justify-content: center;
    margin-bottom: 16px;
}

.name-input,
.id-input {
    width: 200px;
}

.result-container {
    margin-top: 20px;
}

:deep(.el-upload-dragger) {
    width: 100%;
    height: 100%;
    background: transparent;
}

:deep(.el-result) {
    padding: 24px;
}
</style>