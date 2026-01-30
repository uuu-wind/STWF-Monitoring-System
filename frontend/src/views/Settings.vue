<template>
  <div class="settings-container">
    <!-- 左边栏 -->
    <div class="sidebar">
      <div 
        class="sidebar-item" 
        :class="{ active: activeTab === 'home' }"
        @click="activeTab = 'home'; $router.push('/')"
      >
        首页
      </div>
      <div 
        class="sidebar-item" 
        :class="{ active: activeTab === 'receiver' }"
        @click="activeTab = 'receiver'"
      >
        接收设置
      </div>
    </div>

    <!-- 主要页面 -->
    <div class="main-content">
      <h1>接收设置</h1>
      
      <div class="setting-section">
        <!-- 接收数据类型组号和数据表名 -->
        <div class="row setting-row">
          <div class="col-6">
            <label class="form-label">接收数据类型组号</label>
            <select 
              v-model="selectedClassId" 
              class="form-select"
              @change="loadClassConfig"
            >
              <option 
                v-for="id in 256" 
                :key="id - 1" 
                :value="id - 1"
              >
                {{ id - 1 }}
              </option>
            </select>
          </div>
          <div class="col-6">
            <label class="form-label">数据表名</label>
            <input 
              v-model="classConfig.database" 
              type="text" 
              class="form-control"
              placeholder="请输入数据表名"
            >
          </div>
        </div>

        <!-- 通道设置 -->
        <div class="setting-row channels-section">
          <h3>通道设置</h3>
          <div 
            v-for="(channel, index) in classConfig.channels" 
            :key="index"
            class="row channel-row"
          >
            <div class="col-4">
              <label class="form-label">通道 {{ index }} - 数据列名</label>
              <input 
                v-model="channel.column" 
                type="text" 
                class="form-control"
                placeholder="请输入数据列名"
              >
            </div>
            <div class="col-4">
              <label class="form-label">最大值</label>
              <input 
                v-model.number="channel.range.max" 
                type="number" 
                class="form-control"
                placeholder="请输入最大值"
              >
            </div>
            <div class="col-4">
              <label class="form-label">最小值</label>
              <input 
                v-model.number="channel.range.min" 
                type="number" 
                class="form-control"
                placeholder="请输入最小值"
              >
            </div>
          </div>
        </div>

        <!-- 保存按钮 -->
        <div class="save-button-container">
          <button 
            class="btn btn-primary save-button"
            @click="saveConfig"
          >
            保存
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const activeTab = ref('receiver')
const selectedClassId = ref(0)

// 初始化配置结构
const classConfig = reactive({
  database: '',
  channels: Array.from({ length: 8 }, () => ({
    column: '',
    range: {
      min: 0,
      max: 65535
    }
  }))
})

// 从配置文件加载数据
const loadClassConfig = async () => {
  try {
    const response = await fetch(`http://localhost:8000/api/config/${selectedClassId.value}`)
    if (!response.ok) {
      throw new Error('Failed to load config')
    }
    const data = await response.json()
    
    if (data.error) {
      console.error('配置错误:', data.error)
      // 如果配置不存在，重置为默认值
      classConfig.database = ''
      classConfig.channels.forEach(channel => {
        channel.column = ''
        channel.range.min = 0
        channel.range.max = 65535
      })
    } else {
      classConfig.database = data.database || ''
      
      // 更新通道配置
      data.channels.forEach((channel, index) => {
        if (index < classConfig.channels.length) {
          classConfig.channels[index].column = channel.column || ''
          classConfig.channels[index].range.min = channel.range?.min || 0
          classConfig.channels[index].range.max = channel.range?.max || 65535
        }
      })
    }
  } catch (error) {
    console.error('Error loading config:', error)
    // 如果加载失败，重置为默认值
    classConfig.database = ''
    classConfig.channels.forEach(channel => {
      channel.column = ''
      channel.range.min = 0
      channel.range.max = 65535
    })
  }
}

// 保存配置
const saveConfig = async () => {
  try {
    const response = await fetch(`http://localhost:8000/api/config/${selectedClassId.value}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        class_id: selectedClassId.value,
        database: classConfig.database,
        channels: classConfig.channels
      })
    })
    
    const data = await response.json()
    
    if (data.error) {
      console.error('保存失败:', data.error)
      alert(`保存配置失败: ${data.error}`)
    } else {
      console.log('保存成功:', data.message)
      alert('配置已保存！')
    }
  } catch (error) {
    console.error('Error saving config:', error)
    alert('保存配置失败！')
  }
}

// 组件挂载时加载配置
onMounted(() => {
  loadClassConfig()
})
</script>

<style scoped>
.settings-container {
  display: flex;
  height: 100vh;
  overflow: hidden;
}

.sidebar {
  width: 200px;
  background-color: #f8f9fa;
  border-right: 1px solid #dee2e6;
  padding: 20px 0;
}

.sidebar-item {
  padding: 15px 20px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.sidebar-item:hover {
  background-color: #e9ecef;
}

.sidebar-item.active {
  background-color: #007bff;
  color: white;
}

.main-content {
  flex: 1;
  padding: 30px;
  overflow-y: auto;
}

.setting-section {
  margin-top: 20px;
}

.setting-row {
  margin-bottom: 20px;
}

.channels-section {
  margin-top: 30px;
}

.channel-row {
  margin-bottom: 15px;
  padding: 15px;
  background-color: #f8f9fa;
  border-radius: 8px;
}

.save-button-container {
  display: flex;
  justify-content: flex-end;
  margin-top: 30px;
}

.save-button {
  padding: 10px 30px;
  font-size: 16px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .settings-container {
    flex-direction: column;
  }

  .sidebar {
    width: 100%;
    height: auto;
    display: flex;
    border-right: none;
    border-bottom: 1px solid #dee2e6;
  }

  .sidebar-item {
    flex: 1;
    text-align: center;
  }

  .main-content {
    padding: 20px;
  }
}
</style>
