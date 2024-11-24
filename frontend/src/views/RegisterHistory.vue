<template>
    <div class="register-history">
        <!-- 顶部统计卡片 -->
        <el-row :gutter="20" class="stat-row">
            <el-col :span="8">
                <el-card shadow="hover" class="stat-card">
                    <div class="stat-content">
                        <div class="stat-icon primary animate__animated animate__bounceIn">
                            <el-icon><User /></el-icon>
                        </div>
                        <div class="stat-info">
                            <div class="stat-value animate__animated animate__fadeInUp">1,234</div>
                            <div class="stat-label">总录入人数</div>
                        </div>
                    </div>
                </el-card>
            </el-col>
            <el-col :span="8">
                <el-card shadow="hover" class="stat-card">
                    <div class="stat-content">
                        <div class="stat-icon success animate__animated animate__bounceIn" style="animation-delay: 0.2s">
                            <el-icon><Calendar /></el-icon>
                        </div>
                        <div class="stat-info">
                            <div class="stat-value animate__animated animate__fadeInUp" style="animation-delay: 0.2s">28</div>
                            <div class="stat-label">本月新增</div>
                        </div>
                    </div>
                </el-card>
            </el-col>
            <el-col :span="8">
                <el-card shadow="hover" class="stat-card">
                    <div class="stat-content">
                        <div class="stat-icon warning animate__animated animate__bounceIn" style="animation-delay: 0.4s">
                            <el-icon><Histogram /></el-icon>
                        </div>
                        <div class="stat-info">
                            <div class="stat-value animate__animated animate__fadeInUp" style="animation-delay: 0.4s">99.9%</div>
                            <div class="stat-label">录入成功率</div>
                        </div>
                    </div>
                </el-card>
            </el-col>
        </el-row>

        <!-- 主要内容区 -->
        <el-card class="main-card">
            <!-- 搜索和过滤区 -->
            <div class="filter-section">
                <el-input
                    v-model="searchQuery"
                    placeholder="搜索姓名或工号"
                    prefix-icon="Search"
                    clearable
                    @input="handleSearch"
                    class="search-input animate__animated animate__fadeInLeft"
                />
                <div class="filter-buttons animate__animated animate__fadeInRight">
                    <el-date-picker
                        v-model="dateRange"
                        type="daterange"
                        range-separator="至"
                        start-placeholder="开始日期"
                        end-placeholder="结束日期"
                        @change="handleDateChange"
                    />
                    <el-button type="primary" @click="refreshData">
                        <el-icon><Refresh /></el-icon>
                        刷新
                    </el-button>
                </div>
            </div>

            <!-- 数据表格 -->
            <el-table
                :data="filteredRecords"
                style="width: 100%"
                :header-cell-style="{ background: '#f5f7fa', textAlign: 'center' }"
                :cell-style="{ textAlign: 'center' }"
                @row-click="handleRowClick"
                v-loading="loading"
            >
                <el-table-column type="expand">
                    <template #default="props">
                        <div class="expand-detail">
                            <el-image
                                :src="props.row.avatar"
                                fit="cover"
                                class="detail-avatar"
                                :preview-src-list="[props.row.avatar]"
                            />
                            <div class="detail-info">
                                <h3>详细信息</h3>
                                <p><strong>录入时间：</strong>{{ formatDate(props.row.registerTime) }}</p>
                                <p><strong>录入位置：</strong>{{ props.row.location }}</p>
                                <p><strong>操作人员：</strong>{{ props.row.operator }}</p>
                                <p><strong>备注信息：</strong>{{ props.row.remarks }}</p>
                            </div>
                        </div>
                    </template>
                </el-table-column>
                <el-table-column
                    prop="avatar"
                    label="头像"
                    width="80"
                    align="center"
                >
                    <template #default="scope">
                        <el-avatar :src="scope.row.avatar" />
                    </template>
                </el-table-column>
                <el-table-column
                    prop="name"
                    label="姓名"
                    min-width="16%"
                    align="center"
                />
                <el-table-column
                    prop="id"
                    label="工号"
                    min-width="16%"
                    align="center"
                />
                <el-table-column
                    prop="registerTime"
                    label="录入时间"
                    min-width="20%"
                    align="center"
                >
                    <template #default="scope">
                        {{ formatDate(scope.row.registerTime) }}
                    </template>
                </el-table-column>
                <el-table-column
                    prop="status"
                    label="状态"
                    min-width="16%"
                    align="center"
                >
                    <template #default="scope">
                        <el-tag :type="scope.row.status === '成功' ? 'success' : 'danger'">
                            {{ scope.row.status }}
                        </el-tag>
                    </template>
                </el-table-column>
                <el-table-column
                    label="操作"
                    min-width="16%"
                    align="center"
                >
                    <template #default="scope">
                        <el-button-group>
                            <el-button
                                type="primary"
                                link
                                @click.stop="handleView(scope.row)"
                            >
                                <el-icon><View /></el-icon>
                            </el-button>
                            <el-button
                                type="primary"
                                link
                                @click.stop="handleEdit(scope.row)"
                            >
                                <el-icon><Edit /></el-icon>
                            </el-button>
                            <el-button
                                type="danger"
                                link
                                @click.stop="handleDelete(scope.row)"
                            >
                                <el-icon><Delete /></el-icon>
                            </el-button>
                        </el-button-group>
                    </template>
                </el-table-column>
            </el-table>

            <!-- 分页 -->
            <div class="pagination-section">
                <el-pagination
                    v-model:current-page="currentPage"
                    v-model:page-size="pageSize"
                    :page-sizes="[10, 20, 50, 100]"
                    layout="total, sizes, prev, pager, next, jumper"
                    :total="total"
                    @size-change="handleSizeChange"
                    @current-change="handleCurrentChange"
                />
            </div>
        </el-card>
    </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
    User,
    Calendar,
    Histogram,
    Search,
    Refresh,
    View,
    Edit,
    Delete
} from '@element-plus/icons-vue'

// 状态定义
const searchQuery = ref('')
const dateRange = ref([])
const loading = ref(false)
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)

// 模拟数据
const records = ref([
    {
        id: '1001',
        name: '张三',
        avatar: 'https://cube.elemecdn.com/0/88/03b0d39583f48206768a7534e55bcpng.png',
        registerTime: new Date('2024-01-15 10:30:00'),
        status: '成功',
        location: '前台登记处',
        operator: '管理员A',
        remarks: '正常录入'
    },
    {
        id: '1002',
        name: '李四',
        avatar: 'https://cube.elemecdn.com/0/88/03b0d39583f48206768a7534e55bcpng.png',
        registerTime: new Date('2024-01-14 15:20:00'),
        status: '成功',
        location: '前台登记处',
        operator: '管理员B',
        remarks: '正常录入'
    },
    {
        id: '1003',
        name: '王五',
        avatar: 'https://cube.elemecdn.com/0/88/03b0d39583f48206768a7534e55bcpng.png',
        registerTime: new Date('2024-01-13 09:15:00'),
        status: '失败',
        location: '前台登记处',
        operator: '管理员A',
        remarks: '光线不足'
    },
    {
        id: '1004',
        name: '赵六',
        avatar: 'https://cube.elemecdn.com/0/88/03b0d39583f48206768a7534e55bcpng.png',
        registerTime: new Date('2024-01-12 14:45:00'),
        status: '成功',
        location: '前台登记处',
        operator: '管理员C',
        remarks: '正常录入'
    },
    {
        id: '1005',
        name: '孙七',
        avatar: 'https://cube.elemecdn.com/0/88/03b0d39583f48206768a7534e55bcpng.png',
        registerTime: new Date('2024-01-11 11:30:00'),
        status: '成功',
        location: '前台登记处',
        operator: '管理员B',
        remarks: '正常录入'
    }
])

// 计算过滤后的记录
const filteredRecords = computed(() => {
    return records.value.filter(record => {
        const matchQuery = searchQuery.value ? 
            record.name.includes(searchQuery.value) || 
            record.id.includes(searchQuery.value) : true

        const matchDate = dateRange.value && dateRange.value.length === 2 ?
            new Date(record.registerTime) >= dateRange.value[0] &&
            new Date(record.registerTime) <= dateRange.value[1] : true

        return matchQuery && matchDate
    })
})

// 处理函数
const handleSearch = () => {
    currentPage.value = 1
}

const handleDateChange = () => {
    currentPage.value = 1
}

const refreshData = () => {
    loading.value = true
    setTimeout(() => {
        loading.value = false
        ElMessage.success('数据已刷新')
    }, 1000)
}

const handleRowClick = (row: any) => {
    console.log('Row clicked:', row)
}

const handleView = (row: any) => {
    ElMessage.info(`查看用户：${row.name}`)
}

const handleEdit = (row: any) => {
    ElMessage.info(`编辑用户：${row.name}`)
}

const handleDelete = (row: any) => {
    ElMessageBox.confirm(
        `确定要删除用户 ${row.name} 的录入记录吗？`,
        '警告',
        {
            confirmButtonText: '确定',
            cancelButtonText: '取消',
            type: 'warning',
        }
    ).then(() => {
        ElMessage.success(`删除成功：${row.name}`)
    }).catch(() => {
        ElMessage.info('已取消删除')
    })
}

const handleSizeChange = (val: number) => {
    pageSize.value = val
    currentPage.value = 1
}

const handleCurrentChange = (val: number) => {
    currentPage.value = val
}

// 工具函数
const formatDate = (date: Date) => {
    return new Date(date).toLocaleString()
}

// 生命周期钩子
onMounted(() => {
    refreshData()
})
</script>

<style scoped>
.register-history {
    padding: 20px;
    height: calc(100vh - 140px);
    display: flex;
    flex-direction: column;
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
}

.stat-value {
    font-size: 24px;
    font-weight: bold;
    color: #303133;
    margin-bottom: 4px;
}

.stat-label {
    font-size: 14px;
    color: #909399;
}

.main-card {
    flex: 1;
    display: flex;
    flex-direction: column;
    overflow: hidden;
}

.filter-section {
    margin-bottom: 20px;
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.search-input {
    width: 300px;
}

.filter-buttons {
    display: flex;
    gap: 16px;
    align-items: center;
}

.expand-detail {
    padding: 20px;
    display: flex;
    gap: 24px;
}

.detail-avatar {
    width: 200px;
    height: 200px;
    border-radius: 8px;
    object-fit: cover;
}

.detail-info {
    flex: 1;
}

.detail-info h3 {
    margin-top: 0;
    margin-bottom: 16px;
    color: #303133;
}

.detail-info p {
    margin: 8px 0;
    color: #606266;
}

.pagination-section {
    margin-top: 20px;
    display: flex;
    justify-content: flex-end;
}

:deep(.el-table) {
    border-radius: 8px;
    overflow: hidden;
}

:deep(.el-table th) {
    background-color: #f5f7fa !important;
}

:deep(.el-table tr:hover) td {
    background-color: #ecf5ff !important;
}

:deep(.el-table__body-wrapper) {
    overflow-x: hidden;
}

:deep(.el-table__header-wrapper) {
    width: 100%;
}
</style> 