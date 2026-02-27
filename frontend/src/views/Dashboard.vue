<template>
  <div class="dashboard-container">
    <!-- 背景风电厂分布图 -->
    <div class="background-map">
      <div ref="threeJsContainer" class="three-js-container"></div>
    </div>

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
              <router-link to="/" class="nav-item active">总体预览</router-link>
              <router-link to="/local-analysis" class="nav-item">局部分析</router-link>
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
      <!-- 上部分：数据和右侧图表 -->
      <div class="top-main-content">
        <!-- 左侧数据区域 -->
        <div class="left-data-content">
          <!-- 数据部分 -->
          <div class="data-section">
            <el-card shadow="hover">
              <div class="data-content">
                <div class="data-item">
                  <div class="data-label">当日总发电量</div>
                  <div class="data-value">{{ formatPower(dailyStats.totalGeneration) }}</div>
                </div>
                <div class="data-item">
                  <div class="data-label">平均发电功率</div>
                  <div class="data-value">{{ formatPower(dailyStats.avgPower) }}</div>
                </div>
                <div class="data-item">
                  <div class="data-label">运行时长</div>
                  <div class="data-value">{{ dailyStats.runTime }} 小时</div>
                </div>
                <div class="data-item">
                  <div class="data-label">平均效率</div>
                  <div class="data-value">{{ dailyStats.avgEfficiency }}%</div>
                </div>
              </div>
            </el-card>
          </div>
        </div>

        <!-- 右侧区域（占25%宽度） -->
        <div class="right-content">
          <!-- 上部分：故障饼状图 -->
          <div class="chart-item top-chart">
            <el-card shadow="hover">
              <template #header>
                <div class="card-header">
                  <span>故障分布</span>
                </div>
              </template>
              <div class="chart-container">
                <div ref="faultPieChart" class="chart"></div>
              </div>
            </el-card>
          </div>

          <!-- 中部分：总故障数折线图 -->
          <div class="chart-item middle-chart">
            <el-card shadow="hover">
              <template #header>
                <div class="card-header">
                  <span>每日总故障数</span>
                </div>
              </template>
              <div class="chart-container">
                <div ref="faultLineChart" class="chart"></div>
              </div>
            </el-card>
          </div>

          <!-- 下部分：当日发电量折线图 -->
          <div class="chart-item bottom-chart">
            <el-card shadow="hover">
              <template #header>
                <div class="card-header">
                  <span>当日发电量对比</span>
                </div>
              </template>
              <div class="chart-container">
                <div ref="powerLineChart" class="chart"></div>
              </div>
            </el-card>
          </div>
        </div>
      </div>

      <!-- 底部区域：警告信息 -->
      <div class="bottom-content">
        <!-- 警告信息 -->
        <div class="warnings-section">
          <el-card shadow="hover">
            <template #header>
              <div class="card-header">
                <span>最新警告信息</span>
                <el-button type="text" size="small">查看全部</el-button>
              </div>
            </template>
            <div class="warnings-list">
              <el-alert
                v-for="warning in warnings"
                :key="warning.id"
                :title="warning.title"
                :description="warning.description"
                :type="warning.type"
                :closable="false"
                show-icon
                class="warning-item"
              />
            </div>
          </el-card>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted, onUnmounted, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import * as echarts from 'echarts'
import axios from 'axios'
import TurbineCard from '@components/TurbineCard.vue'
import {
  Refresh,
  Setting,
  DataLine,
  TrendCharts,
  Monitor,
  Warning,
  Location,
  WindPower
} from '@element-plus/icons-vue'

// 导入Three.js库
import * as THREE from 'three'
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls'
import { GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader'
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
  name: 'Dashboard',
  components: {
    TurbineCard
  },
  setup() {
    const router = useRouter()
    
    // 响应式数据
    const turbines = ref([])
    const filterStatus = ref('')
    const selectedTurbine = ref('')
    const sortBy = ref('power')
    const currentPage = ref(1)
    const pageSize = ref(8)
    const dailyStats = ref({ totalGeneration: 0, avgPower: 0, maxPower: 0, runTime: 0, avgEfficiency: 0 })
    const warnings = ref([])
    const faultDistribution = ref([])
    const dailyFaults = ref({ dates: [], counts: [] })
    const powerComparison = ref({ hours: [], actual: [], predicted: [] })
    const loading = ref(false)

    // 图表引用
    const faultPieChart = ref(null)
    const faultLineChart = ref(null)
    const powerLineChart = ref(null)
    const threeJsContainer = ref(null)

    // 图表实例
    let faultPieChartInstance = null
    let faultLineChartInstance = null
    let powerLineChartInstance = null

    // Three.js相关
    let scene = null
    let camera = null
    let renderer = null
    let controls = null
    let animationId = null

    // 计算统计信息
    const stats = computed(() => {
      const running = turbines.value.filter(t => t.status === 'running').length
      const warning = turbines.value.filter(t => t.status === 'warning').length
      const stopped = turbines.value.filter(t => t.status === 'stopped').length
      const totalPower = turbines.value.reduce((sum, t) => sum + t.power, 0)
      const avgEfficiency = turbines.value.length > 0 ? turbines.value.reduce((sum, t) => sum + t.efficiency, 0) / turbines.value.length : 0
      
      return {
        totalPower,
        averageEfficiency: Number(avgEfficiency.toFixed(1)),
        runningCount: running,
        warningCount: warning,
        stoppedCount: stopped
      }
    })

    // 获取风机列表
    const fetchTurbines = async () => {
      try {
        loading.value = true
        const params = filterStatus.value ? { status: filterStatus.value } : {}
        const response = await apiClient.get('/turbines', { params })
        turbines.value = response.data
      } catch (error) {
        console.error('获取风机列表失败:', error)
        ElMessage.error('获取风机列表失败，请检查后端服务是否正常运行')
      } finally {
        loading.value = false
      }
    }

    // 获取当日发电统计数据
    const fetchDailyStats = async () => {
      try {
        const response = await apiClient.get('/stats/daily')
        dailyStats.value = response.data
      } catch (error) {
        console.error('获取当日发电统计数据失败:', error)
        ElMessage.error('获取当日发电统计数据失败')
      }
    }

    // 获取警告信息
    const fetchWarnings = async () => {
      try {
        const response = await apiClient.get('/warnings')
        warnings.value = response.data
      } catch (error) {
        console.error('获取警告信息失败:', error)
        ElMessage.error('获取警告信息失败')
      }
    }

    // 获取故障分布数据
    const fetchFaultDistribution = async () => {
      try {
        const response = await apiClient.get('/faults/distribution')
        faultDistribution.value = response.data
        console.log(faultDistribution.value)
        updateFaultPieChart()
      } catch (error) {
        console.error('获取故障分布数据失败:', error)
        ElMessage.error('获取故障分布数据失败')
      }
    }

    // 获取每日故障数数据
    const fetchDailyFaults = async () => {
      try {
        const response = await apiClient.get('/faults/daily')
        dailyFaults.value = response.data
        updateFaultLineChart()
      } catch (error) {
        console.error('获取每日故障数数据失败:', error)
        ElMessage.error('获取每日故障数数据失败')
      }
    }

    // 获取发电量对比数据
    const fetchPowerComparison = async () => {
      try {
        const response = await apiClient.get('/power/comparison')
        powerComparison.value = response.data
        updatePowerLineChart()
      } catch (error) {
        console.error('获取发电量对比数据失败:', error)
        ElMessage.error('获取发电量对比数据失败')
      }
    }

    // 方法
    const formatPower = (power) => {
      if (power >= 1000) {
        return (power / 1000).toFixed(1) + ' MW'
      }
      return power.toFixed(0) + ' kW'
    }

    const refreshData = async () => {
      try {
        loading.value = true
        await Promise.all([
          fetchTurbines(),
          fetchDailyStats(),
          fetchWarnings(),
          fetchFaultDistribution(),
          fetchDailyFaults(),
          fetchPowerComparison()
        ])
        ElMessage.success('数据已刷新')
      } catch (error) {
        console.error('刷新数据失败:', error)
        ElMessage.error('刷新数据失败')
      } finally {
        loading.value = false
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

    // 初始化故障饼状图
    const initFaultPieChart = () => {
      if (faultPieChart.value) {
        // 确保 DOM 元素有尺寸
        if (faultPieChart.value.clientWidth === 0 || faultPieChart.value.clientHeight === 0) {
          // 等待 DOM 渲染完成后重试
          setTimeout(() => {
            initFaultPieChart()
          }, 100)
          return
        }
        faultPieChartInstance = echarts.init(faultPieChart.value)
        updateFaultPieChart()
      }
    }

    // 更新故障饼状图
    const updateFaultPieChart = () => {
      if (!faultPieChartInstance)
      {
        console.log('故障饼状图实例不存在，尝试初始化')
        // 尝试初始化图表
        initFaultPieChart()
        return
      }
      
      const option = {
        tooltip: {
          trigger: 'item',
          formatter: '{a} <br/>{b}: {c} ({d}%)',
          textStyle: {
            color: 'white'
          },
          backgroundColor: 'rgba(39, 64, 139, 0.8)',
          borderColor: 'rgba(79, 195, 247, 0.5)',
          borderWidth: 1
        },
        legend: {
          orient: 'vertical',
          right: '5%',
          top: 'center',
          itemWidth: 10,
          itemHeight: 10,
          itemGap: 6,
          data: faultDistribution.value.map(item => item.name),
          textStyle: {
            color: 'rgba(255, 255, 255, 0.8)',
            fontSize: 10
          },
          formatter: '{name}'
        },
        series: [
          {
            name: '故障分布',
            type: 'pie',
            radius: ['35%', '60%'],
            center: ['40%', '50%'],
            avoidLabelOverlap: false,
            itemStyle: {
              borderRadius: 10,
              borderColor: 'rgba(39, 64, 139, 0.6)',
              borderWidth: 2,
              shadowBlur: 10,
              shadowOffsetX: 0,
              shadowColor: 'rgba(79, 195, 247, 0.5)'
            },
            label: {
              show: false,
              position: 'center'
            },
            emphasis: {
              label: {
                show: true,
                fontSize: '18',
                fontWeight: 'bold',
                color: 'white'
              },
              itemStyle: {
                shadowBlur: 20,
                shadowOffsetX: 0,
                shadowColor: 'rgba(79, 195, 247, 0.8)'
              }
            },
            labelLine: {
              show: false
            },
            data: faultDistribution.value
          }
        ]
      }
      
      faultPieChartInstance.setOption(option)
    }

    // 初始化总故障数折线图
    const initFaultLineChart = () => {
      if (faultLineChart.value) {
        // 确保 DOM 元素有尺寸
        if (faultLineChart.value.clientWidth === 0 || faultLineChart.value.clientHeight === 0) {
          // 等待 DOM 渲染完成后重试
          setTimeout(() => {
            initFaultLineChart()
          }, 100)
          return
        }
        faultLineChartInstance = echarts.init(faultLineChart.value)
        updateFaultLineChart()
      }
    }

    // 更新总故障数折线图
    const updateFaultLineChart = () => {
      if (!faultLineChartInstance)
      {
        console.log('总故障数折线图实例不存在，尝试初始化')
        // 尝试初始化图表
        initFaultLineChart()
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
          left: '3%',
          right: '4%',
          bottom: '3%',
          containLabel: true,
          backgroundColor: 'transparent'
        },
        xAxis: {
          type: 'category',
          boundaryGap: false,
          data: dailyFaults.value.dates || [],
          axisLine: {
            lineStyle: {
              color: 'rgba(255, 255, 255, 0.3)'
            }
          },
          axisLabel: {
            color: 'rgba(255, 255, 255, 0.8)'
          },
          splitLine: {
            show: false
          }
        },
        yAxis: {
          type: 'value',
          name: '故障数',
          nameTextStyle: {
            color: 'rgba(255, 255, 255, 0.8)'
          },
          axisLine: {
            lineStyle: {
              color: 'rgba(255, 255, 255, 0.3)'
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
            name: '故障数',
            data: dailyFaults.value.counts || [],
            type: 'line',
            smooth: true,
            lineStyle: {
              width: 3,
              color: '#4fc3f7',
              shadowBlur: 10,
              shadowColor: 'rgba(79, 195, 247, 0.7)'
            },
            itemStyle: {
              color: '#4fc3f7',
              borderColor: 'rgba(39, 64, 139, 0.6)',
              borderWidth: 2,
              shadowBlur: 10,
              shadowColor: 'rgba(79, 195, 247, 0.7)'
            },
            areaStyle: {
              color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                { offset: 0, color: 'rgba(79, 195, 247, 0.5)' },
                { offset: 1, color: 'rgba(79, 195, 247, 0.1)' }
              ])
            }
          }
        ]
      }
      
      faultLineChartInstance.setOption(option)
    }

    // 初始化当日发电量折线图
    const initPowerLineChart = () => {
      if (powerLineChart.value) {
        // 确保 DOM 元素有尺寸
        if (powerLineChart.value.clientWidth === 0 || powerLineChart.value.clientHeight === 0) {
          // 等待 DOM 渲染完成后重试
          setTimeout(() => {
            initPowerLineChart()
          }, 100)
          return
        }
        powerLineChartInstance = echarts.init(powerLineChart.value)
        updatePowerLineChart()
      }
    }

    // 更新当日发电量折线图
    const updatePowerLineChart = () => {
      if (!powerLineChartInstance)
      {
        console.log('当日发电量折线图实例不存在，尝试初始化')
        // 尝试初始化图表
        initPowerLineChart()
        return
      }
      console.log('更新当日发电量折线图')
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
        legend: {
          data: ['实测发电量', '预测发电量'],
          top: 0,
          textStyle: {
            color: 'rgba(255, 255, 255, 0.8)'
          }
        },
        grid: {
          left: '3%',
          right: '4%',
          bottom: '3%',
          containLabel: true,
          backgroundColor: 'transparent'
        },
        xAxis: {
          type: 'category',
          boundaryGap: false,
          data: powerComparison.value.hours || [],
          name: '时间 (时)',
          nameTextStyle: {
            color: 'rgba(255, 255, 255, 0.8)'
          },
          axisLine: {
            lineStyle: {
              color: 'rgba(255, 255, 255, 0.3)'
            }
          },
          axisLabel: {
            color: 'rgba(255, 255, 255, 0.8)'
          },
          splitLine: {
            show: false
          }
        },
        yAxis: {
          type: 'value',
          name: '发电功率 (kW)',
          nameTextStyle: {
            color: 'rgba(255, 255, 255, 0.8)'
          },
          axisLine: {
            lineStyle: {
              color: 'rgba(255, 255, 255, 0.3)'
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
            name: '实测发电量',
            data: powerComparison.value.actual || [],
            type: 'line',
            smooth: true,
            lineStyle: {
              width: 3,
              color: '#67c23a',
              shadowBlur: 10,
              shadowColor: 'rgba(103, 194, 58, 0.7)'
            },
            itemStyle: {
              color: '#67c23a',
              borderColor: 'rgba(39, 64, 139, 0.6)',
              borderWidth: 2,
              shadowBlur: 10,
              shadowColor: 'rgba(103, 194, 58, 0.7)'
            }
          },
          {
            name: '预测发电量',
            data: powerComparison.value.predicted || [],
            type: 'line',
            smooth: true,
            lineStyle: {
              width: 3,
              color: '#409eff',
              type: 'dashed',
              shadowBlur: 10,
              shadowColor: 'rgba(64, 158, 255, 0.7)'
            },
            itemStyle: {
              color: '#409eff',
              borderColor: 'rgba(39, 64, 139, 0.6)',
              borderWidth: 2,
              shadowBlur: 10,
              shadowColor: 'rgba(64, 158, 255, 0.7)'
            }
          }
        ]
      }
      
      powerLineChartInstance.setOption(option)
    }

    // 处理窗口大小变化
    const handleResize = () => {
      faultPieChartInstance?.resize()
      faultLineChartInstance?.resize()
      powerLineChartInstance?.resize()
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
      camera.position.z = 5

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

      // 添加控制器
      controls = new OrbitControls(camera, renderer.domElement)
      controls.enableDamping = true
      controls.dampingFactor = 0.05
      controls.minDistance = 2
      controls.maxDistance = 20

      // 加载GLB模型
      const loader = new GLTFLoader()
      loader.load(
        '/fans/Scene1.glb',
        (gltf) => {
          if (isUnmounted) return
          
          // 获取模型
          const model = gltf.scene
          
          // 调整模型位置和缩放
          // model.position.set(-10.1, 0, -10.5)
          model.position.set(-6.425, 0, -6.425)
          model.scale.set(0.25, 0.25, 0.25) // 根据模型大小调整缩放
          
          // 添加到场景
          scene.add(model)
          
          // 调整相机位置以更好地查看模型
          camera.position.z = 3
          camera.position.x = -5
          camera.position.y = 1.5
        },
        (xhr) => {
          console.log((xhr.loaded / xhr.total * 100) + '% loaded')
        },
        (error) => {
          console.error('Error loading GLB file:', error)
        }
      )

      // 添加光源
      const ambientLight = new THREE.AmbientLight(0xffffff, 1.0)
      scene.add(ambientLight)
      
      const directionalLight = new THREE.DirectionalLight(0xffffff, 2.0)
      directionalLight.position.set(5, 10, 5)
      scene.add(directionalLight)

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

      // 动画循环
      const animate = () => {
        if (isUnmounted) return
        animationId = requestAnimationFrame(animate)
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
      window.handleThreeResize = handleThreeResize
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
      if (window.handleThreeResize) {
        window.removeEventListener('resize', window.handleThreeResize)
        delete window.handleThreeResize
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
    }

    let updateInterval = null
    let isUnmounted = false

    onMounted(() => {
      isUnmounted = false
      // 等待DOM渲染完成
      nextTick(() => {
        if (isUnmounted) return
        initFaultPieChart()
        initFaultLineChart()
        initPowerLineChart()
        initThreeJs()
      })

      // 监听窗口大小变化
      window.addEventListener('resize', handleResize)

      // 初始加载数据
      refreshData()

      // 自动更新数据
      updateInterval = setInterval(() => {
        if (isUnmounted) return
        refreshData()
      }, 30000) // 每30秒自动刷新一次数据
    })

    onUnmounted(() => {
      isUnmounted = true
      if (updateInterval) {
        clearInterval(updateInterval)
      }
      window.removeEventListener('resize', handleResize)
      
      // 销毁图表实例
      faultPieChartInstance?.dispose()
      faultLineChartInstance?.dispose()
      powerLineChartInstance?.dispose()

      // 清理Three.js资源
      cleanupThreeJs()
    })

    return {
      stats,
      filterStatus,
      selectedTurbine,
      sortBy,
      currentPage,
      pageSize,
      dailyStats,
      warnings,
      faultPieChart,
      faultLineChart,
      powerLineChart,
      threeJsContainer,
      formatPower,
      refreshData,
      navigateToTurbine,
      navigateToSettings
    }
  }
}
</script>

<style scoped>
/* 主容器 */
.dashboard-container {
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

/* 背景风电厂分布图 */
.background-map {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(39, 64, 139, 0.5);
  backdrop-filter: blur(5px);
  opacity: 0.5;
  z-index: 1;
}

/* Three.js容器 */
.three-js-container {
  width: 100%;
  height: 100%;
}

.background-map .map-content {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
}

.background-map h3 {
  margin: 0 0 20px 0;
  font-size: calc(20px + 0.5vw);
  font-weight: 600;
  color: white;
  text-shadow: 0 0 10px rgba(79, 195, 247, 0.7);
}

.background-map .map-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  color: white;
}

.background-map .map-placeholder p {
  margin-top: 20px;
  font-size: calc(16px + 0.3vw);
  color: rgba(255, 255, 255, 0.8);
  text-shadow: 0 0 5px rgba(79, 195, 247, 0.5);
}

/* 工具栏 */
.toolbar {
  width: 100%;
  height: 60px;
  padding: 0 10px;
  margin-bottom: 15px;
  z-index: 3;
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
  flex-direction: column;
  gap: 15px;
  padding: 0 10px 10px 10px;
  overflow: hidden;
  z-index: 2;
}

/* 上部分：数据和右侧图表 */
.top-main-content {
  display: flex;
  gap: 15px;
  flex: 1;
  min-height: 0;
}

/* 左侧数据区域 */
.left-data-content {
  width: calc(100% - 25%);
  display: flex;
  gap: 15px;
}

/* 数据部分 */
.data-section {
  width: 15%;
  height: 50%;
}

.data-section .el-card {
  height: 100%;
  border-radius: 12px;
}

.data-content {
  height: 100%;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  gap: 15px;
  padding: 10px;
}

.data-item {
  text-align: center;
  width: 100%;
}

.data-label {
  font-size: 11px;
  color: rgba(255, 255, 255, 0.8);
  margin-bottom: 3px;
}

.data-value {
  font-size: 14px;
  font-weight: 600;
  color: #4FC3F7;
  text-shadow: 0 0 5px rgba(79, 195, 247, 0.5);
}

/* 底部区域：警告信息 */
.bottom-content {
  width: 74%;
  height: 30%;
}

/* 警告信息 */
.warnings-section {
  width: 100%;
  height: 100%;
}

.warnings-section .el-card {
  height: 100%;
  border-radius: 12px;
  display: flex;
  flex-direction: column;
}

.warnings-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
  flex: 1;
  overflow-y: auto;
  padding: 0 20px 20px 20px;
}

/* 自定义滚动条 */
.warnings-list::-webkit-scrollbar {
  width: 6px;
}

.warnings-list::-webkit-scrollbar-track {
  background: rgba(255, 255, 255, 0.1);
  border-radius: 3px;
}

.warnings-list::-webkit-scrollbar-thumb {
  background: rgba(79, 195, 247, 0.5);
  border-radius: 3px;
}

.warnings-list::-webkit-scrollbar-thumb:hover {
  background: rgba(79, 195, 247, 0.8);
}

.warning-item {
  border-radius: 8px;
  font-size: 12px;
  padding: 8px 16px;
  margin-bottom: 5px;
  height: auto;
  min-height: 40px;
}

/* 右侧内容区域（占25%宽度） */
.right-content {
  width: 25%;
  height: 147%;
  display: flex;
  flex-direction: column;
  gap: 15px;
}

/* 图表项 */
.chart-item {
  height: calc((100% - 30px) / 3);
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
  padding: 10px 0;
}

.chart {
  width: 100%;
  height: 100%;
}

/* 卡片头部样式 */
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-header span {
  font-weight: 600;
  font-size: 14px;
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
  
  .left-content {
    flex-direction: column;
  }
  
  .data-section {
    width: 100%;
    height: auto;
  }
  
  .data-content {
    flex-direction: row;
    flex-wrap: wrap;
    gap: 20px;
  }
  
  .data-item {
    flex: 1 1 calc(25% - 20px);
    min-width: 150px;
  }
}

@media (max-width: 768px) {
  .toolbar {
    padding: 0 5px;
  }
  
  .toolbar-content {
    flex-direction: column;
    gap: 10px;
    padding: 10px;
  }
  
  .toolbar-left {
    flex-direction: column;
    gap: 10px;
  }
  
  .toolbar-right {
    flex-wrap: wrap;
    justify-content: center;
    gap: 10px;
  }
  
  .main-content {
    padding: 10px 5px;
    gap: 10px;
  }
  
  .data-item {
    flex: 1 1 100%;
  }
}
</style>