<template>
  <div class="chat-assistant">
    <!-- 悬浮球 -->
    <div 
      class="chat-float-button" 
      :class="{ active: showChatWindow }"
      @click="toggleChatWindow"
    >
      <el-icon v-if="!showChatWindow" class="chat-icon">
        <ChatRound />
      </el-icon>
      <el-icon v-else class="chat-icon">
        <Close />
      </el-icon>
    </div>

    <!-- 对话窗口 -->
    <div 
      class="chat-window" 
      :class="{ active: showChatWindow }"
    >
      <!-- 窗口头部 -->
      <div class="chat-header">
        <h3>智能助手</h3>
        <el-button 
          type="text" 
          size="small"
          @click="toggleChatWindow"
        >
          <el-icon><Close /></el-icon>
        </el-button>
      </div>

      <!-- 对话记录 -->
      <div class="chat-messages">
        <div 
          v-for="(message, index) in messages" 
          :key="index"
          class="message"
          :class="{ user: message.sender === 'user', assistant: message.sender === 'assistant' }"
        >
          <div class="message-content">
            {{ message.content }}
          </div>
          <div class="message-time">
            {{ message.time }}
          </div>
        </div>
        <div v-if="isLoading" class="loading-message">
          <el-icon class="is-loading"><Loading /></el-icon>
          <span>正在思考...</span>
        </div>
      </div>

      <!-- 输入区域 -->
      <div class="chat-input-area">
        <el-input
          v-model="inputMessage"
          placeholder="请输入您的问题..."
          @keyup.enter="sendMessage"
        />
        <el-button 
          type="primary"
          @click="sendMessage"
          :disabled="!inputMessage.trim()"
        >
          发送
        </el-button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { ChatRound, Close, Loading } from '@element-plus/icons-vue'

const showChatWindow = ref(false)
const messages = ref([])
const inputMessage = ref('')
const isLoading = ref(false)

// 切换对话窗口显示/隐藏
const toggleChatWindow = () => {
  showChatWindow.value = !showChatWindow.value
  // 首次打开时添加欢迎消息
  if (showChatWindow.value && messages.value.length === 0) {
    addAssistantMessage('您好！我是风电场监控系统的智能助手，有什么可以帮您的吗？')
  }
}

// 添加助手消息
const addAssistantMessage = (content) => {
  messages.value.push({
    sender: 'assistant',
    content,
    time: new Date().toLocaleTimeString()
  })
  // 滚动到底部
  scrollToBottom()
}

// 添加用户消息
const addUserMessage = (content) => {
  messages.value.push({
    sender: 'user',
    content,
    time: new Date().toLocaleTimeString()
  })
  // 滚动到底部
  scrollToBottom()
}

// 滚动到底部
const scrollToBottom = () => {
  setTimeout(() => {
    const messagesContainer = document.querySelector('.chat-messages')
    if (messagesContainer) {
      messagesContainer.scrollTop = messagesContainer.scrollHeight
    }
  }, 100)
}

// 发送消息
const sendMessage = async () => {
  const message = inputMessage.value.trim()
  if (!message) return

  // 添加用户消息
  addUserMessage(message)
  inputMessage.value = ''

  // 显示加载状态
  isLoading.value = true

  try {
    // 调用后端API
    const response = await fetch('http://localhost:8000/api/chat', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ message })
    })

    if (!response.ok) {
      throw new Error('API调用失败')
    }

    const data = await response.json()
    // 添加助手回复
    addAssistantMessage(data.response)
  } catch (error) {
    console.error('发送消息失败:', error)
    addAssistantMessage('抱歉，我暂时无法回复您的问题，请稍后再试。')
  } finally {
    isLoading.value = false
  }
}

// 点击外部关闭窗口
const handleClickOutside = (event) => {
  const chatAssistant = document.querySelector('.chat-assistant')
  if (chatAssistant && !chatAssistant.contains(event.target)) {
    showChatWindow.value = false
  }
}

onMounted(() => {
  document.addEventListener('click', handleClickOutside)
})

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
})
</script>

<style scoped>
.chat-assistant {
  position: fixed;
  right: 10px;
  bottom: 10px;
  z-index: 1000;
}

.chat-float-button {
  width: 60px;
  height: 60px;
  border-radius: 50%;
  background-color: #409eff;
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.15);
  transition: all 0.3s ease;
  font-size: 24px;
}

.chat-float-button:hover {
  transform: scale(1.1);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.2);
}

.chat-float-button.active {
  background-color: #606266;
}

.chat-icon {
  pointer-events: none;
}

.chat-window {
  position: fixed;
  right: 70px;
  bottom: 10px;
  width: 20vw;
  height: 50vh;
  background-color: white;
  border-radius: 10px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
  opacity: 0;
  transition: all 0.3s ease;
  pointer-events: none;
  z-index: 1001;
}

.chat-window.active {
  opacity: 1;
  pointer-events: auto;
}

.chat-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px 20px;
  border-bottom: 1px solid #ebeef5;
  background-color: #fafafa;
  border-radius: 10px 10px 0 0;
}

.chat-header h3 {
  margin: 0;
  font-size: 16px;
  font-weight: 500;
  color: #303133;
}

.chat-messages {
  height: calc(50vh - 110px);
  overflow-y: auto;
  padding: 20px;
  background-color: #fafafa;
}

.message {
  margin-bottom: 15px;
  max-width: 80%;
}

.message.user {
  margin-left: auto;
}

.message.assistant {
  margin-right: auto;
}

.message-content {
  padding: 10px 15px;
  border-radius: 8px;
  word-wrap: break-word;
}

.message.user .message-content {
  background-color: #409eff;
  color: white;
  border-bottom-right-radius: 2px;
}

.message.assistant .message-content {
  background-color: white;
  color: #303133;
  border: 1px solid #ebeef5;
  border-bottom-left-radius: 2px;
}

.message-time {
  font-size: 12px;
  color: #909399;
  margin-top: 5px;
  text-align: right;
}

.loading-message {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 10px;
  color: #606266;
}

.loading-message .is-loading {
  margin-right: 8px;
}

.chat-input-area {
  display: flex;
  padding: 15px;
  border-top: 1px solid #ebeef5;
  background-color: white;
  border-radius: 0 0 10px 10px;
}

.chat-input-area .el-input {
  flex: 1;
  margin-right: 10px;
}

/* 滚动条样式 */
.chat-messages::-webkit-scrollbar {
  width: 6px;
}

.chat-messages::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 3px;
}

.chat-messages::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 3px;
}

.chat-messages::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .chat-window {
    width: 90vw;
    height: 70vh;
  }

  .chat-messages {
    height: calc(70vh - 110px);
  }
}
</style>
