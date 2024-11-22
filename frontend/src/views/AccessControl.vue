<template>
    <div class="access-control">
        <el-tabs>
            <el-tab-pane label="访问权限">
                <div class="action-bar">
                    <el-button type="primary" @click="showAddRuleDialog">
                        <el-icon>
                            <Plus />
                        </el-icon>
                        添加权限规则
                    </el-button>
                </div>
                <el-table :data="accessRules" border stripe>
                    <el-table-column prop="area" label="区域" />
                    <el-table-column prop="timeRange" label="允许时间" />
                    <el-table-column prop="personnel" label="授权人员" />
                    <el-table-column label="操作" width="200">
                        <template #default="scope">
                            <el-button-group>
                                <el-button type="primary" size="small" @click="editRule(scope.row)">
                                    <el-icon>
                                        <Edit />
                                    </el-icon>
                                    编辑
                                </el-button>
                                <el-button type="danger" size="small" @click="deleteRule(scope.row)">
                                    <el-icon>
                                        <Delete />
                                    </el-icon>
                                    删除
                                </el-button>
                            </el-button-group>
                        </template>
                    </el-table-column>
                </el-table>
            </el-tab-pane>

            <el-tab-pane label="访问记录">
                <div class="filter-bar">
                    <el-date-picker v-model="dateRange" type="daterange" range-separator="至" start-placeholder="开始日期"
                        end-placeholder="结束日期" @change="filterRecords" />
                    <el-select v-model="areaFilter" placeholder="选择区域" @change="filterRecords">
                        <el-option v-for="area in areas" :key="area.value" :label="area.label" :value="area.value" />
                    </el-select>
                </div>
                <el-timeline>
                    <el-timeline-item v-for="record in accessRecords" :key="record.id" :type="record.status"
                        :timestamp="record.time" :hollow="true">
                        <el-card class="record-card">
                            <div class="record-content">
                                <el-avatar :size="32" :src="record.avatar" />
                                <div class="record-info">
                                    <div class="record-title">
                                        {{ record.name }}
                                        <el-tag :type="record.status === 'success' ? 'success' : 'danger'" size="small">
                                            {{ record.status === 'success' ? '通过' : '拒绝' }}
                                        </el-tag>
                                    </div>
                                    <div class="record-description">{{ record.description }}</div>
                                </div>
                            </div>
                        </el-card>
                    </el-timeline-item>
                </el-timeline>
            </el-tab-pane>
        </el-tabs>

        <!-- 添加/编辑规则对话框 -->
        <el-dialog v-model="ruleDialog.visible" :title="ruleDialog.isEdit ? '编辑权限规则' : '添加权限规则'" width="500px">
            <el-form :model="ruleForm" label-width="100px">
                <el-form-item label="区域">
                    <el-select v-model="ruleForm.area" placeholder="选择区域">
                        <el-option v-for="area in areas" :key="area.value" :label="area.label" :value="area.value" />
                    </el-select>
                </el-form-item>
                <el-form-item label="时间范围">
                    <el-time-picker v-model="ruleForm.timeRange" is-range range-separator="至" start-placeholder="开始时间"
                        end-placeholder="结束时间" format="HH:mm" />
                </el-form-item>
                <el-form-item label="授权人员">
                    <el-select v-model="ruleForm.personnel" multiple filterable placeholder="选择授权人员">
                        <el-option v-for="person in personnel" :key="person.id" :label="person.name"
                            :value="person.id" />
                    </el-select>
                </el-form-item>
            </el-form>
            <template #footer>
                <el-button @click="ruleDialog.visible = false">取消</el-button>
                <el-button type="primary" @click="saveRule">确定</el-button>
            </template>
        </el-dialog>
    </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
    Plus,
    Edit,
    Delete,
    Search
} from '@element-plus/icons-vue'

// 区域数据
const areas = [
    { value: 'entrance', label: '主入口' },
    { value: 'office', label: '办公区' },
    { value: 'meeting', label: '会议室' },
    { value: 'server', label: '机房' }
]

// 人员数据
const personnel = [
    { id: '1', name: '张三' },
    { id: '2', name: '李四' },
    { id: '3', name: '王五' }
]

// 访问规则数据
const accessRules = ref([
    {
        id: '1',
        area: '主入口',
        timeRange: '09:00-18:00',
        personnel: '张三, 李四'
    },
    {
        id: '2',
        area: '办公区',
        timeRange: '08:00-20:00',
        personnel: '全体员工'
    }
])

// 访问记录数据
const accessRecords = ref([
    {
        id: '1',
        name: '张三',
        avatar: 'https://placeholder.com/32',
        status: 'success',
        time: '2024-01-01 09:00:00',
        description: '通过人脸识别进入主入口',
    },
    {
        id: '2',
        name: '李四',
        avatar: 'https://placeholder.com/32',
        status: 'danger',
        time: '2024-01-01 08:30:00',
        description: '未在允许时间范围内，访问被拒绝',
    }
])

// 筛选条件
const dateRange = ref([])
const areaFilter = ref('')

// 规则对话框
const ruleDialog = reactive({
    visible: false,
    isEdit: false
})

// 规则表单
const ruleForm = reactive({
    area: '',
    timeRange: [],
    personnel: []
})

// 显示添加规则对话框
const showAddRuleDialog = () => {
    ruleDialog.isEdit = false
    ruleDialog.visible = true
    // 重置表单
    ruleForm.area = ''
    ruleForm.timeRange = []
    ruleForm.personnel = []
}

// 编辑规则
const editRule = (rule: any) => {
    ruleDialog.isEdit = true
    ruleDialog.visible = true
    // 填充表单
    Object.assign(ruleForm, rule)
}

// 删除规则
const deleteRule = (rule: any) => {
    ElMessageBox.confirm(
        '确定要删除这条规则吗？',
        '警告',
        {
            confirmButtonText: '确定',
            cancelButtonText: '取消',
            type: 'warning'
        }
    ).then(() => {
        // 这里添加删除逻辑
        ElMessage.success('删除成功')
    })
}

// 保存规则
const saveRule = () => {
    // 这里添加保存逻辑
    ElMessage.success(ruleDialog.isEdit ? '修改成功' : '添加成功')
    ruleDialog.visible = false
}

// 筛选记录
const filterRecords = () => {
    // 这里添加筛选逻辑
    console.log('Filter:', { dateRange: dateRange.value, area: areaFilter.value })
}
</script>

<style scoped>
.access-control {
    padding: 20px;
    height: calc(100vh - 84px);
    overflow: auto;
}

.action-bar {
    margin-bottom: 20px;
}

.filter-bar {
    margin-bottom: 20px;
    display: flex;
    gap: 16px;
}

.record-card {
    margin-bottom: 4px;
    transition: all 0.3s ease;
}

.record-card:hover {
    transform: translateX(5px);
    box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
}

.record-content {
    display: flex;
    align-items: center;
    gap: 12px;
}

.record-info {
    flex: 1;
}

.record-title {
    display: flex;
    align-items: center;
    gap: 8px;
    margin-bottom: 4px;
}

.record-description {
    color: #666;
    font-size: 14px;
}

:deep(.el-timeline-item__node) {
    background-color: transparent;
}

:deep(.el-timeline-item__node--success) {
    color: var(--el-color-success);
}

:deep(.el-timeline-item__node--danger) {
    color: var(--el-color-danger);
}

/* 添加动画效果 */
.el-button {
    transition: all 0.3s ease;
}

.el-button:hover {
    transform: translateY(-2px);
}

.el-table {
    margin-top: 20px;
    box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
    border-radius: 4px;
}

.el-tabs {
    background: white;
    padding: 20px;
    border-radius: 8px;
    box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
}
</style>