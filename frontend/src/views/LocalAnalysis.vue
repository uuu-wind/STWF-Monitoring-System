<template>
  <div class="local-analysis-container">
    <!-- 工具栏 -->
    <div class="toolbar">
      <el-card shadow="hover">
        <div class="toolbar-content">
          <div class="toolbar-left">
            <div class="logo">
              <el-icon size="24"><WindPower /></el-icon>
              <span class="logo-text">风电智能监控平台</span>
            </div>
            <div class="nav-menu">
              <router-link to="/" class="nav-item">总体预览</router-link>
              <router-link to="/local-analysis" class="nav-item active">局部分析</router-link>
            </div>
          </div>
          <div class="toolbar-right">
            <el-button type="primary" @click="refreshData">
              刷新数据
            </el-button>
            <el-button>
              系统设置
            </el-button>
          </div>
        </div>
      </el-card>
    </div>

    <!-- 主要内容区域 -->
    <div class="main-content">
      <!-- 左侧区域（占25%宽度） -->
      <div class="left-content">
        <!-- 上部分：风机名称和机械参数（高度25%） -->
        <div class="left-top-section">
          <el-card shadow="hover">
            <template #header>
              <div class="card-header">
                <span>风机信息</span>
              </div>
            </template>
            <div class="turbine-info">
              <h3 class="turbine-name">{{ turbineInfo.name }}</h3>
              <p class="turbine-location">{{ turbineInfo.location }}</p>
              <div class="mechanical-params">
                <div class="param-item">
                  <span class="param-label">叶片长度</span>
                  <span class="param-value">{{ turbineInfo.bladeLength }} m</span>
                </div>
                <div class="param-item">
                  <span class="param-label">转子直径</span>
                  <span class="param-value">{{ turbineInfo.rotorDiameter }} m</span>
                </div>
                <div class="param-item">
                  <span class="param-label">额定功率</span>
                  <span class="param-value">{{ turbineInfo.ratedPower }} kW</span>
                </div>
                <div class="param-item">
                  <span class="param-label">轮毂高度</span>
                  <span class="param-value">{{ turbineInfo.hubHeight }} m</span>
                </div>
                <div class="param-item">
                  <span class="param-label">叶片数量</span>
                  <span class="param-value">{{ turbineInfo.bladeCount }}</span>
                </div>
                <div class="param-item">
                  <span class="param-label">转速范围</span>
                  <span class="param-value">{{ turbineInfo.speedRange }}</span>
                </div>
              </div>
            </div>
          </el-card>
        </div>

        <!-- 中部分：发电量和功率数据（高度25%） -->
        <div class="left-middle-section">
          <el-card shadow="hover">
            <template #header>
              <div class="card-header">
                <span>运行数据</span>
              </div>
            </template>
            <div class="power-data">
              <div class="data-grid">
                <div class="data-item">
                  <span class="data-label">今日发电量</span>
                  <span class="data-value">{{ runtimeData.dailyGeneration.toFixed(2) }} 千瓦时</span>
                </div>
                <div class="data-item">
                  <span class="data-label">输出功率</span>
                  <span class="data-value">{{ runtimeData.activePower.toFixed(2) }} kW</span>
                </div>
                <div class="data-item">
                  <span class="data-label">运行状态</span>
                  <el-tag :type="runtimeData.status === 'running' ? 'success' : 'warning'">{{ runtimeData.statusText }}</el-tag>
                </div>
              </div>
            </div>
          </el-card>
        </div>

        <!-- 下部分：风机系统信息（高度22%） -->
        <div class="left-bottom-section">
          <el-card shadow="hover">
            <template #header>
              <div class="card-header">
                <span>系统信息</span>
              </div>
            </template>
            <div class="system-info">
              <div class="info-grid">
                <div class="info-item">
                  <span class="info-label">风机型号</span>
                  <span class="info-value">{{ systemInfo.model }}</span>
                </div>
                <div class="info-item">
                  <span class="info-label">制造商</span>
                  <span class="info-value">{{ systemInfo.manufacturer }}</span>
                </div>
                <div class="info-item">
                  <span class="info-label">安装日期</span>
                  <span class="info-value">{{ systemInfo.installationDate }}</span>
                </div>
              </div>
            </div>
          </el-card>
        </div>
      </div>

      <!-- 中间底部区域：故障信息 -->
      <div class="middle-bottom-section">
        <el-card shadow="hover">
          <template #header>
            <div class="card-header">
              <span>故障信息</span>
            </div>
          </template>
          <div class="fault-info-content">
            <div v-if="faultInfo.length > 0" class="fault-list">
              <div v-for="(fault, index) in faultInfo" :key="index" class="fault-item">
                <div class="fault-header">
                  <span class="fault-title">{{ fault.title }}</span>
                  <el-tag :type="fault.type === 'error' ? 'danger' : 'warning'" size="small">
                    {{ fault.type === 'error' ? '严重' : '警告' }}
                  </el-tag>
                </div>
                <div class="fault-description">{{ fault.description }}</div>
                <div class="fault-time">{{ fault.timestamp }}</div>
              </div>
            </div>
            <div v-else class="no-fault">
              <el-icon size="40" color="#67C23A"><SuccessFilled /></el-icon>
              <p>当前无故障信息</p>
            </div>
          </div>
        </el-card>
      </div>
      
      <!-- 中间区域：风机细节图（three.js网格形式） -->
      <div class="center-content">
        <div ref="threeJsContainer" class="three-js-container"></div>
      </div>

      <!-- 右侧区域（占20%宽度） -->
      <div class="right-content">
        <!-- 上部分：风速风向图（罗盘形式，占1/3高度） -->
        <div class="chart-item wind-chart">
          <el-card shadow="hover">
            <template #header>
              <div class="card-header">
                <span>风速风向</span>
              </div>
            </template>
            <div class="wind-compass">
              <div class="compass-circle">
                <div class="compass-rose">
                  <div class="compass-direction">N</div>
                  <div class="compass-direction">E</div>
                  <div class="compass-direction">S</div>
                  <div class="compass-direction">W</div>
                </div>
                <div class="wind-indicator" :style="{ transform: `rotate(${windData.direction}deg)` }">
                  <div class="wind-arrow"></div>
                </div>
                <div class="wind-speed">{{ windData.speed }} m/s</div>
              </div>
            </div>
          </el-card>
        </div>

        <!-- 中部分：发电量折线图（占1/3高度） -->
        <div class="chart-item power-chart">
          <el-card shadow="hover">
            <template #header>
              <div class="card-header">
                <span>发电量趋势</span>
              </div>
            </template>
            <div class="chart-container">
              <div ref="powerChart" class="chart"></div>
            </div>
          </el-card>
        </div>

        <!-- 下部分：告警统计（占1/3高度） -->
        <div class="chart-item alert-chart">
          <el-card shadow="hover">
            <template #header>
              <div class="card-header">
                <span>告警统计</span>
              </div>
            </template>
            <div class="alert-stats">
              <div ref="alertChart" class="chart"></div>
            </div>
          </el-card>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, onUnmounted, nextTick, computed } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import * as echarts from 'echarts'
import axios from 'axios'
import * as THREE from 'three'
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls'
import { STLLoader } from 'three/examples/jsm/loaders/STLLoader'
import { WindPower, SuccessFilled } from '@element-plus/icons-vue'

// API基础URL
const API_BASE_URL = 'http://localhost:8000/api'

// 创建axios实例
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  }
})

export default {
  name: 'LocalAnalysis',
  setup() {
    // 获取路由参数
    const route = useRoute()
    
    // 从路由参数中获取风机ID，默认为T001
    const turbineId = computed(() => {
      const id = route.params.turbineId || route.query.id || 'T001'
      return id.toUpperCase()
    })
    
    // 根据风机ID获取风机名称
    const turbineName = computed(() => {
      const id = turbineId.value.toLowerCase()
      const num = id.replace('t', '').replace('t00', '').replace('t0', '')
      return `风机${num}`
    })
    
    // 响应式数据
    const turbineInfo = ref({ 
      name: turbineName.value,
      location: '',
      bladeLength: 0,
      rotorDiameter: 0,
      ratedPower: 0,
      hubHeight: 0,
      bladeCount: 0,
      speedRange: ''
    })
    const runtimeData = ref({ 
      dailyGeneration: 0,
      activePower: 0,
      reactivePower: 0,
      apparentPower: 0,
      status: 'running',
      statusText: '运行中'
    })
    const systemInfo = ref({ 
      model: '',
      manufacturer: '',
      installationDate: '',
    })
    const windData = ref({ 
      speed: 0,
      direction: 0
    })
    const alertStats = ref({ 
      critical: 0,
      major: 0,
      minor: 0
    })
    const powerTrend = ref({ 
      hours: [],
      power: []
    })
    const faultInfo = ref([])
    const loading = ref(false)

    // 图表引用
    const powerChart = ref(null)
    const alertChart = ref(null)
    const threeJsContainer = ref(null)

    // 图表实例
    let powerChartInstance = null
    let alertChartInstance = null

    // Three.js相关
    let scene = null
    let camera = null
    let renderer = null
    let controls = null
    let animationId = null
    let fanGroup = null // 用于存储风扇模型的父物体，控制旋转
    let fanGroup2 = null
    let isUnmounted = false

    // 格式化功率数据
    const formatPower = (power) => {
      if (power >= 1000) {
        return (power / 1000).toFixed(1) + ' MW'
      }
      return power.toFixed(0) + ' kW'
    }

    // 获取风机信息
    const fetchTurbineInfo = async () => {
      try {
        const response = await apiClient.get(`/turbines/${turbineId.value}`)
        turbineInfo.value = response.data
      } catch (error) {
        console.error('获取风机信息失败:', error)
        ElMessage.error('获取风机信息失败')
      }
    }

    // 获取运行数据
    const fetchRuntimeData = async () => {
      try {
        const response = await apiClient.get(`/turbines/${turbineId.value}/runtime`)
        runtimeData.value = response.data
      } catch (error) {
        console.error('获取运行数据失败:', error)
        ElMessage.error('获取运行数据失败')
      }
    }

    // 获取系统信息
    const fetchSystemInfo = async () => {
      try {
        const response = await apiClient.get(`/turbines/${turbineId.value}/system`)
        systemInfo.value = response.data
      } catch (error) {
        console.error('获取系统信息失败:', error)
        ElMessage.error('获取系统信息失败')
      }
    }

    // 获取风速风向数据
    const fetchWindData = async () => {
      try {
        const response = await apiClient.get(`/turbines/${turbineId.value}/wind`)
        windData.value = response.data
      } catch (error) {
        console.error('获取风速风向数据失败:', error)
        ElMessage.error('获取风速风向数据失败')
      }
    }

    // 获取告警统计
    const fetchAlertStats = async () => {
      try {
        const response = await apiClient.get(`/turbines/${turbineId.value}/alerts`)
        alertStats.value = response.data
        updateAlertChart()
      } catch (error) {
        console.error('获取告警统计失败:', error)
        ElMessage.error('获取告警统计失败')
      }
    }

    // 获取发电量趋势
    const fetchPowerTrend = async () => {
      try {
        const response = await apiClient.get(`/turbines/${turbineId.value}/power/trend`)
        powerTrend.value = response.data
        updatePowerChart()
      } catch (error) {
        console.error('获取发电量趋势失败:', error)
        ElMessage.error('获取发电量趋势失败')
      }
    }

    // 获取故障信息
    const fetchFaultInfo = async () => {
      try {
        const response = await apiClient.get('/warnings')
        faultInfo.value = response.data.filter(warning => warning.turbine_id === turbineId.value)
      } catch (error) {
        console.error('获取故障信息失败:', error)
        ElMessage.error('获取故障信息失败')
      }
    }

    // 刷新数据
    const refreshData = async () => {
      try {
        loading.value = true
        await Promise.all([
          fetchTurbineInfo(),
          fetchRuntimeData(),
          fetchSystemInfo(),
          fetchWindData(),
          fetchAlertStats(),
          fetchPowerTrend(),
          fetchFaultInfo()
        ])
        ElMessage.success('数据刷新成功')
      } catch (error) {
        console.error('刷新数据失败:', error)
        ElMessage.error('刷新数据失败')
      } finally {
        loading.value = false
      }
    }

    // 初始化发电量折线图
    const initPowerChart = () => {
      if (powerChart.value) {
        powerChartInstance = echarts.init(powerChart.value)
        updatePowerChart()
      }
    }

    // 初始化告警统计柱状图
    const initAlertChart = () => {
      if (alertChart.value) {
        alertChartInstance = echarts.init(alertChart.value)
        updateAlertChart()
      }
    }

    // 更新发电量折线图
    const updatePowerChart = () => {
      if (!powerChartInstance) return
      
      const option = {
        tooltip: {
          trigger: 'axis',
          textStyle: {
            color: 'white'
          },
          backgroundColor: 'rgba(39, 64, 139, 0.8)',
          borderColor: 'rgba(79, 195, 247, 0.5)',
          borderWidth: 1
        },
        grid: {
          left: '3%',
          right: '4%',
          bottom: '3%',
          containLabel: true
        },
        xAxis: [
          {
            type: 'category',
            boundaryGap: false,
            data: powerTrend.value.hours || [],
            axisLine: {
              lineStyle: {
                color: 'rgba(255, 255, 255, 0.5)'
              }
            },
            axisLabel: {
              color: 'rgba(255, 255, 255, 0.8)'
            }
          }
        ],
        yAxis: [
          {
            type: 'value',
            name: '发电量 (kW)',
            nameTextStyle: {
              color: 'rgba(255, 255, 255, 0.8)'
            },
            axisLine: {
              lineStyle: {
                color: 'rgba(255, 255, 255, 0.5)'
              }
            },
            axisLabel: {
              color: 'rgba(255, 255, 255, 0.8)'
            },
            splitLine: {
              lineStyle: {
                color: 'rgba(255, 255, 255, 0.1)'
              }
            }
          }
        ],
        series: [
          {
            name: '发电量',
            type: 'line',
            smooth: true,
            symbol: 'circle',
            symbolSize: 6,
            lineStyle: {
              width: 3,
              color: '#4FC3F7'
            },
            itemStyle: {
              color: '#4FC3F7',
              borderColor: '#ffffff',
              borderWidth: 2
            },
            areaStyle: {
              color: {
                type: 'linear',
                x: 0,
                y: 0,
                x2: 0,
                y2: 1,
                colorStops: [{
                  offset: 0, color: 'rgba(79, 195, 247, 0.5)'
                }, {
                  offset: 1, color: 'rgba(79, 195, 247, 0.1)'
                }],
                global: false
              }
            },
            data: powerTrend.value.power || []
          }
        ]
      }
      
      powerChartInstance.setOption(option)
    }

    // 更新告警统计柱状图
    const updateAlertChart = () => {
      if (!alertChartInstance) return
      
      const option = {
        tooltip: {
          trigger: 'axis',
          textStyle: {
            color: 'white'
          },
          backgroundColor: 'rgba(39, 64, 139, 0.8)',
          borderColor: 'rgba(79, 195, 247, 0.5)',
          borderWidth: 1
        },
        grid: {
          left: '10%',
          right: '10%',
          bottom: '15%',
          top: '10%',
          containLabel: true
        },
        xAxis: {
          type: 'category',
          data: ['严重', '主要', '次要'],
          axisLine: {
            lineStyle: {
              color: 'rgba(255, 255, 255, 0.5)'
            }
          },
          axisLabel: {
            color: 'rgba(255, 255, 255, 0.8)'
          }
        },
        yAxis: {
          type: 'value',
          axisLine: {
            lineStyle: {
              color: 'rgba(255, 255, 255, 0.5)'
            }
          },
          axisLabel: {
            color: 'rgba(255, 255, 255, 0.8)'
          },
          splitLine: {
            lineStyle: {
              color: 'rgba(255, 255, 255, 0.1)'
            }
          }
        },
        series: [
          {
            name: '告警数量',
            type: 'bar',
            barWidth: '40%',
            data: [
              {
                value: alertStats.value.critical,
                itemStyle: {
                  color: '#F56C6C'
                }
              },
              {
                value: alertStats.value.major,
                itemStyle: {
                  color: '#E6A23C'
                }
              },
              {
                value: alertStats.value.minor,
                itemStyle: {
                  color: '#409EFF'
                }
              }
            ]
          }
        ]
      }
      
      alertChartInstance.setOption(option)
    }

    // 初始化Three.js场景
    const initThreeJs = () => {
      if (!threeJsContainer.value || isUnmounted) return

      // 创建场景
      scene = new THREE.Scene()
      scene.background = null

      // 创建相机
      camera = new THREE.PerspectiveCamera(
        75,
        threeJsContainer.value.clientWidth / threeJsContainer.value.clientHeight,
        0.1,
        1000
      )
      camera.position.z = 10

      // 创建渲染器
      renderer = new THREE.WebGLRenderer({ alpha: true, antialias: true })
      renderer.setSize(threeJsContainer.value.clientWidth, threeJsContainer.value.clientHeight)
      renderer.setClearColor(0x000000, 0)
      threeJsContainer.value.appendChild(renderer.domElement)

      // 添加网格
      const gridHelper = new THREE.GridHelper(20, 20, 0x4FC3F7, 0x27408B)
      gridHelper.position.y = 0
      gridHelper.material.opacity = 0.7
      gridHelper.material.transparent = true
      scene.add(gridHelper)

      // 添加坐标轴
      const axesHelper = new THREE.AxesHelper(5)
      scene.add(axesHelper)

      // 添加风机模型（加载本地STL模型）
      const createTurbineModel = () => {
        const loader = new STLLoader()
        
        // 设置材质
        const towerMaterial = new THREE.MeshBasicMaterial({ color: 0x888888 })
        const fanMaterial = new THREE.MeshBasicMaterial({ color: 0x4FC3F7, transparent: true, opacity: 0.8 })
        
        // 加载塔柱模型
        loader.load(
          new URL('/src/assets/fans/塔柱.STL', import.meta.url).href,
          (geometry) => {
            const towerMesh = new THREE.Mesh(geometry, towerMaterial)
            towerMesh.scale.set(0.1, 0.1, 0.1) // 根据实际模型大小调整缩放比例
            towerMesh.position.set(0, 0, 0) // 调整位置
            scene.add(towerMesh)
          },
          (xhr) => {
            console.log((xhr.loaded / xhr.total * 100) + '% 塔柱模型已加载')
          },
          (error) => {
            console.error('加载塔柱模型出错:', error)
          }
        )
        
        // 加载风扇模型
        loader.load(
          new URL('/src/assets/fans/风扇2.STL', import.meta.url).href,
          (geometry) => {
            const fanMesh = new THREE.Mesh(geometry, fanMaterial)
            fanMesh.scale.set(0.1, 0.1, 0.1) // 根据实际模型大小调整缩放比例
            
            // 创建父物体Group
            fanGroup = new THREE.Group()
            // 设置父物体的全局位置为0,0,0
            fanGroup.position.set(0.43, 11.84, 0)
            fanGroup.rotation.x = 0.055
            
            // 设置风扇模型相对于父物体的位置
            fanMesh.position.set(-7.73, -8.75, 1.35)
            // fanMesh.position.set(-7.3, 3.09, 1.35)
            
            // 将风扇模型添加到父物体中
            fanGroup.add(fanMesh)
            
            // 将父物体添加到场景
            scene.add(fanGroup)
          },
          (xhr) => {
            console.log((xhr.loaded / xhr.total * 100) + '% 风扇模型已加载')
          },
          (error) => {
            console.error('加载风扇模型出错:', error)
          }
        )
      }

      createTurbineModel()

      // 添加控制器
      controls = new OrbitControls(camera, renderer.domElement)
      controls.enableDamping = true
      controls.dampingFactor = 0.05
      controls.minDistance = 5
      controls.maxDistance = 30

      // 动画循环
      const animate = () => {
        if (isUnmounted) return
        animationId = requestAnimationFrame(animate)
        
        // 父物体绕Z轴自转（负值表示顺时针方向）
        if (fanGroup) {
          fanGroup.rotation.z -= 0.01 // 控制旋转速度
        }
        
        controls.update()
        renderer.render(scene, camera)
      }
      animate()

      // 窗口大小调整
      const handleThreeResize = () => {
        if (!threeJsContainer.value || isUnmounted) return
        camera.aspect = threeJsContainer.value.clientWidth / threeJsContainer.value.clientHeight
        camera.updateProjectionMatrix()
        renderer.setSize(threeJsContainer.value.clientWidth, threeJsContainer.value.clientHeight)
      }
      window.addEventListener('resize', handleThreeResize)
      
      // 存储事件监听器引用，以便后续移除
      window.handleLocalThreeResize = handleThreeResize
    }

    // 清理Three.js资源
    const cleanupThreeJs = () => {
      if (animationId) {
        cancelAnimationFrame(animationId)
      }
      if (controls) {
        controls.dispose()
      }
      if (renderer) {
        renderer.dispose()
        if (threeJsContainer.value && renderer.domElement) {
          threeJsContainer.value.removeChild(renderer.domElement)
        }
      }
      if (window.handleLocalThreeResize) {
        window.removeEventListener('resize', window.handleLocalThreeResize)
        delete window.handleLocalThreeResize
      }
      // 清理场景中的所有对象
      if (scene) {
        while(scene.children.length > 0) {
          const child = scene.children[0]
          if (child.geometry) {
            child.geometry.dispose()
          }
          if (child.material) {
            if (Array.isArray(child.material)) {
              child.material.forEach(material => material.dispose())
            } else {
              child.material.dispose()
            }
          }
          scene.remove(child)
        }
      }
      // 清理加载的模型引用
      fanGroup = null
      fanGroup2 = null
    }

    onMounted(() => {
      isUnmounted = false
      // 等待DOM渲染完成
      nextTick(() => {
        if (isUnmounted) return
        initPowerChart()
        initAlertChart()
        initThreeJs()
      })

      // 初始加载数据
      fetchFaultInfo()

      // 监听窗口大小变化
      window.addEventListener('resize', handleResize)

      // 自动更新数据
      const updateInterval = setInterval(() => {
        if (isUnmounted) return
        refreshData()
      }, 30000) // 每30秒自动刷新一次数据

      // 存储定时器引用，以便在组件卸载时清除
      window.localAnalysisUpdateInterval = updateInterval
    })

    // 处理窗口大小变化
    const handleResize = () => {
      powerChartInstance?.resize()
      alertChartInstance?.resize()
    }

    return {
      turbineInfo,
      runtimeData,
      systemInfo,
      windData,
      alertStats,
      faultInfo,
      powerChart,
      alertChart,
      threeJsContainer,
      formatPower,
      refreshData
    }
  }
}
</script>

<style scoped>
/* 主容器 */
.local-analysis-container {
  position: relative;
  width: 100%;
  height: 100%;
  padding: 10px;
  overflow: hidden;
  background: rgba(39, 64, 139, 0.8);
  backdrop-filter: blur(10px);
  display: flex;
  flex-direction: column;
}

/* 工具栏 */
.toolbar {
  height: 60px;
  padding: 0 10px;
  margin-bottom: 15px;
}

.toolbar .el-card {
  height: 100%;
  border-radius: 12px;
}

.toolbar-content {
  height: 100%;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 15px;
}

.toolbar-left {
  display: flex;
  align-items: center;
  gap: 20px;
}

/* Logo样式 */
.logo {
  display: flex;
  align-items: center;
  gap: 10px;
  color: white;
}

.logo-text {
  font-size: 16px;
  font-weight: 600;
  color: white;
  text-shadow: 0 0 10px rgba(79, 195, 247, 0.7);
}

/* 导航菜单 */
.nav-menu {
  display: flex;
  gap: 8px;
}

.nav-item {
  padding: 6px 12px;
  border-radius: 6px;
  color: rgba(255, 255, 255, 0.8);
  text-decoration: none;
  font-size: 12px;
  font-weight: 500;
  transition: all 0.3s ease;
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.nav-item:hover {
  background: rgba(79, 195, 247, 0.3);
  color: white;
  box-shadow: 0 0 10px rgba(79, 195, 247, 0.5);
}

.nav-item.active {
  background: rgba(79, 195, 247, 0.5);
  color: white;
  box-shadow: 0 0 15px rgba(79, 195, 247, 0.7);
  border-color: rgba(79, 195, 247, 0.8);
}

.toolbar-right {
  display: flex;
  align-items: center;
  gap: 10px;
}

/* 主要内容区域 */
.main-content {
  position: relative;
  width: 100%;
  flex: 1;
  display: flex;
  gap: 15px;
  padding: 0 10px 10px 10px;
  overflow: hidden;
}

/* 左侧区域（占25%宽度） */
.left-content {
  width: 25%;
  height: 100%;
  display: flex;
  flex-direction: column;
  gap: 15px;
}

/* 左侧上部分：风机名称和机械参数 */
.left-top-section {
  flex: 1;
  min-height: 180px;
}

.left-top-section .el-card {
  height: 100%;
  border-radius: 12px;
  display: flex;
  flex-direction: column;
}

.turbine-info {
  height: 100%;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  text-align: center;
}

.turbine-name {
  margin: 0 0 5px 0;
  font-size: 16px;
  font-weight: 600;
  color: white;
  text-shadow: 0 0 10px rgba(79, 195, 247, 0.7);
}

.turbine-location {
  margin: 0 0 10px 0;
  font-size: 11px;
  color: rgba(255, 255, 255, 0.8);
}

.mechanical-params {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 8px;
  width: 100%;
  padding: 0 8px;
}

.param-item {
  text-align: center;
  padding: 6px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 6px;
}

.param-label {
  display: block;
  font-size: 10px;
  color: rgba(255, 255, 255, 0.7);
  margin-bottom: 2px;
}

.param-value {
  display: block;
  font-size: 11px;
  font-weight: 600;
  color: white;
}

/* 左侧中部分：发电量和功率数据 */
.left-middle-section {
  flex: 1;
  min-height: 180px;
}

.left-middle-section .el-card {
  height: 100%;
  border-radius: 12px;
  display: flex;
  flex-direction: column;
}

.power-data {
  height: 100%;
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.data-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 10px;
  width: 100%;
  padding: 0 10px;
}

.data-item {
  text-align: center;
  padding: 8px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 8px;
}

.data-label {
  display: block;
  font-size: 11px;
  color: rgba(255, 255, 255, 0.8);
  margin-bottom: 3px;
}

.data-value {
  display: block;
  font-size: 14px;
  font-weight: 600;
  color: #4FC3F7;
  text-shadow: 0 0 5px rgba(79, 195, 247, 0.5);
}

/* 左侧下部分：风机系统信息 */
.left-bottom-section {
  flex: 0.6;
  min-height: 160px;
}

.left-bottom-section .el-card {
  height: 100%;
  border-radius: 12px;
  display: flex;
  flex-direction: column;
}

.system-info {
  height: 100%;
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 8px;
  width: 100%;
  padding: 0 8px;
}

.info-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 6px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 6px;
}

.info-label {
  font-size: 10px;
  color: rgba(255, 255, 255, 0.8);
}

.info-value {
  font-size: 10px;
  font-weight: 600;
  color: white;
}

/* 中间底部区域：新增框图 */
.middle-bottom-section {
  width: 52.5%;
  height: 24%;
  position: absolute;
  bottom: 0;
  left: calc(25% + 15px);
  z-index: 10;
}

.middle-bottom-section .el-card {
  height: 94%;
  border-radius: 12px;
  display: flex;
  flex-direction: column;
}

.fault-info-content {
  height: 100%;
  padding: 10px;
  overflow-y: auto;
}

.fault-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.fault-item {
  padding: 12px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 8px;
  border-left: 3px solid #E6A23C;
}

.fault-item:hover {
  background: rgba(255, 255, 255, 0.15);
}

.fault-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.fault-title {
  font-size: 14px;
  font-weight: 600;
  color: #ffffff;
}

.fault-description {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.8);
  margin-bottom: 6px;
  line-height: 1.4;
}

.fault-time {
  font-size: 11px;
  color: rgba(255, 255, 255, 0.6);
}

.no-fault {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: #67C23A;
}

.no-fault p {
  margin-top: 10px;
  font-size: 14px;
  color: rgba(255, 255, 255, 0.8);
}


/* 中间区域：风机细节图 */
.center-content {
  flex: 1;
  min-height: 0;
  display: flex;
  justify-content: center;
  align-items: center;
  background: rgba(39, 64, 139, 0.3);
  border-radius: 12px;
  overflow: hidden;
}

.three-js-container {
  width: 100%;
  height: 100%;
}

/* 右侧区域（占20%宽度） */
.right-content {
  width: 20%;
  height: 100%;
  display: flex;
  flex-direction: column;
  gap: 15px;
}

/* 右侧图表项 */
.chart-item {
  flex: 1;
  min-height: 0;
}

.chart-item .el-card {
  height: 100%;
  border-radius: 12px;
  display: flex;
  flex-direction: column;
}

.chart-container {
  flex: 1;
  padding: 5px 0;
}

.chart {
  width: 100%;
  height: 100%;
}

/* 风速风向罗盘 */
.wind-compass {
  flex: 1;
  display: flex;
  justify-content: center;
  align-items: center;
}

.compass-circle {
  position: relative;
  width: 150px;
  height: 150px;
  border-radius: 50%;
  background: rgba(39, 64, 139, 0.8);
  border: 2px solid rgba(79, 195, 247, 0.8);
  display: flex;
  justify-content: center;
  align-items: center;
}

.compass-rose {
  position: absolute;
  width: 100%;
  height: 100%;
}

.compass-direction {
  position: absolute;
  font-size: 12px;
  font-weight: 600;
  color: white;
  text-shadow: 0 0 5px rgba(79, 195, 247, 0.8);
}

.compass-direction:nth-child(1) { top: 8px; left: 50%; transform: translateX(-50%); }
.compass-direction:nth-child(2) { top: 50%; right: 8px; transform: translateY(-50%); }
.compass-direction:nth-child(3) { bottom: 8px; left: 50%; transform: translateX(-50%); }
.compass-direction:nth-child(4) { top: 50%; left: 8px; transform: translateY(-50%); }

.wind-indicator {
  position: absolute;
  width: 100%;
  height: 100%;
  display: flex;
  justify-content: center;
  align-items: center;
}

.wind-arrow {
  width: 0;
  height: 0;
  border-left: 8px solid transparent;
  border-right: 8px solid transparent;
  border-bottom: 60px solid #4FC3F7;
  filter: drop-shadow(0 0 5px rgba(79, 195, 247, 0.8));
  transform-origin: 50% 65px;
}

.wind-speed {
  position: absolute;
  bottom: 20px;
  font-size: 18px;
  font-weight: 600;
  color: white;
  text-shadow: 0 0 5px rgba(79, 195, 247, 0.8);
}

/* 告警统计 */
.alert-stats {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: space-around;
  align-items: center;
  padding: 5px 0;
}

/* 卡片头部样式 */
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-header span {
  font-weight: 600;
  font-size: 12px;
  color: white;
}

/* 故障分析区域 */
.fault-analysis-section {
  width: 55%;
  height: 33.3%;
  margin: 15px 10px 10px 25%;
  display: flex;
  justify-content: center;
  align-items: center;
}

.fault-analysis-section .el-card {
  width: 100%;
  height: 100%;
  border-radius: 12px;
}

.fault-analysis-content {
  height: 100%;
  display: flex;
  justify-content: center;
  align-items: center;
  color: white;
}

/* 响应式布局 */
@media (max-width: 1200px) {
  .main-content {
    flex-direction: column;
  }
  
  .left-content,
  .right-content {
    width: 100%;
  }
  
  .center-content {
    height: 400px;
  }
  
  .left-top-section,
  .left-middle-section,
  .left-bottom-section {
    height: auto;
    min-height: 200px;
  }
  
  .fault-analysis-section {
    width: 100%;
    margin-left: 10px;
  }
}

@media (max-width: 768px) {
  .main-content {
    padding: 10px;
  }
  
  .mechanical-params,
  .data-grid,
  .info-grid {
    grid-template-columns: 1fr;
  }
  
  .compass-circle {
    width: 150px;
    height: 150px;
  }
  
  .wind-arrow {
    border-bottom: 60px solid #4FC3F7;
    transform-origin: 50% 65px;
  }
}
</style>