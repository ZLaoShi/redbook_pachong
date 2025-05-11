<script setup>
import { defineProps, computed } from 'vue'
import { NTabs, NTabPane, NTag } from 'naive-ui'
import { marked } from 'marked' // 导入 marked

const props = defineProps({
  note: {
    type: Object,
    required: true
  }
})

// 计算属性：将 Markdown 转换为 HTML
const analysisHtml = computed(() => {
  if (!props.note.analysis_result_text) return ''
  return marked(props.note.analysis_result_text) // 解析 Markdown
})
</script>

<template>
  <div class="note-detail">
    <div class="note-header">
      <h3>{{ note.note_title || '无标题' }}</h3>
      <div class="note-meta">
        <n-tag :type="note.processing_status === 'completed' ? 'success' : note.processing_status.includes('error') ? 'error' : 'warning'">
          {{ note.processing_status }}
        </n-tag>
        <span v-if="note.original_likes_count" class="note-likes">
          👍 {{ note.original_likes_count }}
        </span>
      </div>
    </div>
    
    <n-tabs type="line">
      <n-tab-pane name="content" tab="内容">
        <div v-if="note.video_url" class="note-video">
          <video controls :src="note.video_url"></video>
        </div>
        <div v-else-if="note.video_url_internal" class="note-video">
          <video controls :src="note.video_url_internal"></video>
        </div>
        <div v-else class="note-no-video">
          <p v-if="note.processing_status.includes('error')">
            {{ note.error_message || '视频获取失败' }}
          </p>
          <p v-else>
            尚未获取到视频
          </p>
        </div>
      </n-tab-pane>
      
      <n-tab-pane name="transcript" tab="文案">
        <div v-if="note.video_transcript_text" class="note-transcript">
          <p>{{ note.video_transcript_text }}</p>
        </div>
        <div v-else class="note-no-transcript">
          <p v-if="note.processing_status === 'error_transcript'">
            {{ note.error_message || '文案转写失败' }}
          </p>
          <p v-else>
            尚未生成文案
          </p>
        </div>
      </n-tab-pane>
      
      <n-tab-pane name="analysis" tab="分析结果">
        <div v-if="note.analysis_result_text" class="note-analysis">
          <!-- 使用 v-html 渲染转换后的 HTML -->
          <div v-html="analysisHtml" class="markdown-content"></div>
        </div>
        <div v-else class="note-no-analysis">
          <p v-if="note.processing_status === 'error_analysis'">
            {{ note.error_message || 'AI分析失败' }}
          </p>
          <p v-else>
            尚未生成分析结果
          </p>
        </div>
      </n-tab-pane>
    </n-tabs>
  </div>
</template>

<style scoped lang="scss">
.note-detail {
  .note-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 16px;
    
    h3 {
      margin: 0;
    }
    
    .note-meta {
      display: flex;
      align-items: center;
      gap: 12px;
      
      .note-likes {
        font-size: 14px;
        color: #666;
      }
    }
  }
  
  .note-video {
    margin-bottom: 16px;
    
    video {
      width: 100%;
      max-height: 400px;
      border-radius: 4px;
    }
  }
  
  .note-no-video,
  .note-no-transcript,
  .note-no-analysis {
    padding: 20px;
    text-align: center;
    color: #999;
    background-color: #f5f5f5;
    border-radius: 4px;
  }
  
  .note-transcript,
  .note-analysis {
    padding: 16px;
    background-color: #f5f5f5;
    border-radius: 4px;
    white-space: pre-wrap;
  }
  
  /* Markdown 内容样式 */
  :deep(.markdown-content) {
    h3 {
      margin-top: 20px;
      margin-bottom: 10px;
      color: #18a058;
      border-bottom: 1px solid #eee;
      padding-bottom: 5px;
    }
    
    strong {
      font-weight: bold;
      color: #333;
    }
    
    ul {
      padding-left: 20px;
    }
    
    li {
      margin-bottom: 5px;
    }
    
    hr {
      margin: 15px 0;
      border: 0;
      border-top: 1px dashed #ddd;
    }
  }
}
</style>