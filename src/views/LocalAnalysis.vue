<template>
  <div class="local-analysis-container">
    <!-- 工具栏 -->
    <div class="toolbar">
      <el-card shadow="hover">
        <div class="toolbar-content">
          <div class="toolbar-left">
            <h3>风电智能监控平台</h3>
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
                  <span class="data-value">{{ formatPower(runtimeData.dailyGeneration) }}</span>
                </div>
                <div class="data-item">
                  <span class="data-label">有功功率</span>
                  <span class="data-value">{{ formatPower(runtimeData.activePower) }}</span>
                </div>
                <div class="data-item">
                  <span class="data-label">无功功率</span>
                  <span class="data-value">{{ formatPower(runtimeData.reactivePower) }}</span>
                </div>
                <div class="data-item">
                  <span class="data-label">视在功率</span>
                  <span class="data-value">{{ formatPower(runtimeData.apparentPower) }}</span>
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
                  <span class="info-label">运行小时数</span>
                  <span class="info-value">{{ systemInfo.runHours }} h</span>
                </div>
                <div class="info-item">
                  <span class="info-label">维护周期</span>
                  <span class="info-value">{{ systemInfo.maintenanceCycle }} days</span>
                </div>
                <div class="info-item">
                  <span class="info-label">状态</span>
                  <el-tag :type="systemInfo.status === 'running' ? 'success' : 'warning'">{{ systemInfo.statusText }}</el-tag>
                </div>
              </div>
            </div>
          </el-card>
        </div>
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
              <div class="alert-item">
                <el-progress
                  type="circle"
                  :percentage="alertStats.critical"
                  :color="'#F56C6C'"
                  :stroke-width="8"
                  :width="80"
                >
                  <div class="progress-content">
                    <span class="progress-label">严重</span>
                    <span class="progress-value">{{ alertStats.critical }}</span>
                  </div>
                </el-progress>
              </div>
              <div class="alert-item">
                <el-progress
                  type="circle"
                  :percentage="alertStats.major"
                  :color="'#E6A23C'"
                  :stroke-width="8"
                  :width="80"
                >
                  <div class="progress-content">
                    <span class="progress-label">主要</span>
                    <span class="progress-value">{{ alertStats.major }}</span>
                  </div>
                </el-progress>
              </div>
              <div class="alert-item">
                <el-progress
                  type="circle"
                  :percentage="alertStats.minor"
                  :color="'#409EFF'"
                  :stroke-width="8"
                  :width="80"
                >
                  <div class="progress-content">
                    <span class="progress-label">次要</span>
                    <span class="progress-value">{{ alertStats.minor }}</span>
                  </div>
                </el-progress>
              </div>
            </div>
          </el-card>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, onUnmounted, nextTick } from 'vue'
import * as echarts from 'echarts'
import * as THREE from 'three'
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls'
import { STLLoader } from 'three/examples/jsm/loaders/STLLoader'

// 模拟风机数据
const mockTurbineInfo = {
  name: '北风一号',
  location: '内蒙古风场A区',
  bladeLength: 55,
  rotorDiameter: 112,
  ratedPower: 2500,
  hubHeight: 120,
  bladeCount: 3,
  speedRange: '3-20 RPM'
}

// 模拟运行数据
const mockRuntimeData = {
  dailyGeneration: 28500,
  activePower: 2200,
  reactivePower: 350,
  apparentPower: 2230
}

// 模拟系统信息
const mockSystemInfo = {
  model: 'WTG-2.5MW',
  manufacturer: '新能源科技有限公司',
  installationDate: '2024-03-15',
  runHours: 8640,
  maintenanceCycle: 90,
  status: 'running',
  statusText: '运行中'
}

// 模拟风速风向数据
const mockWindData = {
  speed: 12.5,
  direction: 135
}

// 模拟告警统计数据
const mockAlertStats = {
  critical: 0,
  major: 2,
  minor: 5
}

// 模拟发电量趋势数据
const mockPowerTrend = {
  hours: ['00', '02', '04', '06', '08', '10', '12', '14', '16', '18', '20', '22'],
  power: [850, 720, 680, 1200, 2100, 2800, 3100, 2900, 2700, 2200, 1500, 1000]
}

export default {
  name: 'LocalAnalysis',
  setup() {
    // 响应式数据
    const turbineInfo = ref({ ...mockTurbineInfo })
    const runtimeData = ref({ ...mockRuntimeData })
    const systemInfo = ref({ ...mockSystemInfo })
    const windData = ref({ ...mockWindData })
    const alertStats = ref({ ...mockAlertStats })

    // 图表引用
    const powerChart = ref(null)
    const threeJsContainer = ref(null)

    // 图表实例
    let powerChartInstance = null

    // Three.js相关
    let scene = null
    let camera = null
    let renderer = null
    let controls = null
    let animationId = null
    let fanGroup = null // 用于存储风扇模型的父物体，控制旋转
    let fanGroup2 = null

    // 格式化功率数据
    const formatPower = (power) => {
      if (power >= 1000) {
        return (power / 1000).toFixed(1) + ' MW'
      }
      return power.toFixed(0) + ' kW'
    }

    // 刷新数据
    const refreshData = () => {
      // 模拟数据更新
      runtimeData.value.dailyGeneration += Math.random() * 1000 - 500
      runtimeData.value.activePower += Math.random() * 100 - 50
      runtimeData.value.reactivePower += Math.random() * 50 - 25
      runtimeData.value.apparentPower += Math.random() * 100 - 50
      
      windData.value.speed += Math.random() * 2 - 1
      windData.value.direction += Math.random() * 20 - 10
      
      // 确保值在合理范围内
      windData.value.speed = Math.max(0, Math.min(windData.value.speed, 25))
      windData.value.direction = (windData.value.direction + 360) % 360
      
      // 更新图表
      updatePowerChart()
      
      // 可以添加刷新成功的提示
    }

    // 初始化发电量折线图
    const initPowerChart = () => {
      if (powerChart.value) {
        powerChartInstance = echarts.init(powerChart.value)
        updatePowerChart()
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
            data: mockPowerTrend.hours,
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
            data: mockPowerTrend.power
          }
        ]
      }
      
      powerChartInstance.setOption(option)
    }

    // 初始化Three.js场景
    const initThreeJs = () => {
      if (!threeJsContainer.value) return

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
      const handleResize = () => {
        if (!threeJsContainer.value) return
        camera.aspect = threeJsContainer.value.clientWidth / threeJsContainer.value.clientHeight
        camera.updateProjectionMatrix()
        renderer.setSize(threeJsContainer.value.clientWidth, threeJsContainer.value.clientHeight)
      }
      window.addEventListener('resize', handleResize)
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
      window.removeEventListener('resize', () => {})
    }

    // 处理窗口大小变化
    const handleResize = () => {
      powerChartInstance?.resize()
    }

    onMounted(() => {
      // 等待DOM渲染完成
      nextTick(() => {
        initPowerChart()
        initThreeJs()
      })

      // 监听窗口大小变化
      window.addEventListener('resize', handleResize)

      onUnmounted(() => {
        window.removeEventListener('resize', handleResize)
        
        // 销毁图表实例
        powerChartInstance?.dispose()

        // 清理Three.js资源
        cleanupThreeJs()
      })
    })

    return {
      turbineInfo,
      runtimeData,
      systemInfo,
      windData,
      alertStats,
      powerChart,
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
  padding: 0;
  overflow: hidden;
  background: rgba(39, 64, 139, 0.8);
  backdrop-filter: blur(10px);
  display: flex;
  flex-direction: column;
}

/* 工具栏 */
.toolbar {
  height: 60px;
  padding: 0 20px;
  margin-bottom: 20px;
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
  padding: 0 20px;
}

.toolbar-left {
  display: flex;
  align-items: center;
  gap: 30px;
}

.toolbar-left h3 {
  margin: 0;
  font-size: calc(16px + 0.3vw);
  font-weight: 600;
  color: white;
  text-shadow: 0 0 10px rgba(79, 195, 247, 0.7);
}

/* 导航菜单 */
.nav-menu {
  display: flex;
  gap: 10px;
}

.nav-item {
  padding: 8px 16px;
  border-radius: 6px;
  color: rgba(255, 255, 255, 0.8);
  text-decoration: none;
  font-size: calc(12px + 0.2vw);
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
  gap: 15px;
}

/* 主要内容区域 */
.main-content {
  position: relative;
  width: 100%;
  flex: 1;
  display: flex;
  gap: 20px;
  padding: 0 20px 20px 20px;
  overflow: hidden;
}

/* 左侧区域（占25%宽度） */
.left-content {
  width: 25%;
  height: 100%;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

/* 左侧上部分：风机名称和机械参数（高度25%） */
.left-top-section {
  height: 25%;
  min-height: 200px;
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
  font-size: calc(18px + 0.5vw);
  font-weight: 600;
  color: white;
  text-shadow: 0 0 10px rgba(79, 195, 247, 0.7);
}

.turbine-location {
  margin: 0 0 15px 0;
  font-size: calc(12px + 0.2vw);
  color: rgba(255, 255, 255, 0.8);
}

.mechanical-params {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 10px;
  width: 100%;
  padding: 0 10px;
}

.param-item {
  text-align: center;
  padding: 8px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 6px;
}

.param-label {
  display: block;
  font-size: calc(10px + 0.1vw);
  color: rgba(255, 255, 255, 0.7);
  margin-bottom: 3px;
}

.param-value {
  display: block;
  font-size: calc(12px + 0.2vw);
  font-weight: 600;
  color: white;
}

/* 左侧中部分：发电量和功率数据（高度25%） */
.left-middle-section {
  height: 25%;
  min-height: 200px;
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
  gap: 15px;
  width: 100%;
  padding: 0 15px;
}

.data-item {
  text-align: center;
  padding: 10px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 8px;
}

.data-label {
  display: block;
  font-size: calc(12px + 0.2vw);
  color: rgba(255, 255, 255, 0.8);
  margin-bottom: 5px;
}

.data-value {
  display: block;
  font-size: calc(18px + 0.4vw);
  font-weight: 600;
  color: #4FC3F7;
  text-shadow: 0 0 5px rgba(79, 195, 247, 0.5);
}

/* 左侧下部分：风机系统信息（高度22%） */
.left-bottom-section {
  height: 22%;
  min-height: 180px;
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
  gap: 10px;
  width: 100%;
  padding: 0 10px;
}

.info-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 6px;
}

.info-label {
  font-size: calc(11px + 0.1vw);
  color: rgba(255, 255, 255, 0.8);
}

.info-value {
  font-size: calc(11px + 0.1vw);
  font-weight: 600;
  color: white;
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
  gap: 20px;
}

/* 右侧图表项（各占1/3高度） */
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
  padding: 10px 0;
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
  width: 180px;
  height: 180px;
  border-radius: 50%;
  background: rgba(39, 64, 139, 0.8);
  border: 3px solid rgba(79, 195, 247, 0.8);
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
  font-size: 14px;
  font-weight: 600;
  color: white;
  text-shadow: 0 0 5px rgba(79, 195, 247, 0.8);
}

.compass-direction:nth-child(1) { top: 10px; left: 50%; transform: translateX(-50%); }
.compass-direction:nth-child(2) { top: 50%; right: 10px; transform: translateY(-50%); }
.compass-direction:nth-child(3) { bottom: 10px; left: 50%; transform: translateX(-50%); }
.compass-direction:nth-child(4) { top: 50%; left: 10px; transform: translateY(-50%); }

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
  border-left: 10px solid transparent;
  border-right: 10px solid transparent;
  border-bottom: 80px solid #4FC3F7;
  filter: drop-shadow(0 0 5px rgba(79, 195, 247, 0.8));
  transform-origin: 50% 80px;
}

.wind-speed {
  position: absolute;
  bottom: 25px;
  font-size: 24px;
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
  padding: 10px 0;
}

.alert-item {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.progress-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

.progress-label {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.8);
  margin-bottom: 3px;
}

.progress-value {
  font-size: 18px;
  font-weight: 600;
  color: white;
}

/* 卡片头部样式 */
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-header span {
  font-weight: 600;
  font-size: calc(14px + 0.2vw);
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