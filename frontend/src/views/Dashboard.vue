<script setup>
import { ref, onMounted, computed, onBeforeUnmount, h } from 'vue'
import { useRouter } from 'vue-router'
import { NButton, NCard, NDataTable, NModal, NSpace, useMessage, NTag, NSpin } from 'naive-ui'
import { getTasks, getTaskDetail, deleteTask as apiDeleteTask } from '../api/tasks'

import TaskForm from '../components/TaskForm.vue'
import NoteDetail from '../components/NoteDetail.vue'
import TaskStatusCard from '../components/TaskStatusCard.vue'

const router = useRouter()
const message = useMessage()

// 状态管理
const loading = ref(false)
const taskLoading = ref(false)
const tasks = ref([])
const currentTask = ref(null)
const currentTaskId = ref(null)
const showCreateModal = ref(false)

// 状态计算
const taskProgress = computed(() => {
  if (!currentTask.value) return 0
  if (currentTask.value.total_notes_identified === 0) return 0
  
  // 所有已处理的笔记都计入进度，无论成功还是失败
  return Math.round((currentTask.value.notes_processed_count / currentTask.value.total_notes_identified) * 100)
})

// 表格列定义
const taskColumns = [
  {
    title: 'ID',
    key: 'id'
  },
  {
    title: '博主ID',
    key: 'blogger_id',
    render: (row) => {
      return row.blogger_id || '加载中...'
    }
  },
  {
    title: '状态',
    key: 'status',
    render: (row) => {
      const statusMap = {
        'pending': { type: 'info', text: '等待处理' },
        'in_progress': { type: 'warning', text: '处理中' },
        'notes_identified': { type: 'success', text: '已识别笔记' },
        'collected': { type: 'success', text: '已采集' },
        'completed': { type: 'success', text: '已完成' },
        'failed': { type: 'error', text: '失败' },
        'no_notes_found': { type: 'warning', text: '未找到笔记' }
      }
      
      const status = statusMap[row.status] || { type: 'default', text: row.status }
      
      return h(NTag, { type: status.type }, { default: () => status.text })
    }
  },
  {
    title: '笔记数',
    key: 'notes_count',
    render: (row) => `${row.notes_processed_count}/${row.total_notes_identified}`
  },
  {
    title: '创建时间',
    key: 'created_at',
    render: (row) => {
      return new Date(row.created_at).toLocaleString()
    }
  },
  {
    title: '操作',
    key: 'actions',
    render: (row) => {
      return h(NSpace, { align: 'center' }, {
        default: () => [
          h(
            NButton,
            { 
              size: 'small',
              onClick: () => viewTaskDetail(row.id)
            }, 
            { default: () => '查看' }
          ),
          h(
            NButton,
            { 
              size: 'small',
              type: 'error',
              onClick: () => handleDeleteTask(row.id)
            }, 
            { default: () => '删除' }
          )
        ]
      })
    }
  }
]

// 笔记表格列定义
const noteColumns = [
  {
    title: '标题',
    key: 'note_title',
    ellipsis: true
  },
  {
    title: '类型',
    key: 'note_type'
  },
  {
    title: '状态',
    key: 'processing_status',
    render: (row) => {
      const statusMap = {
        'pending_collection': { type: 'info', text: '待采集' },
        'collecting': { type: 'warning', text: '采集中' },
        'collected': { type: 'success', text: '已采集' },
        'pending_transcript': { type: 'info', text: '待转写' },
        'transcribing': { type: 'warning', text: '转写中' },
        'transcribed': { type: 'success', text: '已转写' },
        'pending_analysis': { type: 'info', text: '待分析' },
        'analyzing': { type: 'warning', text: '分析中' },
        'completed': { type: 'success', text: '已完成' },
        'error_collection': { type: 'error', text: '采集失败' },
        'error_transcript': { type: 'error', text: '转写失败' },
        'error_analysis': { type: 'error', text: '分析失败' }
      }
      
      const status = statusMap[row.processing_status] || { type: 'default', text: row.processing_status }
      
      return h(NTag, { type: status.type }, { default: () => status.text })
    }
  },
  {
    title: '点赞数',
    key: 'original_likes_count'
  },
  {
    title: '操作',
    key: 'actions',
    render: (row) => {
      return h(NSpace, { align: 'center' }, {
        default: () => [
          h(
            NButton,
            { 
              size: 'small',
              onClick: () => viewNoteDetail(row)
            }, 
            { default: () => '查看' }
          )
        ]
      })
    }
  }
]

// 获取任务列表
const fetchTasks = async () => {
  loading.value = true
  try {
    const response = await getTasks()
    tasks.value = response
  } catch (error) {
    message.error(error.message || '获取任务列表失败')
  } finally {
    loading.value = false
  }
}

// 获取任务详情
const viewTaskDetail = async (id) => {
  currentTaskId.value = id
  taskLoading.value = true
  try {
    const response = await getTaskDetail(id)
    currentTask.value = response
  } catch (error) {
    message.error(error.message || '获取任务详情失败')
  } finally {
    taskLoading.value = false
  }
}

// 查看笔记详情
const currentNote = ref(null)
const showNoteModal = ref(false)

const viewNoteDetail = (note) => {
  currentNote.value = note
  showNoteModal.value = true
}

// 处理任务创建成功
const handleTaskCreated = () => {
  showCreateModal.value = false
  fetchTasks()
}

// 删除任务
const handleDeleteTask = async (id) => {
  if (!confirm('确定要删除此任务吗？')) return
  
  try {
    await apiDeleteTask(id)
    message.success('任务删除成功')
    
    // 如果当前查看的是被删除的任务，清空当前任务
    if (currentTaskId.value === id) {
      currentTask.value = null
      currentTaskId.value = null
    }
    
    // 刷新任务列表
    fetchTasks()
  } catch (error) {
    message.error(error.message || '删除任务失败')
  }
}

// 退出登录
const logout = () => {
  localStorage.removeItem('token')
  localStorage.removeItem('user')
  router.push('/login')
  message.success('已退出登录')
}

// 自动刷新数据
let refreshInterval = null

const startAutoRefresh = () => {
  refreshInterval = setInterval(() => {
    if (currentTaskId.value) {
      viewTaskDetail(currentTaskId.value)
    }
    fetchTasks()
  }, 10000) // 每10秒刷新一次
}

const stopAutoRefresh = () => {
  if (refreshInterval) {
    clearInterval(refreshInterval)
    refreshInterval = null
  }
}

// 页面加载时获取任务列表
onMounted(() => {
  fetchTasks()
  startAutoRefresh()
})

// 组件销毁时清除刷新定时器
onBeforeUnmount(() => {
  stopAutoRefresh()
})
</script>

<template>
  <div class="dashboard-container">
    <!-- 顶部导航栏 -->
    <header class="dashboard-header">
      <div class="header-title">
        <h1>小红书内容分析工具</h1>
      </div>
      <div class="header-actions">
        <n-button type="primary" @click="showCreateModal = true">创建新任务</n-button>
        <n-button @click="logout">退出登录</n-button>
      </div>
    </header>
    
    <!-- 主内容区 -->
    <div class="dashboard-content">
      <!-- 左侧任务列表 -->
      <div class="task-list-container">
        <n-card title="任务列表" :bordered="false">
          <template #header-extra>
            <n-button size="small" @click="fetchTasks" :loading="loading">刷新</n-button>
          </template>
          
          <n-spin :show="loading">
            <n-data-table
              :columns="taskColumns"
              :data="tasks"
              :row-key="row => row.id"
              :pagination="{
                pageSize: 10
              }"
            />
          </n-spin>
        </n-card>
      </div>
      
      <!-- 右侧任务详情 -->
      <div class="task-detail-container">
        <n-card v-if="currentTask" :title="`任务详情 (ID: ${currentTask.id})`" :bordered="false">
          <template #header-extra>
            <n-button size="small" @click="viewTaskDetail(currentTaskId)" :loading="taskLoading">刷新</n-button>
          </template>
          
          <n-spin :show="taskLoading">
            <!-- 使用任务状态卡片组件 -->
            <task-status-card :task="currentTask" />
            
            <div class="notes-container">
              <h3>笔记列表</h3>
              <n-data-table
                :columns="noteColumns"
                :data="currentTask.notes || []"
                :row-key="row => row.id"
                :pagination="{
                  pageSize: 5
                }"
              />
            </div>
          </n-spin>
        </n-card>
        
        <n-card v-else :bordered="false">
          <div class="empty-state">
            <p>请从左侧选择一个任务查看详情</p>
          </div>
        </n-card>
      </div>
    </div>
    
    <!-- 创建任务弹窗 -->
    <n-modal
      v-model:show="showCreateModal"
      preset="card"
      title="创建新任务"
      style="width: 600px"
    >
      <!-- 使用任务表单组件 -->
      <task-form 
        @created="handleTaskCreated" 
        @cancel="showCreateModal = false" 
      />
    </n-modal>
    
    <!-- 笔记详情弹窗 -->
    <n-modal
      v-model:show="showNoteModal"
      preset="card"
      title="笔记详情"
      style="width: 800px"
    >
      <!-- 使用笔记详情组件 -->
      <note-detail v-if="currentNote" :note="currentNote" />
    </n-modal>
  </div>
</template>

<style scoped lang="scss">
.dashboard-container {
  display: flex;
  flex-direction: column;
  height: 100vh;
  
  .dashboard-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 16px 24px;
    background-color: #18a058;
    color: white;
    
    .header-title {
      h1 {
        margin: 0;
        font-size: 20px;
      }
    }
    
    .header-actions {
      display: flex;
      gap: 12px;
    }
  }
  
  .dashboard-content {
    flex: 1;
    display: flex;
    padding: 20px;
    gap: 20px;
    overflow: hidden;
    
    .task-list-container {
      width: 30%;
      min-width: 350px;
      overflow-y: auto;
    }
    
    .task-detail-container {
      flex: 1;
      overflow-y: auto;
      
      .notes-container {
        margin-top: 20px;
        
        h3 {
          margin-top: 0;
          margin-bottom: 16px;
        }
      }
      
      .empty-state {
        padding: 40px;
        text-align: center;
        color: #999;
      }
    }
  }
}
</style>