<script setup>
import { defineProps, computed, onMounted, ref } from 'vue'
import { NTabs, NTabPane, NTag, NSpin, NSpace, NProgress, NDivider, NButton, NIcon, useMessage } from 'naive-ui'
import { marked } from 'marked'
import videojs from 'video.js'
import 'video.js/dist/video-js.css'

const props = defineProps({
  note: {
    type: Object,
    required: true
  }
})

// 计算属性：将 Markdown 转换为 HTML
const analysisHtml = computed(() => {
  if (!props.note.analysis_result_text) return ''
  return marked(props.note.analysis_result_text)
})

// 计算状态显示标签类型
const statusType = computed(() => {
  if (props.note.processing_status === 'completed') return 'success'
  if (props.note.processing_status.includes('error')) return 'error'
  return 'warning'
})

// 计算状态显示文本
const statusText = computed(() => {
  const statusMap = {
    'pending_collection': '待采集',
    'collecting': '采集中',
    'collected': '已采集',
    'pending_transcript': '待转写',
    'transcribing': '转写中',
    'transcribed': '已转写',
    'pending_analysis': '待分析',
    'analyzing': '分析中',
    'completed': '已完成',
    'error_collection': '采集失败',
    'error_transcript': '转写失败',
    'error_analysis': '分析失败'
  }
  
  return statusMap[props.note.processing_status] || props.note.processing_status
})

// 计算处理进度
const processingProgress = computed(() => {
  const progressMap = {
    'pending_collection': 0,
    'collecting': 20,
    'collected': 40,
    'pending_transcript': 40,
    'transcribing': 60,
    'transcribed': 80,
    'pending_analysis': 80,
    'analyzing': 90,
    'completed': 100
  }
  
  return progressMap[props.note.processing_status] || 0
})

// 视频播放器引用（保留为兼容性检查）
const videoPlayer = ref(null)
const videoContainer = ref(null)

// 获取视频URL
const getVideoUrl = computed(() => {
  return props.note.video_url_internal || 
         (props.note.raw_note_details && props.note.raw_note_details.video_link)
})

// 尝试使用Video.js，如果失败则使用备用方案
onMounted(() => {
  if (getVideoUrl.value) {
    try {
      initializePlayer()
    } catch (e) {
      console.error('Video.js 初始化失败:', e)
    }
  }
})

// 在新窗口打开视频链接
const openVideoInNewTab = () => {
  if (getVideoUrl.value) {
    window.open(getVideoUrl.value, '_blank')
  }
}

// 初始化视频播放器
const initializePlayer = () => {
  if (videoContainer.value) {
    const videoUrl = getVideoUrl.value
    
    if (videoPlayer.value) {
      videoPlayer.value.dispose()
    }
    
    if (videoUrl) {
      videoPlayer.value = videojs(videoContainer.value, {
        controls: true,
        autoplay: false,
        preload: 'auto',
        fluid: true,
        sources: [{
          src: videoUrl,
          type: 'video/mp4'
        }]
      })
    }
  }
}
</script>

<template>
  <div class="note-detail">
    <!-- 笔记头部信息 -->
    <div class="note-header">
      <div class="note-title">
        <h3>{{ note.note_title || '无标题' }}</h3>
        <div class="note-meta">
          <n-tag :type="statusType">{{ statusText }}</n-tag>
          <span v-if="note.original_likes_count" class="note-likes">
            👍 {{ note.original_likes_count }}
          </span>
        </div>
      </div>
      
      <!-- 处理进度 -->
      <div class="note-progress">
        <div class="progress-label">处理进度</div>
        <n-progress 
          type="line" 
          :percentage="processingProgress"
          :processing="note.processing_status.includes('ing')"
          :status="note.processing_status.includes('error') ? 'error' : 'success'"
        />
      </div>
    </div>
    
    <!-- 时间轴 -->
    <div class="note-timeline">
      <div class="timeline-item" :class="{ 'completed': note.details_collected_at }">
        <div class="time">{{ note.details_collected_at ? new Date(note.details_collected_at).toLocaleString() : '未完成' }}</div>
        <div class="event">采集笔记</div>
      </div>
      <div class="timeline-item" :class="{ 'completed': note.video_downloaded_at }">
        <div class="time">{{ note.video_downloaded_at ? new Date(note.video_downloaded_at).toLocaleString() : '未完成' }}</div>
        <div class="event">下载视频</div>
      </div>
      <div class="timeline-item" :class="{ 'completed': note.transcribed_at }">
        <div class="time">{{ note.transcribed_at ? new Date(note.transcribed_at).toLocaleString() : '未完成' }}</div>
        <div class="event">转写文案</div>
      </div>
      <div class="timeline-item" :class="{ 'completed': note.analyzed_at }">
        <div class="time">{{ note.analyzed_at ? new Date(note.analyzed_at).toLocaleString() : '未完成' }}</div>
        <div class="event">AI分析</div>
      </div>
    </div>
    
    <n-divider />
    
    <!-- 笔记内容标签页 -->
    <n-tabs type="line" animated>
      <!-- 根据笔记类型显示不同标签页 -->
      <n-tab-pane v-if="note.note_type === 'video'" name="content" tab="视频内容">
        <!-- 视频播放区域 -->
        <div v-if="getVideoUrl" class="note-video">
          <!-- 播放器容器 -->
          <div data-vjs-player>
            <video ref="videoContainer" class="video-js vjs-big-play-centered"></video>
          </div>
          
          <!-- 视频播放问题提示和备用方案 -->
          <div class="video-actions">
            <div v-if="!note.video_url_internal && note.raw_note_details && note.raw_note_details.video_link" 
                class="video-source-info">
              使用原始视频链接，可能无法直接播放
            </div>
            
            <n-button 
              type="primary" 
              @click="openVideoInNewTab" 
              class="open-video-btn"
            >
              <template #icon>
                <n-icon><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="16" height="16"><path fill="none" d="M0 0h24v24H0z"/><path d="M10 6v2H5v11h11v-5h2v6a1 1 0 0 1-1 1H4a1 1 0 0 1-1-1V7a1 1 0 0 1 1-1h6zm11-3v8h-2V6.413l-7.793 7.794-1.414-1.414L17.585 5H13V3h8z" fill="currentColor"/></svg></n-icon>
              </template>
              在新窗口打开视频
            </n-button>
            
            <!-- 添加视频链接复制功能 -->
            <n-button 
              @click="() => { navigator.clipboard.writeText(getVideoUrl); $message.success('视频链接已复制到剪贴板') }"
              class="copy-link-btn"
            >
              <template #icon>
                <n-icon><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="16" height="16"><path fill="none" d="M0 0h24v24H0z"/><path d="M7 6V3a1 1 0 0 1 1-1h12a1 1 0 0 1 1 1v14a1 1 0 0 1-1 1h-3v3a1 1 0 0 1-1 1H4a1 1 0 0 1-1-1V7a1 1 0 0 1 1-1h3zm0 2H5v12h12v-2h-5a1 1 0 0 1-1-1V8zm2-2v12h12V4H9z" fill="currentColor"/></svg></n-icon>
              </template>
              复制视频链接
            </n-button>
          </div>
        </div>
        
        <!-- 无视频内容时显示 -->
        <div v-else class="note-no-content">
          <n-spin v-if="['collecting', 'pending_collection'].includes(note.processing_status)" />
          <p v-else-if="note.processing_status.includes('error_collection')">
            {{ note.error_message || '视频获取失败' }}
          </p>
          <p v-else>
            尚未获取到视频
          </p>
        </div>
      </n-tab-pane>
      
      <n-tab-pane v-if="note.note_type === 'normal'" name="content" tab="图文内容">
        <!-- 图文内容显示逻辑 -->
        <div v-if="note.raw_note_details" class="note-image-content">
          <!-- 显示笔记描述 -->
          <div v-if="note.raw_note_details.desc" class="note-description">
            <h4>笔记描述</h4>
            <p>{{ note.raw_note_details.desc }}</p>
          </div>
          
          <!-- 显示笔记图片 -->
          <div v-if="note.raw_note_details.image_urls && note.raw_note_details.image_urls.length > 0" class="note-images">
            <h4>笔记图片 ({{ note.raw_note_details.image_urls.length }}张)</h4>
            <div class="image-grid">
              <div v-for="(imageUrl, index) in note.raw_note_details.image_urls" :key="index" class="image-item">
                <img :src="imageUrl" :alt="`图片 ${index+1}`">
              </div>
            </div>
          </div>
        </div>
        <div v-else class="note-no-content">
          <n-spin v-if="['collecting', 'pending_collection'].includes(note.processing_status)" />
          <p v-else-if="note.processing_status.includes('error_collection')">
            {{ note.error_message || '图文获取失败' }}
          </p>
          <p v-else>
            尚未获取到图文内容
          </p>
        </div>
      </n-tab-pane>
      
      <!-- 文案内容标签 - 只对视频显示 -->
      <n-tab-pane v-if="note.note_type === 'video'" name="transcript" tab="文案内容">
        <div v-if="note.video_transcript_text" class="note-transcript">
          <div class="transcript-header">
            <h4>文案转写结果</h4>
            <span class="time" v-if="note.transcribed_at">
              转写于: {{ new Date(note.transcribed_at).toLocaleString() }}
            </span>
          </div>
          <div class="transcript-content">
            <p>{{ note.video_transcript_text }}</p>
          </div>
        </div>
        <div v-else class="note-no-content">
          <n-spin v-if="['transcribing', 'pending_transcript'].includes(note.processing_status)" />
          <p v-else-if="note.processing_status.includes('error_transcript')">
            {{ note.error_message || '文案转写失败' }}
          </p>
          <p v-else>
            尚未生成文案
          </p>
        </div>
      </n-tab-pane>
      
      <!-- AI分析结果标签 - 对所有类型显示 -->
      <n-tab-pane name="analysis" tab="AI分析结果">
        <div v-if="note.analysis_result_text" class="note-analysis">
          <div class="analysis-header">
            <h4>内容分析</h4>
            <span class="time" v-if="note.analyzed_at">
              分析于: {{ new Date(note.analyzed_at).toLocaleString() }}
            </span>
          </div>
          <div v-html="analysisHtml" class="markdown-content"></div>
        </div>
        <div v-else class="note-no-content">
          <n-spin v-if="['analyzing', 'pending_analysis'].includes(note.processing_status)" />
          <p v-else-if="note.processing_status.includes('error_analysis')">
            {{ note.error_message || 'AI分析失败' }}
          </p>
          <p v-else>
            尚未生成分析结果
          </p>
        </div>
      </n-tab-pane>
      
      <n-tab-pane name="details" tab="笔记详情">
        <div class="note-raw-details">
          <div v-if="note.raw_note_details">
            <div class="detail-item" v-for="(value, key) in note.raw_note_details" :key="key">
              <div class="detail-label">{{ key }}</div>
              <div class="detail-value">
                <pre v-if="typeof value === 'object'">{{ JSON.stringify(value, null, 2) }}</pre>
                <span v-else>{{ value }}</span>
              </div>
            </div>
          </div>
          <div v-else class="note-no-content">
            <p>暂无原始数据</p>
          </div>
        </div>
      </n-tab-pane>
    </n-tabs>
    
    <!-- 错误信息显示 -->
    <div v-if="note.error_message" class="note-error">
      <n-divider />
      <div class="error-title">处理过程中的错误</div>
      <div class="error-message">{{ note.error_message }}</div>
    </div>
  </div>
</template>

<style scoped lang="scss">
.note-detail {
  padding: 10px;
  
  .note-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    margin-bottom: 20px;
    
    .note-title {
      h3 {
        margin: 0 0 10px 0;
        font-size: 18px;
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
    
    .note-progress {
      width: 200px;
      
      .progress-label {
        font-size: 14px;
        color: #666;
        margin-bottom: 5px;
      }
    }
  }
  
  .video-source-info {
  text-align: center;
  padding: 8px;
  font-size: 12px;
  color: #ff9800;
  background-color: #fff8e1;
  border-radius: 0 0 4px 4px;
  margin-top: -5px;
  }

  .note-timeline {
    display: flex;
    justify-content: space-between;
    margin-bottom: 20px;
    
    .timeline-item {
      display: flex;
      flex-direction: column;
      align-items: center;
      position: relative;
      width: 25%;
      
      &:not(:last-child)::after {
        content: '';
        position: absolute;
        top: 10px;
        right: -50%;
        width: 100%;
        height: 2px;
        background-color: #ddd;
        z-index: 1;
      }
      
      &::before {
        content: '';
        width: 20px;
        height: 20px;
        border-radius: 50%;
        background-color: #ddd;
        margin-bottom: 8px;
        z-index: 2;
      }
      
      &.completed {
        &::before {
          background-color: #18a058;
        }
        
        &:not(:last-child)::after {
          background-color: #18a058;
        }
        
        .time, .event {
          color: #18a058;
        }
      }
      
      .time {
        font-size: 12px;
        color: #999;
        margin-bottom: 4px;
      }
      
      .event {
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
      background-color: #000;
    }
  }
  
  .note-no-content {
    padding: 40px;
    text-align: center;
    color: #999;
    background-color: #f5f5f5;
    border-radius: 4px;
    min-height: 200px;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
  }
  
  .note-transcript, .note-analysis {
    background-color: #f9f9f9;
    border-radius: 4px;
    overflow: hidden;
    
    .transcript-header, .analysis-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 12px 16px;
      background-color: #f0f0f0;
      
      h4 {
        margin: 0;
        font-size: 16px;
        color: #333;
      }
      
      .time {
        font-size: 12px;
        color: #666;
      }
    }
    
    .transcript-content {
      padding: 16px;
      white-space: pre-wrap;
      line-height: 1.6;
      color: #333;
    }
  }
  
  /* Markdown 内容样式 */
  :deep(.markdown-content) {
    padding: 16px;
    
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
  
  .note-raw-details {
    padding: 16px;
    
    .detail-item {
      margin-bottom: 12px;
      
      .detail-label {
        font-weight: 500;
        margin-bottom: 4px;
        color: #666;
      }
      
      .detail-value {
        padding: 8px;
        background-color: #f5f5f5;
        border-radius: 4px;
        overflow-x: auto;
        
        pre {
          margin: 0;
          white-space: pre-wrap;
          font-family: monospace;
        }
      }
    }
  }
  
  .note-error {
    .error-title {
      font-weight: 500;
      color: #d03050;
      margin-bottom: 8px;
    }
    
    .error-message {
      padding: 12px;
      background-color: #ffebec;
      border-radius: 4px;
      color: #d03050;
      white-space: pre-wrap;
    }
  }
  
  .video-actions {
    display: flex;
    flex-direction: column;
    gap: 10px;
    margin-top: 12px;
    
    .open-video-btn, .copy-link-btn {
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 8px;
    }
    
    .open-video-btn {
      background-color: #18a058;
      color: white;
      
      &:hover {
        background-color: #0c7a43;
      }
    }
    
    .copy-link-btn {
      background-color: #f5f5f5;
      color: #333;
      
      &:hover {
        background-color: #e0e0e0;
      }
    }
  }
}

/* 添加图文内容样式 */
.note-image-content {
  .note-description {
    background-color: #f9f9f9;
    padding: 16px;
    border-radius: 4px;
    margin-bottom: 20px;
    
    h4 {
      margin-top: 0;
      margin-bottom: 10px;
      color: #333;
    }
    
    p {
      margin: 0;
      line-height: 1.6;
      white-space: pre-wrap;
    }
  }
  
  .note-images {
    h4 {
      margin-bottom: 16px;
      color: #333;
    }
    
    .image-grid {
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
      gap: 16px;
      
      .image-item {
        img {
          width: 100%;
          height: auto;
          border-radius: 4px;
          box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }
      }
    }
  }
}
</style>