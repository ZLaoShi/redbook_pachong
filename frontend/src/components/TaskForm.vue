<script setup>
import { ref, defineEmits } from 'vue'
import { NForm, NFormItem, NInput, NSelect, NInputNumber, NButton, NSpace, NCard, NDivider, useMessage } from 'naive-ui'
import { createTask } from '../api/tasks'

const emit = defineEmits(['created', 'cancel'])
const message = useMessage()

// 表单数据
const formData = ref({
  blogger_profile_url: '',
  user_cookie: '',
  scraping_rules: {
    type: 'video',
    sort_by: 'likes',
    count: 10
  }
})

// 加载状态
const loading = ref(false)

// 提交表单
const handleSubmit = async () => {
  // 验证表单
  if (!formData.value.blogger_profile_url) {
    message.error('请输入博主主页链接')
    return
  }
  
  if (!formData.value.user_cookie) {
    message.error('请输入Cookie')
    return
  }
  
  loading.value = true
  try {
    await createTask(formData.value)
    message.success('任务创建成功')
    emit('created')
    
    // 重置表单
    formData.value = {
      blogger_profile_url: '',
      user_cookie: '',
      scraping_rules: {
        type: 'video',
        sort_by: 'likes',
        count: 10
      }
    }
  } catch (error) {
    message.error(error.message || '创建任务失败')
  } finally {
    loading.value = false
  }
}

// 取消
const handleCancel = () => {
  emit('cancel')
}
</script>

<template>
  <n-form :model="formData" label-placement="left" label-width="auto">
    <!-- 博主链接 -->
    <n-form-item label="博主主页链接" required>
      <n-input 
        v-model:value="formData.blogger_profile_url" 
        placeholder="例如: https://www.xiaohongshu.com/user/profile/5b0ce846e8ac2b08b55e5075" 
      />
      <div class="form-tip">从小红书APP或网页版分享博主主页获取链接</div>
    </n-form-item>
    
    <!-- Cookie -->
    <n-form-item label="Cookie" required>
      <n-input
        v-model:value="formData.user_cookie"
        type="textarea"
        placeholder="请输入小红书登录后的Cookie"
        :autosize="{
          minRows: 3,
          maxRows: 5
        }"
      />
      <div class="form-tip">
        获取方法：在浏览器中登录小红书 → F12打开开发者工具 → 网络(Network)选项卡 → 
        点击任意请求 → 右侧Headers中找到Cookie → 复制完整内容
      </div>
    </n-form-item>
    
    <!-- 抓取规则 -->
    <n-card title="抓取规则设置" class="rules-card">
      <div class="rules-container">
        <!-- 内容类型 -->
        <div class="rule-item">
          <div class="rule-label">内容类型</div>
          <n-select
            v-model:value="formData.scraping_rules.type"
            :options="[
              { label: '视频', value: 'video' },
              { label: '图文', value: 'image' },
              { label: '全部', value: 'all' }
            ]"
            class="rule-select"
          />
        </div>
        
        <!-- 排序方式 -->
        <div class="rule-item">
          <div class="rule-label">排序方式</div>
          <n-select
            v-model:value="formData.scraping_rules.sort_by"
            :options="[
              { label: '点赞最多', value: 'likes' },
              { label: '最新发布', value: 'latest' }
            ]"
            class="rule-select"
          />
        </div>
        
        <!-- 抓取数量 -->
        <div class="rule-item">
          <div class="rule-label">抓取数量</div>
          <n-input-number
            v-model:value="formData.scraping_rules.count"
            :min="1"
            :max="50"
            class="rule-input"
          />
        </div>
      </div>
    </n-card>
    
    <n-divider />
    
    <!-- 表单操作按钮 -->
    <div class="form-actions">
      <n-space justify="end">
        <n-button @click="handleCancel">取消</n-button>
        <n-button type="primary" @click="handleSubmit" :loading="loading">
          {{ loading ? '创建中...' : '创建任务' }}
        </n-button>
      </n-space>
    </div>
  </n-form>
</template>

<style scoped lang="scss">
.form-tip {
  font-size: 12px;
  color: #888;
  margin-top: 4px;
  line-height: 1.5;
}

.rules-card {
  margin: 16px 0;
}

.rules-container {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 24px;
  
  @media (max-width: 768px) {
    grid-template-columns: 1fr;
  }
}

.rule-item {
  display: flex;
  flex-direction: column;
  gap: 8px;
  
  .rule-label {
    font-weight: 500;
    font-size: 14px;
    color: #333;
  }
  
  .rule-select, .rule-input {
    width: 100%;
  }
}

.form-actions {
  margin-top: 24px;
}
</style>