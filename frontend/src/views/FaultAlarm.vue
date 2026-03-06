<template>
  <div class="fault-alarm-container">
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
              <router-link to="/fault-alarm" class="nav-item active">故障告警</router-link>
              <!--<router-link to="/local-analysis" class="nav-item">局部分析</router-link> -->
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

    <div class="main-content">
      <div class="chart-column">
        <el-card shadow="hover" class="chart-card">
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

      <div class="chart-column">
        <el-card shadow="hover" class="chart-card">
          <template #header>
            <div class="card-header">
              <span>每日主故障数</span>
            </div>
          </template>
          <div class="chart-container">
            <div ref="faultLineChart" class="chart"></div>
          </div>
        </el-card>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, onUnmounted, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import * as echarts from 'echarts'
import axios from 'axios'
import { Refresh, Setting, WindPower } from '@element-plus/icons-vue'

const API_BASE_URL = 'http://localhost:8000/api'

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  }
})

export default {
  name: 'FaultAlarm',
  setup() {
    const router = useRouter()
    const selectedTurbine = ref('')
    const faultDistribution = ref([])
    const dailyFaults = ref({ dates: [], counts: [] })

    const faultPieChart = ref(null)
    const faultLineChart = ref(null)

    let faultPieChartInstance = null
    let faultLineChartInstance = null
    let updateInterval = null

    const navigateToTurbine = (turbineId) => {
      if (turbineId) {
        router.push(`/local-analysis/${turbineId}`)
      }
    }

    const navigateToSettings = () => {
      router.push('/settings')
    }

    const initFaultPieChart = () => {
      if (faultPieChart.value) {
        if (faultPieChart.value.clientWidth === 0 || faultPieChart.value.clientHeight === 0) {
          setTimeout(() => {
            initFaultPieChart()
          }, 100)
          return
        }
        faultPieChartInstance = echarts.init(faultPieChart.value)
        updateFaultPieChart()
      }
    }

    const updateFaultPieChart = () => {
      if (!faultPieChartInstance) {
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
            fontSize: 11
          }
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

    const initFaultLineChart = () => {
      if (faultLineChart.value) {
        if (faultLineChart.value.clientWidth === 0 || faultLineChart.value.clientHeight === 0) {
          setTimeout(() => {
            initFaultLineChart()
          }, 100)
          return
        }
        faultLineChartInstance = echarts.init(faultLineChart.value)
        updateFaultLineChart()
      }
    }

    const updateFaultLineChart = () => {
      if (!faultLineChartInstance) {
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

    const fetchFaultDistribution = async () => {
      try {
        const response = await apiClient.get('/faults/distribution')
        faultDistribution.value = response.data
        updateFaultPieChart()
      } catch (error) {
        console.error('获取故障分布数据失败:', error)
        ElMessage.error('获取故障分布数据失败')
      }
    }

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

    const refreshData = async () => {
      try {
        await Promise.all([
          fetchFaultDistribution(),
          fetchDailyFaults()
        ])
        ElMessage.success('故障数据已刷新')
      } catch (error) {
        console.error('刷新故障数据失败:', error)
        ElMessage.error('刷新故障数据失败')
      }
    }

    const handleResize = () => {
      faultPieChartInstance?.resize()
      faultLineChartInstance?.resize()
    }

    onMounted(() => {
      nextTick(() => {
        initFaultPieChart()
        initFaultLineChart()
      })

      window.addEventListener('resize', handleResize)
      refreshData()
      updateInterval = setInterval(refreshData, 30000)
    })

    onUnmounted(() => {
      if (updateInterval) {
        clearInterval(updateInterval)
      }
      window.removeEventListener('resize', handleResize)
      faultPieChartInstance?.dispose()
      faultLineChartInstance?.dispose()
    })

    return {
      selectedTurbine,
      faultPieChart,
      faultLineChart,
      refreshData,
      navigateToSettings,
      navigateToTurbine,
      Refresh,
      Setting,
      WindPower
    }
  }
}
</script>

<style scoped>
.fault-alarm-container {
  width: 100%;
  height: 100%;
  padding: 10px;
  background: rgba(39, 64, 139, 0.8);
  backdrop-filter: blur(10px);
  display: flex;
  flex-direction: column;
}

.toolbar {
  width: 100%;
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

.main-content {
  flex: 1;
  min-height: 0;
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 15px;
  padding: 0 10px 10px 10px;
}

.chart-column,
.chart-card {
  width: 100%;
  height: 100%;
}

.chart-card {
  border-radius: 12px;
  display: flex;
  flex-direction: column;
}

.chart-container {
  flex: 1;
  min-height: 0;
  padding: 10px 0;
}

.chart {
  width: 100%;
  height: 100%;
}

.card-header span {
  font-weight: 600;
  font-size: 14px;
  color: white;
}

@media (max-width: 1000px) {
  .main-content {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .toolbar {
    height: auto;
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
  }
}
</style>
