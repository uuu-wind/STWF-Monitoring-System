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
        :class="{ active: activeTab === 'turbine' }"
        @click="activeTab = 'turbine'"
      >
        风机信息
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

      <!-- 风机信息设置页面 -->
      <div v-if="activeTab === 'turbine'">
        <h1>风机信息设置</h1>
        
        <div class="setting-section">
          <!-- 风机选择 -->
          <div class="row setting-row">
            <div class="col-6">
              <label class="form-label">选择风机</label>
              <select 
                v-model="selectedTurbineId" 
                class="form-select"
                @change="loadTurbineConfig"
              >
                <option 
                  v-for="id in 256" 
                  :key="id" 
                  :value="'T' + String(id).padStart(3, '0')"
                >
                  T{{ String(id).padStart(3, '0') }}
                </option>
              </select>
            </div>
            <div class="col-6">
              <label class="form-label">操作</label>
              <button 
                class="btn btn-info copy-button"
                @click="showCopyModal = true"
              >
                一键复制
              </button>
            </div>
          </div>

          <!-- 风机信息 -->
          <div class="setting-row turbine-section">
            <h3>风机信息</h3>
            <div class="row">
              <div class="col-6">
                <label class="form-label">风机ID</label>
                <input 
                  v-model="turbineConfig.info.id" 
                  type="text" 
                  class="form-control"
                  placeholder="例如: T001"
                >
              </div>
              <div class="col-6">
                <label class="form-label">风机名称</label>
                <input 
                  v-model="turbineConfig.info.name" 
                  type="text" 
                  class="form-control"
                  placeholder="例如: NW1"
                >
              </div>
            </div>
            <div class="row">
              <div class="col-12">
                <label class="form-label">位置</label>
                <input 
                  v-model="turbineConfig.info.location" 
                  type="text" 
                  class="form-control"
                  placeholder="例如: IM_Zone_A"
                >
              </div>
            </div>
            <div class="row">
              <div class="col-4">
                <label class="form-label">叶片长度 (m)</label>
                <input 
                  v-model.number="turbineConfig.info.bladeLength" 
                  type="number" 
                  class="form-control"
                  placeholder="叶片长度"
                >
              </div>
              <div class="col-4">
                <label class="form-label">转子直径 (m)</label>
                <input 
                  v-model.number="turbineConfig.info.rotorDiameter" 
                  type="number" 
                  class="form-control"
                  placeholder="转子直径"
                >
              </div>
              <div class="col-4">
                <label class="form-label">额定功率 (kW)</label>
                <input 
                  v-model.number="turbineConfig.info.ratedPower" 
                  type="number" 
                  class="form-control"
                  placeholder="额定功率"
                >
              </div>
            </div>
            <div class="row">
              <div class="col-4">
                <label class="form-label">轮毂高度 (m)</label>
                <input 
                  v-model.number="turbineConfig.info.hubHeight" 
                  type="number" 
                  class="form-control"
                  placeholder="轮毂高度"
                >
              </div>
              <div class="col-4">
                <label class="form-label">叶片数量</label>
                <input 
                  v-model.number="turbineConfig.info.bladeCount" 
                  type="number" 
                  class="form-control"
                  placeholder="叶片数量"
                >
              </div>
              <div class="col-4">
                <label class="form-label">转速范围</label>
                <input 
                  v-model="turbineConfig.info.speedRange" 
                  type="text" 
                  class="form-control"
                  placeholder="例如: 3-20 RPM"
                >
              </div>
            </div>
          </div>

          <!-- 风机系统信息 -->
          <div class="setting-row turbine-system-section">
            <h3>风机系统信息</h3>
            <div class="row">
              <div class="col-6">
                <label class="form-label">型号</label>
                <input 
                  v-model="turbineConfig.system.model" 
                  type="text" 
                  class="form-control"
                  placeholder="例如: WTG-2.5MW"
                >
              </div>
              <div class="col-6">
                <label class="form-label">制造商</label>
                <input 
                  v-model="turbineConfig.system.manufacturer" 
                  type="text" 
                  class="form-control"
                  placeholder="制造商名称"
                >
              </div>
            </div>
            <div class="row">
              <div class="col-6">
                <label class="form-label">安装日期</label>
                <input 
                  v-model="turbineConfig.system.installationDate" 
                  type="text" 
                  class="form-control"
                  placeholder="例如: 2024-03-15"
                >
              </div>
              <div class="col-6">
                <label class="form-label">运行小时数</label>
                <input 
                  v-model.number="turbineConfig.system.runHours" 
                  type="number" 
                  class="form-control"
                  placeholder="运行小时数"
                >
              </div>
            </div>
            <div class="row">
              <div class="col-6">
                <label class="form-label">维护周期 (天)</label>
                <input 
                  v-model.number="turbineConfig.system.maintenanceCycle" 
                  type="number" 
                  class="form-control"
                  placeholder="维护周期"
                >
              </div>
              <div class="col-6">
                <label class="form-label">状态</label>
                <select 
                  v-model="turbineConfig.system.status" 
                  class="form-select"
                >
                  <option value="running">运行中</option>
                  <option value="stopped">停止</option>
                  <option value="maintenance">维护中</option>
                  <option value="error">故障</option>
                </select>
              </div>
            </div>
            <div class="row">
              <div class="col-12">
                <label class="form-label">状态文本</label>
                <input 
                  v-model="turbineConfig.system.statusText" 
                  type="text" 
                  class="form-control"
                  placeholder="例如: Running"
                >
              </div>
            </div>
          </div>

          <!-- 保存按钮 -->
          <div class="save-button-container">
            <button 
              class="btn btn-primary save-button"
              @click="saveTurbineConfig"
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

    <!-- 复制模态框 -->
    <div v-if="showCopyModal" class="modal-overlay" @click="showCopyModal = false">
      <div class="modal-content" @click.stop>
        <h2>选择要复制的风机</h2>
        <div class="turbine-list">
          <div 
            v-for="turbineId in availableTurbines" 
            :key="turbineId"
            class="turbine-item"
            @click="copyFromTurbine(turbineId)"
          >
            {{ turbineId }}
          </div>
        </div>
        <div class="modal-actions">
          <button class="btn btn-secondary" @click="showCopyModal = false">取消</button>
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

// 风机配置相关
const selectedTurbineId = ref('T001')
const turbineConfig = reactive({
  info: {
    id: 'T001',
    name: '',
    location: '',
    bladeLength: 0,
    rotorDiameter: 0,
    ratedPower: 0,
    hubHeight: 0,
    bladeCount: 0,
    speedRange: ''
  },
  system: {
    model: '',
    manufacturer: '',
    installationDate: '',
    runHours: 0,
    maintenanceCycle: 0,
    status: 'running',
    statusText: ''
  }
})
const showCopyModal = ref(false)
const availableTurbines = ref([])

// 监听标签页切换
watch(activeTab, (newTab) => {
  if (newTab === 'ai') {
    loadAIConfig()
  }
  if (newTab === 'turbine') {
    loadAllTurbines()
    loadTurbineConfig()
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

// 加载所有风机列表
const loadAllTurbines = async () => {
  try {
    const response = await fetch('http://localhost:8000/api/turbines/config')
    const data = await response.json()
    
    if (data.error) {
      console.error('加载风机列表失败:', data.error)
      availableTurbines.value = []
    } else {
      availableTurbines.value = Object.keys(data)
    }
  } catch (error) {
    console.error('Error loading turbines:', error)
    availableTurbines.value = []
  }
}

// 加载指定风机配置
const loadTurbineConfig = async () => {
  try {
    const response = await fetch(`http://localhost:8000/api/turbines/config/${selectedTurbineId.value}`)
    const data = await response.json()
    
    if (data.error) {
      console.error('风机不存在，显示空配置:', data.error)
      turbineConfig.info.id = selectedTurbineId.value
      turbineConfig.info.name = ''
      turbineConfig.info.location = ''
      turbineConfig.info.bladeLength = 0
      turbineConfig.info.rotorDiameter = 0
      turbineConfig.info.ratedPower = 0
      turbineConfig.info.hubHeight = 0
      turbineConfig.info.bladeCount = 0
      turbineConfig.info.speedRange = ''
      
      turbineConfig.system.model = ''
      turbineConfig.system.manufacturer = ''
      turbineConfig.system.installationDate = ''
      turbineConfig.system.runHours = 0
      turbineConfig.system.maintenanceCycle = 0
      turbineConfig.system.status = 'running'
      turbineConfig.system.statusText = ''
    } else {
      turbineConfig.info.id = data.info.id || selectedTurbineId.value
      turbineConfig.info.name = data.info.name || ''
      turbineConfig.info.location = data.info.location || ''
      turbineConfig.info.bladeLength = data.info.bladeLength || 0
      turbineConfig.info.rotorDiameter = data.info.rotorDiameter || 0
      turbineConfig.info.ratedPower = data.info.ratedPower || 0
      turbineConfig.info.hubHeight = data.info.hubHeight || 0
      turbineConfig.info.bladeCount = data.info.bladeCount || 0
      turbineConfig.info.speedRange = data.info.speedRange || ''
      
      turbineConfig.system.model = data.system.model || ''
      turbineConfig.system.manufacturer = data.system.manufacturer || ''
      turbineConfig.system.installationDate = data.system.installationDate || ''
      turbineConfig.system.runHours = data.system.runHours || 0
      turbineConfig.system.maintenanceCycle = data.system.maintenanceCycle || 0
      turbineConfig.system.status = data.system.status || 'running'
      turbineConfig.system.statusText = data.system.statusText || ''
    }
  } catch (error) {
    console.error('Error loading turbine config:', error)
    turbineConfig.info.id = selectedTurbineId.value
    turbineConfig.info.name = ''
    turbineConfig.info.location = ''
    turbineConfig.info.bladeLength = 0
    turbineConfig.info.rotorDiameter = 0
    turbineConfig.info.ratedPower = 0
    turbineConfig.info.hubHeight = 0
    turbineConfig.info.bladeCount = 0
    turbineConfig.info.speedRange = ''
    
    turbineConfig.system.model = ''
    turbineConfig.system.manufacturer = ''
    turbineConfig.system.installationDate = ''
    turbineConfig.system.runHours = 0
    turbineConfig.system.maintenanceCycle = 0
    turbineConfig.system.status = 'running'
    turbineConfig.system.statusText = ''
  }
}

// 保存风机配置
const saveTurbineConfig = async () => {
  try {
    const response = await fetch(`http://localhost:8000/api/turbines/config/${selectedTurbineId.value}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        info: turbineConfig.info,
        system: turbineConfig.system
      })
    })
    
    const data = await response.json()
    
    if (data.error) {
      console.error('保存风机配置失败:', data.error)
      alert(`保存风机配置失败: ${data.error}`)
    } else {
      console.log('保存风机配置成功:', data.message)
      alert('风机配置已保存！')
      loadAllTurbines()
    }
  } catch (error) {
    console.error('Error saving turbine config:', error)
    alert('保存风机配置失败！')
  }
}

// 从其他风机复制配置
const copyFromTurbine = async (sourceTurbineId) => {
  try {
    const response = await fetch(`http://localhost:8000/api/turbines/config/${sourceTurbineId}`)
    const data = await response.json()
    
    if (data.error) {
      console.error('复制风机配置失败:', data.error)
      alert(`复制风机配置失败: ${data.error}`)
    } else {
      turbineConfig.info.name = data.info.name || ''
      turbineConfig.info.location = data.info.location || ''
      turbineConfig.info.bladeLength = data.info.bladeLength || 0
      turbineConfig.info.rotorDiameter = data.info.rotorDiameter || 0
      turbineConfig.info.ratedPower = data.info.ratedPower || 0
      turbineConfig.info.hubHeight = data.info.hubHeight || 0
      turbineConfig.info.bladeCount = data.info.bladeCount || 0
      turbineConfig.info.speedRange = data.info.speedRange || ''
      
      turbineConfig.system.model = data.system.model || ''
      turbineConfig.system.manufacturer = data.system.manufacturer || ''
      turbineConfig.system.installationDate = data.system.installationDate || ''
      turbineConfig.system.runHours = data.system.runHours || 0
      turbineConfig.system.maintenanceCycle = data.system.maintenanceCycle || 0
      turbineConfig.system.status = data.system.status || 'running'
      turbineConfig.system.statusText = data.system.statusText || ''
      
      showCopyModal.value = false
      alert(`已从 ${sourceTurbineId} 复制配置！`)
    }
  } catch (error) {
    console.error('Error copying turbine config:', error)
    alert('复制风机配置失败！')
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

.copy-button {
  padding: 10px 30px;
  font-size: 16px;
  background-color: #17a2b8;
  border-color: #17a2b8;
}

.copy-button:hover {
  background-color: #138496;
  border-color: #117a8b;
}

.turbine-section {
  margin-top: 30px;
}

.turbine-section h3,
.turbine-system-section h3 {
  margin-bottom: 20px;
  color: #333;
}

.turbine-system-section {
  margin-top: 30px;
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal-content {
  background-color: white;
  border-radius: 8px;
  padding: 30px;
  min-width: 400px;
  max-width: 600px;
  max-height: 80vh;
  overflow-y: auto;
}

.modal-content h2 {
  margin-top: 0;
  margin-bottom: 20px;
  color: #333;
}

.turbine-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(100px, 1fr));
  gap: 10px;
  margin-bottom: 20px;
}

.turbine-item {
  padding: 15px;
  background-color: #f8f9fa;
  border: 1px solid #dee2e6;
  border-radius: 4px;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s ease;
}

.turbine-item:hover {
  background-color: #007bff;
  color: white;
  border-color: #007bff;
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
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
