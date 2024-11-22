<template>
    <div class="emergency-alert">
        <el-button type="danger" class="alarm-button" :loading="alerting" @click="triggerAlert">
            紧急报警
        </el-button>

        <el-dialog v-model="showEmergencyDialog" title="紧急情况处理" width="500px">
            <div class="emergency-info">
                <el-steps :active="currentStep" finish-status="success">
                    <el-step title="发送警报" />
                    <el-step title="通知安保" />
                    <el-step title="记录事件" />
                </el-steps>

                <div class="emergency-actions">
                    <el-form>
                        <el-form-item label="事件类型">
                            <el-select v-model="emergencyType">
                                <el-option label="可疑人员" value="suspicious" />
                                <el-option label="非法闯入" value="intrusion" />
                                <el-option label="打架斗殴" value="fight" />
                            </el-select>
                        </el-form-item>

                        <el-form-item label="事件描述">
                            <el-input type="textarea" v-model="emergencyDesc" />
                        </el-form-item>
                    </el-form>
                </div>
            </div>
        </el-dialog>
    </div>
</template>