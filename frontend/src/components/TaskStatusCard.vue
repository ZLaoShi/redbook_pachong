<script setup>
import { defineProps, computed } from 'vue'
import { NTag, NProgress } from 'naive-ui'

const props = defineProps({
  task: {
    type: Object,
    required: true
  }
})

// 计算处理进度
const progressPercentage = computed(() => {
  if (!props.task) return 0
  if (props.task.total_notes_identified === 0) return 0
  
  return Math.round((props.task.notes_processed_count / props.task.total_notes_identified) * 100)
})

// 计算成功率
const successRate = computed(() => {
  if (!props.task || !props.task.notes || props.task.notes.length === 0) return 0
  
  const completedNotes = props.task.notes.filter(note => 
    note.processing_status === 'completed'
  ).length
  
  return Math.round((completedNotes / props.task.notes.length) * 100)
})

// 确定状态颜色
const statusType = computed(() => {
  const statusMap = {
    'pending': 'info',
    'in_progress': 'warning',
    'notes_identified': 'success',
    'collected': 'success',
    'completed': 'success',
    'failed': 'error',
    'no_notes_found': 'warning'
  }
  
  return statusMap[props.task.status] || 'default'
})

// 状态显示文本
const statusText = computed(() => {
  const statusMap = {
    'pending': '等待处理',
    'in_progress': '处理中',
    'notes_identified': '已识别笔记',
    'collected': '已采集',
    'completed': '已完成',
    'failed': '失败',
    'no_notes_found': '未找到笔记'
  }
  
  return statusMap[props.task.status] || props.task.status
})
</script>

<template>
  <div class="task-status-card">
    <div class="status-header">
      <div class="status-title">
        <span class="label">博主ID:</span>
        <span class="value">{{ task.blogger_id || '加载中...' }}</span>
      </div>
      <n-tag :type="statusType">{{ statusText }}</n-tag>
    </div>
    
    <div class="status-progress">
      <div class="progress-item">
        <div class="progress-label">
          <span>处理进度:</span>
          <span>{{ progressPercentage }}%</span>
        </div>
        <n-progress 
          type="line" 
          :percentage="progressPercentage"
          :status="task.status === 'failed' ? 'error' : 'success'"
          :show-indicator="false"
        />
      </div>
      
      <div v-if="task.notes && task.notes.length > 0" class="progress-item">
        <div class="progress-label">
          <span>成功率:</span>
          <span>{{ successRate }}%</span>
        </div>
        <n-progress 
          type="line" 
          :percentage="successRate"
          :status="successRate < 50 ? 'error' : successRate < 80 ? 'warning' : 'success'"
          :show-indicator="false"
        />
      </div>
    </div>
    
    <div class="status-info">
      <div class="info-item">
        <span class="label">笔记总数:</span>
        <span class="value">{{ task.total_notes_identified }}</span>
      </div>
      <div class="info-item">
        <span class="label">已处理:</span>
        <span class="value">{{ task.notes_processed_count }}</span>
      </div>
      <div class="info-item">
        <span class="label">创建时间:</span>
        <span class="value">{{ new Date(task.created_at).toLocaleString() }}</span>
      </div>
      <div class="info-item">
        <span class="label">更新时间:</span>
        <span class="value">{{ new Date(task.updated_at).toLocaleString() }}</span>
      </div>
    </div>
    
    <div v-if="task.status_message" class="status-message">
      <span class="label">状态信息:</span>
      <span class="value">{{ task.status_message }}</span>
    </div>
  </div>
</template>

<style scoped lang="scss">
.task-status-card {
  padding: 16px;
  background-color: #f9f9f9;
  border-radius: 8px;
  
  .status-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 16px;
    
    .status-title {
      font-weight: 500;
      
      .label {
        color: #666;
        margin-right: 4px;
      }
      
      .value {
        color: #333;
      }
    }
  }
  
  .status-progress {
    margin-bottom: 16px;
    
    .progress-item {
      margin-bottom: 8px;
      
      .progress-label {
        display: flex;
        justify-content: space-between;
        margin-bottom: 4px;
        font-size: 14px;
        color: #666;
      }
    }
  }
  
  .status-info {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 12px;
    margin-bottom: 16px;
    
    .info-item {
      .label {
        color: #666;
        margin-right: 4px;
      }
      
      .value {
        color: #333;
      }
    }
  }
  
  .status-message {
    padding: 12px;
    background-color: #f0f0f0;
    border-radius: 4px;
    
    .label {
      font-weight: 500;
      color: #666;
      margin-right: 4px;
    }
    
    .value {
      color: #333;
    }
  }
}
</style>