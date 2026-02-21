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
      <div 
        class="sidebar-item" 
        :class="{ active: activeTab === 'ai' }"
        @click="activeTab = 'ai'"
      >
        AI配置
      </div>
    </div>

    <!-- 主要页面 -->
    <div class="main-content">
      <!-- 接收设置页面 -->
      <div v-if="activeTab === 'receiver'">
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

          <!-- 计算通道设置 -->
          <div class="setting-row calculate-section">
            <h3>计算通道设置</h3>
            <div 
              v-for="(calc, index) in classConfig.calculate" 
              :key="index"
              class="row calculate-row"
            >
              <div class="col-6">
                <label class="form-label">计算通道 {{ index + 1 }} - 数据列名</label>
                <input 
                  v-model="calc.column" 
                  type="text" 
                  class="form-control"
                  placeholder="请输入计算结果的列名"
                >
              </div>
              <div class="col-6">
                <label class="form-label">计算表达式</label>
                <input 
                  v-model="calc.function" 
                  type="text" 
                  class="form-control"
                  placeholder="例如: CH0+CH2+3*(CH4+5)"
                >
                <small class="form-text text-muted">
                  支持通道引用(CH0-CH7)、四则运算和小括号
                </small>
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

      <!-- AI配置页面 -->
      <div v-if="activeTab === 'ai'">
        <h1>AI配置</h1>
        
        <div class="setting-section">
          <div class="setting-row">
            <label class="form-label">纬度</label>
            <input 
              v-model="aiConfig.latitude" 
              type="text" 
              class="form-control"
              placeholder="请输入纬度"
            >
          </div>
          <div class="setting-row">
            <label class="form-label">经度</label>
            <input 
              v-model="aiConfig.longitude" 
              type="text" 
              class="form-control"
              placeholder="请输入经度"
            >
          </div>
          <div class="setting-row">
            <label class="form-label">风机整体朝向</label>
            <input 
              v-model="aiConfig.turbine_orientation" 
              type="text" 
              class="form-control"
              placeholder="请输入风机整体朝向"
            >
          </div>
          <div class="save-button-container">
            <button 
              class="btn btn-primary save-button"
              @click="saveAIConfig"
            >
              保存AI配置
            </button>
            <button 
              class="btn btn-success train-button"
              @click="trainModel"
              :disabled="isTraining"
            >
              {{ isTraining ? '训练中...' : '训练模型' }}
            </button>
          </div>
          
          <!-- 训练结果显示 -->
          <div v-if="trainResult" class="train-result">
            <h3>训练结果</h3>
            <div class="result-item">
              <span class="result-label">状态:</span>
              <span class="result-value" :class="{ success: trainResult.success, error: !trainResult.success }">
                {{ trainResult.success ? '成功' : '失败' }}
              </span>
            </div>
            <div class="result-item">
              <span class="result-label">消息:</span>
              <span class="result-value">{{ trainResult.message }}</span>
            </div>
            <div v-if="trainResult.rows" class="result-item">
              <span class="result-label">训练数据行数:</span>
              <span class="result-value">{{ trainResult.rows }}</span>
            </div>
            <div v-if="trainResult.mae !== null" class="result-item">
              <span class="result-label">平均绝对误差 (MAE):</span>
              <span class="result-value">{{ trainResult.mae?.toFixed(2) }} W</span>
            </div>
            <div v-if="trainResult.rmse !== null" class="result-item">
              <span class="result-label">均方根误差 (RMSE):</span>
              <span class="result-value">{{ trainResult.rmse?.toFixed(2) }} W</span>
            </div>
            <div v-if="trainResult.r2 !== null" class="result-item">
              <span class="result-label">R²分数:</span>
              <span class="result-value">{{ trainResult.r2?.toFixed(4) }}</span>
            </div>
            <div v-if="trainResult.model_weight !== null" class="result-item">
              <span class="result-label">最优权重:</span>
              <span class="result-value">{{ trainResult.model_weight?.toFixed(4) }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, watch } from 'vue'
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
  })),
  calculate: Array.from({ length: 2 }, () => ({
    column: '',
    function: ''
  }))
})

// AI配置
const aiConfig = reactive({
  latitude: '',
  longitude: '',
  turbine_orientation: ''
})

// 训练相关状态
const isTraining = ref(false)
const trainResult = ref(null)

// 监听标签页切换
watch(activeTab, (newTab) => {
  if (newTab === 'ai') {
    loadAIConfig()
  }
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
      classConfig.database = ''
      classConfig.channels.forEach(channel => {
        channel.column = ''
        channel.range.min = 0
        channel.range.max = 65535
      })
      classConfig.calculate.forEach(calc => {
        calc.column = ''
        calc.function = ''
      })
    } else {
      classConfig.database = data.database || ''
      
      data.channels.forEach((channel, index) => {
        if (index < classConfig.channels.length) {
          classConfig.channels[index].column = channel.column || ''
          classConfig.channels[index].range.min = channel.range?.min || 0
          classConfig.channels[index].range.max = channel.range?.max || 65535
        }
      })
      
      if (data.calculate && Array.isArray(data.calculate)) {
        data.calculate.forEach((calc, index) => {
          if (index < classConfig.calculate.length) {
            classConfig.calculate[index].column = calc.column || ''
            classConfig.calculate[index].function = calc.function || ''
          }
        })
      } else {
        classConfig.calculate.forEach(calc => {
          calc.column = ''
          calc.function = ''
        })
      }
    }
  } catch (error) {
    console.error('Error loading config:', error)
    classConfig.database = ''
    classConfig.channels.forEach(channel => {
      channel.column = ''
      channel.range.min = 0
      channel.range.max = 65535
    })
    classConfig.calculate.forEach(calc => {
      calc.column = ''
      calc.function = ''
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
        channels: classConfig.channels,
        calculate: classConfig.calculate
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

// 加载AI配置
const loadAIConfig = async () => {
  try {
    const response = await fetch('http://localhost:8000/api/ai/config')
    if (!response.ok) {
      throw new Error('Failed to load AI config')
    }
    const data = await response.json()
    
    if (data.error) {
      console.error('AI配置错误:', data.error)
      aiConfig.latitude = ''
      aiConfig.longitude = ''
      aiConfig.turbine_orientation = ''
    } else {
      aiConfig.latitude = data.latitude || ''
      aiConfig.longitude = data.longitude || ''
      aiConfig.turbine_orientation = data.turbine_orientation || ''
    }
  } catch (error) {
    console.error('Error loading AI config:', error)
    aiConfig.latitude = ''
    aiConfig.longitude = ''
    aiConfig.turbine_orientation = ''
  }
}

// 保存AI配置
const saveAIConfig = async () => {
  try {
    const response = await fetch('http://localhost:8000/api/ai/config', {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        latitude: aiConfig.latitude,
        longitude: aiConfig.longitude,
        turbine_orientation: aiConfig.turbine_orientation
      })
    })
    
    const data = await response.json()
    
    if (data.error) {
      console.error('保存AI配置失败:', data.error)
      alert(`保存AI配置失败: ${data.error}`)
    } else {
      console.log('保存AI配置成功:', data.message)
      alert('AI配置已保存！')
    }
  } catch (error) {
    console.error('Error saving AI config:', error)
    alert('保存AI配置失败！')
  }
}

// 训练模型
const trainModel = async () => {
  isTraining.value = true
  trainResult.value = null
  
  try {
    const response = await fetch('http://localhost:8000/api/ai/train', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        turbine_id: 'T001',
        use_test_data: false
      })
    })
    
    const data = await response.json()
    trainResult.value = data
    
    if (data.success) {
      console.log('模型训练成功:', data)
      alert(`模型训练成功！\nMAE: ${data.mae?.toFixed(2)} W\nRMSE: ${data.rmse?.toFixed(2)} W\nR²: ${data.r2?.toFixed(4)}`)
    } else {
      console.error('模型训练失败:', data.message)
      alert(`模型训练失败: ${data.message}`)
    }
  } catch (error) {
    console.error('Error training model:', error)
    trainResult.value = {
      success: false,
      message: `训练失败: ${error.message}`,
      turbine_id: 'T001'
    }
    alert('模型训练失败！')
  } finally {
    isTraining.value = false
  }
}
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

.calculate-section {
  margin-top: 30px;
}

.calculate-row {
  margin-bottom: 15px;
  padding: 15px;
  background-color: #e3f2fd;
  border-radius: 8px;
  border-left: 4px solid #2196f3;
}

.save-button-container {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 30px;
}

.save-button {
  padding: 10px 30px;
  font-size: 16px;
}

.train-button {
  padding: 10px 30px;
  font-size: 16px;
  background-color: #28a745;
  border-color: #28a745;
}

.train-button:hover {
  background-color: #218838;
  border-color: #1e7e34;
}

.train-button:disabled {
  background-color: #6c757d;
  border-color: #6c757d;
  cursor: not-allowed;
}

.train-result {
  margin-top: 30px;
  padding: 20px;
  background-color: #f8f9fa;
  border-radius: 8px;
  border-left: 4px solid #007bff;
}

.train-result h3 {
  margin-top: 0;
  margin-bottom: 20px;
  color: #333;
}

.result-item {
  display: flex;
  justify-content: space-between;
  padding: 10px 0;
  border-bottom: 1px solid #dee2e6;
}

.result-item:last-child {
  border-bottom: none;
}

.result-label {
  font-weight: 600;
  color: #495057;
}

.result-value {
  color: #212529;
}

.result-value.success {
  color: #28a745;
  font-weight: 600;
}

.result-value.error {
  color: #dc3545;
  font-weight: 600;
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
