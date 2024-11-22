<template>
    <div class="smart-alert">
        <el-card class="alert-card">
            <template #header>
                <div class="card-header">
                    <span>智能预警</span>
                    <el-tag :type="alertLevel">{{ alertStatus }}</el-tag>
                </div>
            </template>

            <div class="alert-content">
                <div class="risk-gauge">
                    <el-progress type="dashboard" :percentage="riskLevel" :color="riskColors" />
                    <span class="risk-text">当前风险等级</span>
                </div>

                <div class="alert-list">
                    <el-collapse v-model="activeAlerts">
                        <el-collapse-item v-for="alert in alerts" :key="alert.id" :title="alert.title" :name="alert.id">
                            <div class="alert-details">
                                <p>{{ alert.description }}</p>
                                <el-button type="primary" size="small">
                                    处理
                                </el-button>
                            </div>
                        </el-collapse-item>
                    </el-collapse>
                </div>
            </div>
        </el-card>
    </div>
</template>