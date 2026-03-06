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
              <router-link to="/fault-alarm" class="nav-item">故障告警</router-link>
              <router-link to="/local-analysis" class="nav-item active">局部分析</router-link>
            </div>
          </div>
          <div class="toolbar-right">
            <el-button type="primary" :icon="Refresh" @click="refreshData">
              刷新数据
            </el-button>
            <el-button :icon="Setting" @click="navigateToSettings">
              系统设置
            </el-button>
            <el-select v-model="selectedTurbine" placeholder="选择风机" clearable @change="navigateToTurbine">
              <el-option label="风机1" value="T001" />
              <el-option label="风机2" value="T002" />
              <el-option label="风机3" value="T003" />
              <el-option label="风机4" value="T004" />
              <el-option label="风机5" value="T005" />
              <el-option label="风机6" value="T006" />
              <el-option label="风机7" value="T007" />
              <el-option label="风机8" value="T008" />
              <el-option label="风机9" value="T009" />
              <el-option label="风机10" value="T010" />
            </el-select>
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
                <div class="info-item">
                  <span class="info-label">风机朝向</span>
                  <span class="info-value">{{ formatOrientation(turbineInfo.orientation) }}</span>
                </div>
              </div>
            </div>
          </el-card>
        </div>
      </div>

      <!-- 中间底部区域：新增框图 -->
      <div class="middle-bottom-section">
        <el-card shadow="hover">
          <template #header>
            <div class="card-header">
              <span>数据概览</span>
            </div>
          </template>
          <div class="overview-content">
            <div class="overview-item">
              <span class="overview-label">总发电量</span>
              <span class="overview-value">{{ formatPower(runtimeData.dailyGeneration * 30) }}</span>
            </div>
            <div class="overview-item">
              <span class="overview-label">运行效率</span>
              <span class="overview-value">{{ (runtimeData.activePower / turbineInfo.ratedPower * 100).toFixed(1) }}%</span>
            </div>
            <div class="overview-item">
              <span class="overview-label">风速</span>
              <span class="overview-value">{{ windData.speed }} m/s</span>
            </div>
            <div class="overview-item">
              <span class="overview-label">风向</span>
              <span class="overview-value">{{ windData.direction }}°</span>
            </div>
          </div>
        </el-card>
      </div>
      
      <!-- 中间区域：风机细节图（three.js网格形式） -->
      <div class="center-content">
        <div class="layer-options-row">
          <el-checkbox v-model="showHorizontalWindLayer" class="layer-checkbox">水平风速仿真图</el-checkbox>
          <el-checkbox v-model="showVerticalWindLayer" class="layer-checkbox">垂直风速仿真图</el-checkbox>
        </div>
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
                <div class="layer-options-row">
                  <el-checkbox v-model="showWindSpeedChart" class="layer-checkbox">风速</el-checkbox>
                  <el-checkbox v-model="showWindRoseChart" class="layer-checkbox">风向</el-checkbox>
                </div>
              </div>
            </template>
            <div class="wind-split">
              <div class="wind-panel" v-if="showWindSpeedChart">
                <div class="wind-panel-title">风速</div>
                <div ref="windSpeedChart" class="wind-panel-chart"></div>
              </div>
              <div class="wind-panel" v-if="showWindRoseChart">
                <div class="wind-panel-title">风向</div>
                <div ref="windRoseChart" class="wind-panel-chart"></div>
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
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import * as echarts from 'echarts'
import axios from 'axios'
import * as THREE from 'three'
import { GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader'
import { WindPower, Refresh, Setting } from '@element-plus/icons-vue'
import { RGBELoader } from 'three/examples/jsm/loaders/RGBELoader'

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
    const router = useRouter()
    
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
      speedRange: '',
      orientation: 0
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
    const windHistory = ref([])
    const loading = ref(false)
    const showHorizontalWindLayer = ref(true)
    const showVerticalWindLayer = ref(false)
    const showWindSpeedChart = ref(true)
    const showWindRoseChart = ref(true)
    const selectedTurbine = ref(turbineId.value)

    // 图表引用
    const windSpeedChart = ref(null)
    const windRoseChart = ref(null)
    const powerChart = ref(null)
    const alertChart = ref(null)
    const threeJsContainer = ref(null)

    // 图表实例
    let windSpeedChartInstance = null
    let windRoseChartInstance = null
    let powerChartInstance = null
    let alertChartInstance = null

    // Three.js相关
    let scene = null
    let camera = null
    let renderer = null
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

    const formatOrientation = (orientation) => {
      const orientationValue = Number(orientation)
      if (!Number.isFinite(orientationValue)) {
        return '--'
      }
      const normalized = ((orientationValue % 360) + 360) % 360
      return `${normalized.toFixed(1)}°`
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
        switch(runtimeData.value.status) {
          case 'running':
            runtimeData.value.statusText = '运行中'
            break
          case 'stopped':
            runtimeData.value.statusText = '已停机'
            break
          case 'warning':
            runtimeData.value.statusText = '告警'
            break
          default:
            runtimeData.value.statusText = '存在问题'
            break
        }
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
        const response = await apiClient.get(`/turbines/${turbineId.value}/wind/history`, {
          params: {
            minutes: 60
          }
        })

        const points = response.data?.points || []
        if (points.length > 0) {
          windHistory.value = points.map(item => ({
            timestamp: new Date(String(item.timestamp).replace(' ', 'T')),
            speed: Number(item.speed) || 0,
            direction: Number(item.direction) || 0
          }))

          const latest = windHistory.value[windHistory.value.length - 1]
          windData.value = {
            turbine_id: response.data.turbine_id || turbineId.value,
            speed: latest.speed,
            direction: latest.direction
          }
        } else {
          const latestResponse = await apiClient.get(`/turbines/${turbineId.value}/wind`)
          windData.value = latestResponse.data
          windHistory.value = [{
            timestamp: new Date(),
            speed: Number(windData.value.speed) || 0,
            direction: Number(windData.value.direction) || 0
          }]
        }

        updateWindSpeedChart()
        updateWindRoseChart()
      } catch (error) {
        console.error('获取风速风向数据失败:', error)
        ElMessage.error('获取风速风向数据失败')
      }
    }

    const initWindSpeedChart = () => {
      if (windSpeedChart.value) {
        if (windSpeedChart.value.clientWidth === 0 || windSpeedChart.value.clientHeight === 0) {
          setTimeout(() => {
            initWindSpeedChart()
          }, 100)
          return
        }
        windSpeedChartInstance = echarts.init(windSpeedChart.value)
        updateWindSpeedChart()
      }
    }

    const initWindRoseChart = () => {
      if (windRoseChart.value) {
        if (windRoseChart.value.clientWidth === 0 || windRoseChart.value.clientHeight === 0) {
          setTimeout(() => {
            initWindRoseChart()
          }, 100)
          return
        }
        windRoseChartInstance = echarts.init(windRoseChart.value)
        updateWindRoseChart()
      }
    }

    const updateWindSpeedChart = () => {
      if (!windSpeedChartInstance) {
        initWindSpeedChart()
        return
      }

      const history = windHistory.value
      const xAxisData = history.map(item => {
        const date = new Date(item.timestamp)
        const hh = String(date.getHours()).padStart(2, '0')
        const mm = String(date.getMinutes()).padStart(2, '0')
        const ss = String(date.getSeconds()).padStart(2, '0')
        return `${hh}:${mm}:${ss}`
      })
      const speedData = history.map(item => item.speed)

      const option = {
        tooltip: {
          trigger: 'axis',
          formatter: params => {
            if (!params.length) return ''
            const point = params[0]
            return `${point.axisValue}<br/>${point.marker} 风速: ${point.data} m/s`
          },
          textStyle: {
            color: 'white'
          },
          backgroundColor: 'rgba(39, 64, 139, 0.8)',
          borderColor: 'rgba(79, 195, 247, 0.5)',
          borderWidth: 1
        },
        grid: {
          left: '10%',
          right: '8%',
          top: '15%',
          bottom: '18%'
        },
        xAxis: {
          type: 'category',
          data: xAxisData,
          boundaryGap: false,
          axisLabel: {
            color: 'rgba(255, 255, 255, 0.8)',
            fontSize: 10,
            interval: 'auto'
          },
          axisLine: {
            lineStyle: {
              color: 'rgba(255, 255, 255, 0.4)'
            }
          }
        },
        yAxis: {
          type: 'value',
          name: 'm/s',
          nameTextStyle: {
            color: 'rgba(255, 255, 255, 0.8)',
            padding: [0, 0, 0, -8]
          },
          axisLabel: {
            color: 'rgba(255, 255, 255, 0.8)',
            fontSize: 10
          },
          axisLine: {
            lineStyle: {
              color: 'rgba(255, 255, 255, 0.4)'
            }
          },
          splitLine: {
            lineStyle: {
              color: 'rgba(255, 255, 255, 0.12)'
            }
          }
        },
        series: [
          {
            name: '风速',
            type: 'line',
            smooth: true,
            showSymbol: false,
            data: speedData,
            lineStyle: {
              color: '#4FC3F7',
              width: 2
            },
            areaStyle: {
              color: 'rgba(79, 195, 247, 0.18)'
            }
          }
        ]
      }

      windSpeedChartInstance.setOption(option)
    }

    const updateWindRoseChart = () => {
      if (!windRoseChartInstance) {
        initWindRoseChart()
        return
      }

      const samples = windHistory.value.length
        ? windHistory.value.map(item => ({
            direction: ((Number(item.direction) || 0) % 360 + 360) % 360,
            speed: Math.max(0, Number(item.speed) || 0)
          }))
        : [{
            direction: ((Number(windData.value.direction) || 0) % 360 + 360) % 360,
            speed: Math.max(0, Number(windData.value.speed) || 0)
          }]

      const sortedSamples = [...samples].sort((first, second) => first.direction - second.direction)
      const pointData = sortedSamples.map(item => [item.speed, item.direction])
      const loopLineData = pointData.length > 1
        ? [...pointData, pointData[0]]
        : pointData
      const maxRadius = Math.max(12, Math.ceil(Math.max(...samples.map(item => item.speed), 0) + 2))

      const option = {
        tooltip: {
          trigger: 'item',
          formatter: params => {
            const value = params.value || []
            const speed = Number(value[0]) || 0
            const direction = Number(value[1]) || 0
            return `风向: ${direction.toFixed(1)}°<br/>风速: ${speed.toFixed(2)} m/s`
          },
          textStyle: {
            color: 'white'
          },
          backgroundColor: 'rgba(39, 64, 139, 0.8)',
          borderColor: 'rgba(79, 195, 247, 0.5)',
          borderWidth: 1
        },
        polar: {
          radius: '78%'
        },
        angleAxis: {
          type: 'value',
          min: 0,
          max: 360,
          startAngle: 90,
          clockwise: false,
          interval: 45,
          axisLabel: {
            formatter: value => {
              const labels = {
                0: 'N',
                45: 'NE',
                90: 'E',
                135: 'SE',
                180: 'S',
                225: 'SW',
                270: 'W',
                315: 'NW',
                360: 'N'
              }
              return labels[value] ?? ''
            },
            color: 'rgba(255, 255, 255, 0.85)',
            fontSize: 10
          },
          axisLine: {
            lineStyle: {
              color: 'rgba(255, 255, 255, 0.35)'
            }
          }
        },
        radiusAxis: {
          min: 0,
          max: maxRadius,
          splitNumber: 4,
          axisLabel: {
            color: 'rgba(255, 255, 255, 0.65)',
            fontSize: 10
          },
          axisLine: {
            lineStyle: {
              color: 'rgba(255, 255, 255, 0.35)'
            }
          },
          splitLine: {
            lineStyle: {
              color: 'rgba(255, 255, 255, 0.12)'
            }
          }
        },
        series: [
          {
            name: '风场轨迹',
            type: 'line',
            coordinateSystem: 'polar',
            data: loopLineData,
            symbol: 'none',
            lineStyle: {
              color: '#4FC3F7',
              width: 2
            },
            areaStyle: {
              color: 'rgba(79, 195, 247, 0.12)'
            },
            silent: true,
            z: 1
          },
          {
            name: '风速风向采样点',
            type: 'scatter',
            coordinateSystem: 'polar',
            data: pointData,
            symbolSize: 7,
            itemStyle: {
              color: '#FFD700',
              borderColor: '#FFFFFF',
              borderWidth: 1
            },
            z: 2
          }
        ]
      }

      windRoseChartInstance.setOption(option)
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

    // 跳转到风机详情页
    const navigateToTurbine = (turbineId) => {
      if (turbineId) {
        router.push(`/local-analysis/${turbineId}`)
      }
    }

    // 跳转到设置页面
    const navigateToSettings = () => {
      router.push('/settings')
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
          fetchPowerTrend()
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
        // 确保 DOM 元素有尺寸
        if (powerChart.value.clientWidth === 0 || powerChart.value.clientHeight === 0) {
          // 等待 DOM 渲染完成后重试
          setTimeout(() => {
            initPowerChart()
          }, 100)
          return
        }
        powerChartInstance = echarts.init(powerChart.value)
        updatePowerChart()
      }
    }

    // 初始化告警统计柱状图
    const initAlertChart = () => {
      if (alertChart.value) {
        // 确保 DOM 元素有尺寸
        if (alertChart.value.clientWidth === 0 || alertChart.value.clientHeight === 0) {
          // 等待 DOM 渲染完成后重试
          setTimeout(() => {
            initAlertChart()
          }, 100)
          return
        }
        alertChartInstance = echarts.init(alertChart.value)
        updateAlertChart()
      }
    }

    // 更新发电量折线图
    const updatePowerChart = () => {
      if (!powerChartInstance) {
        console.log('发电量折线图实例不存在，尝试初始化')
        // 尝试初始化图表
        initPowerChart()
        return
      }
      
      const powerTrendOption = computed(() => {
        if(!powerTrend.value) return {}
        
        const hours = powerTrend.value.hours || []
        const power = powerTrend.value.power || []
        const forecast = powerTrend.value.forecast || []

        // 时间转换为毫秒，适配不同格式
        const toMs = (t) => {
          if (!t) return NaN

          // 尝试直接解析完整时间格式（ISO、日期）
          const parsed = Date.parse(t)
          if (!Number.isNaN(parsed)) return parsed

          // 兼容 HH:mm 或 HH:mm:ss 格式
          const m = String(t).match(/^(\d{1,2}):(\d{2})(?::(\d{2}))?$/)
          if (m) {
            const now = new Date()
            const d = new Date(
              now.getFullYear(),
              now.getMonth(),
              now.getDate(),
              Number(m[1]),
              Number(m[2]),
              Number(m[3] || 0),
              0
            )
            return d.getTime()
          }
          return NaN
        }

        const actualData = hours
          .map((h, i) => [toMs(h), power[i]])
          .filter(([t, v]) => Number.isFinite(t) && v != null)

        // 构建预测数据，直接使用hours的最后四个时间值作为X轴
        let forecastData = []
        if (forecast.length > 0 && hours.length >= 5) {
          // 获取hours的最后四个时间点
          const forecastHours = hours.slice(-5)
          
          forecastData = forecast.map((v, index) => {
            // 使用对应的forecastHours时间
            return [toMs(forecastHours[index]), v]
          })
        }

        return {
          tooltip: {
            trigger: 'axis',
            formatter: (params) => {
              if (!params.length) return ''
              const date = new Date(params[0].value[0])
              const hh = String(date.getHours()).padStart(2, '0')
              const mi = String(date.getMinutes()).padStart(2, '0')

              let str = `${hh}:${mi}<br/>`
              params.forEach(p => {
                str += `${p.marker} ${p.seriesName}: ${p.value[1]} kW<br/>`
              })
              return str
            },
            textStyle: {
              color: 'white'
            },
            backgroundColor: 'rgba(39, 64, 139, 0.8)',
            borderColor: 'rgba(79, 195, 247, 0.5)',
            borderWidth: 1
          },
          grid: {
            left: '1%',
            right: '1%',
            bottom: '1%',
            containLabel: true
          },
          xAxis: {
            type: 'time',
            boundaryGap: false,
            axisLabel: {
              formatter: (value) => {
                const d = new Date(value)
                const hh = String(d.getHours()).padStart(2, '0')
                const mm = String(d.getMinutes()).padStart(2, '0')
                return `${hh}:${mm}`
              },
              color: 'rgba(255, 255, 255, 0.8)'
            },
            axisLine: {
              lineStyle: {
                color: 'rgba(255, 255, 255, 0.5)'
              }
            },
          },
          yAxis: {
            type: 'value',
            name: '功率 (kW)',
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
          },
          series: [
            {
              name: '发电量',
              type: 'line',
              smooth: true,
              symbol: 'circle',
              symbolSize: 6,
              data: actualData,
              lineStyle: {
                width: 3,
                color: '#4FC3F7'
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
              }
            },
            {
              name: '预测出力',
              type: 'line',
              smooth: true,
              symbol: 'circle',
              symbolSize: 6,
              data: forecastData,
              lineStyle: {
                color: "#FFD700",
                width: 2
              },
              itemStyle: {
                color: "#FFD700"
              }
            }
          ]
        }
      })
      powerChartInstance.setOption(powerTrendOption.value)
    }

    // 更新告警统计柱状图
    const updateAlertChart = () => {
      if (!alertChartInstance) {
        console.log('告警统计柱状图实例不存在，尝试初始化')
        // 尝试初始化图表
        initAlertChart()
        return
      }
      
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
      // camera.position.z = 10
      camera.position.set(3, 10, 6)
      camera.lookAt(0, 5, 0)

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

      // 添加风机模型（加载本地GLB模型）
      const createTurbineModel = () => {
        const loader = new GLTFLoader()
        
        // 设置材质
        const towerMaterial = new THREE.MeshBasicMaterial({ color: 0x888888 })
        const fanMaterial = new THREE.MeshBasicMaterial({ color: 0x4FC3F7, transparent: true, opacity: 0.8 })
        
        // 加载塔柱模型
        loader.load(
          '/fans/Tower.glb',
          (gltf) => {
            const towerModel = gltf.scene
            // 不再指定材质，直接使用模型自带材质
            towerModel.scale.set(0.1, 0.1, 0.1) // 根据实际模型大小调整缩放比例
            towerModel.position.set(0, 0, 0) // 调整位置
            towerModel.rotation.set(0, 1.5708, 0)
            scene.add(towerModel)
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
          '/fans/Fan.glb',
          (gltf) => {
            const fanModel = gltf.scene
            // 不再指定材质，直接使用模型自带材质
            fanModel.scale.set(0.1, 0.1, 0.1) // 根据实际模型大小调整缩放比例
            
            // 创建父物体Group
            fanGroup = new THREE.Group()
            // 设置父物体的全局位置为0,0,0
            // fanGroup.position.set(0.43, 11.84, 0)
            // fanGroup.position.set(0, 11.84, 0.475)
            fanGroup.position.set(0, 2.1, -1.58)
            fanGroup.rotation.set(0, 3.14159, 0)
            fanGroup.rotation.x = 0.055
            
            // 设置风扇模型相对于父物体的位置
            // fanModel.position.set(-7.73, -8.75, 1.35)
            // fanModel.position.set(-7.3, 3.09, 1.35)
            fanModel.position.set(0, 0, 0)
            
            // 将风扇模型添加到父物体中
            fanGroup.add(fanModel)
            
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
        // 加载风扇模型
        loader.load(
          '/fans/Fan.glb',
          (gltf) => {
            const fanModel2 = gltf.scene
            // 不再指定材质，直接使用模型自带材质
            fanModel2.scale.set(0.1, 0.1, 0.1) // 根据实际模型大小调整缩放比例
            
            // 创建父物体Group
            fanGroup2 = new THREE.Group()
            // 设置父物体的全局位置为0,0,0
            // fanGroup.position.set(0.43, 11.84, 0)
            // fanGroup.position.set(0, 11.84, 0.475)
            fanGroup2.position.set(0, 5.225, -1.58)
            fanGroup2.rotation.set(0, 3.14159, 0)
            fanGroup2.rotation.x = 0.055
            
            // 设置风扇模型相对于父物体的位置
            // fanModel.position.set(-7.73, -8.75, 1.35)
            // fanModel.position.set(-7.3, 3.09, 1.35)
            fanModel2.position.set(0, 0, 0)
            
            // 将风扇模型添加到父物体中
            fanGroup2.add(fanModel2)
            
            // 将父物体添加到场景
            scene.add(fanGroup2)
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

      // 动画循环
      const animate = () => {
        if (isUnmounted) return
        animationId = requestAnimationFrame(animate)
        
        // 父物体绕Z轴自转（负值表示顺时针方向）
        if (fanGroup) {
          fanGroup.rotation.z -= 0.01 // 控制旋转速度
        }
        if (fanGroup2) {
          fanGroup2.rotation.z -= 0.01 // 控制旋转速度
        }
        
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

      renderer.outputColorSpace = THREE.SRGBColorSpace
      renderer.toneMapping = THREE.ACESFilmicToneMapping
      renderer.toneMappingExposure = 1.0

      const pmremGenerator = new THREE.PMREMGenerator(renderer)
      pmremGenerator.compileEquirectangularShader()

      new RGBELoader()
        .setPath('/hdr/')
        .load('golden_gate_hills_1k.hdr', (hdrEquirect) => {
          const envMap = pmremGenerator.fromEquirectangular(hdrEquirect).texture
          scene.environment = envMap
          scene.background = envMap
          
          hdrEquirect.dispose()
          pmremGenerator.dispose()
        })
    }

    // 清理Three.js资源
    const cleanupThreeJs = () => {
      if (animationId) {
        cancelAnimationFrame(animationId)
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
        initWindSpeedChart()
        initWindRoseChart()
        initPowerChart()
        initAlertChart()
        initThreeJs()
      })

      // 初始加载数据
      refreshData()

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

    onUnmounted(() => {
      isUnmounted = true

      if (window.localAnalysisUpdateInterval) {
        clearInterval(window.localAnalysisUpdateInterval)
        delete window.localAnalysisUpdateInterval
      }

      window.removeEventListener('resize', handleResize)

      windSpeedChartInstance?.dispose()
      windRoseChartInstance?.dispose()
      powerChartInstance?.dispose()
      alertChartInstance?.dispose()

      cleanupThreeJs()
    })

    // 处理窗口大小变化
    const handleResize = () => {
      windSpeedChartInstance?.resize()
      windRoseChartInstance?.resize()
      powerChartInstance?.resize()
      alertChartInstance?.resize()
    }

    return {
      turbineInfo,
      runtimeData,
      systemInfo,
      windData,
      alertStats,
      windSpeedChart,
      windRoseChart,
      powerChart,
      alertChart,
      threeJsContainer,
      selectedTurbine,
      navigateToTurbine,
      navigateToSettings,
      router,
      Refresh,
      Setting,
      showHorizontalWindLayer,
      showVerticalWindLayer,
      showWindSpeedChart,
      showWindRoseChart,
      formatPower,
      formatOrientation,
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
  width: 53%;
  height: 22%;
  position: absolute;
  bottom: 0;
  left: calc(25% + 15px);
  z-index: 10;
}

.middle-bottom-section .el-card {
  height: 89%;
  border-radius: 12px;
  display: flex;
  flex-direction: column;
}

.overview-content {
  height: 100%;
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 10px;
  padding: 0 10px;
  align-items: center;
}

.overview-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 8px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 8px;
}

.overview-label {
  font-size: 11px;
  color: rgba(255, 255, 255, 0.8);
  margin-bottom: 4px;
}

.overview-value {
  font-size: 14px;
  font-weight: 600;
  color: #4FC3F7;
  text-shadow: 0 0 5px rgba(79, 195, 247, 0.5);
}


/* 中间区域：风机细节图 */
.center-content {
  flex: 1;
  min-height: 0;
  display: flex;
  flex-direction: column;
  justify-content: flex-start;
  align-items: stretch;
  background: rgba(39, 64, 139, 0.3);
  border-radius: 12px;
  overflow: hidden;
}

.layer-options-row {
  height: 38px;
  display: flex;
  align-items: center;
  gap: 20px;
  padding: 0 14px;
  background: rgba(39, 64, 139, 0.6);
  border-bottom: 1px solid rgba(79, 195, 247, 0.35);
  flex-shrink: 0;
}

.layer-checkbox :deep(.el-checkbox__label) {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.9);
}

.layer-checkbox :deep(.el-checkbox__input.is-checked + .el-checkbox__label) {
  color: #4FC3F7;
}

.three-js-container {
  flex: 1;
  min-height: 0;
  width: 100%;
  height: auto;
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

.chart-item :deep(.el-card__body) {
  flex: 1;
  min-height: 0;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  padding: 10px;
}

/* .chart-container {
  flex: 1;
  padding: 5px 0;
} */
 .chart-container {
  flex: 1;
  min-height: 0;
  overflow: hiddel;
  padding: 0;
 }

/* .chart {
  width: 300px;
  height: 100px;
} */
 .chart {
  flex: 1;
  min-height: 0;
  width: 100%;
  height: 100%;
 }

/* 风速风向分栏图 */
.wind-split {
  flex: 1;
  display: flex;
  gap: 10px;
  min-height: 0;
}

.wind-panel {
  width: 50%;
  display: flex;
  flex-direction: column;
  min-height: 0;
  background: rgba(255, 255, 255, 0.06);
  border: 1px solid rgba(79, 195, 247, 0.3);
  border-radius: 8px;
  padding: 8px;
}

.wind-panel-title {
  font-size: 11px;
  color: rgba(255, 255, 255, 0.9);
  margin-bottom: 6px;
  text-align: center;
  flex-shrink: 0;
}

.wind-panel-chart {
  flex: 1;
  min-height: 0;
  width: 100%;
}

@media (max-width: 1600px) {
  .wind-split {
    flex-direction: column;
  }

  .wind-panel {
    width: 100%;
  }
}

@media (max-width: 1200px) {
  .wind-split {
    flex-direction: row;
  }

  .wind-panel {
    width: 50%;
  }
}

@media (max-width: 768px) {
  .wind-split {
    flex-direction: column;
  }

  .wind-panel {
    width: 100%;
  }
}

/* 告警统计 */
.alert-stats {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
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