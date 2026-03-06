<template>
  <el-card class="turbine-card" :class="`status-${turbine.status}`" shadow="hover" @click="navigateToAnalysis">
    <template #header>
      <div class="card-header">
        <div class="header-left">
          <el-tag :type="getStatusType(turbine.status)" size="small">
            {{ getStatusText(turbine.status) }}
          </el-tag>
          <h3>{{ turbine.name }}</h3>
        </div>
        <div class="header-right">
          <span class="location">
            <el-icon><Location /></el-icon>
            {{ turbine.location }}
          </span>
        </div>
      </div>
    </template>

    <div class="turbine-content">
      <!-- 主要指标 -->
      <div class="metrics-grid">
        <div class="metric-item">
          <div class="metric-label">发电功率</div>
          <div class="metric-value">{{ turbine.power.toFixed(0) }} kW</div>
          <div class="metric-trend">
            <el-icon :color="turbine.power > 2000 ? '#67c23a' : '#e6a23c'">
              <TrendCharts />
            </el-icon>
          </div>
        </div>
        
        <div class="metric-item">
          <div class="metric-label">风速</div>
          <div class="metric-value">{{ turbine.windSpeed.toFixed(1) }} m/s</div>
        </div>
        
        <div class="metric-item">
          <div class="metric-label">温度</div>
          <div class="metric-value">{{ turbine.temperature.toFixed(1) }}°C</div>
        </div>
        
        <div class="metric-item">
          <div class="metric-label">振动</div>
          <div class="metric-value">{{ turbine.vibration.toFixed(2) }} mm/s</div>
          <div class="metric-trend">
            <el-icon :color="turbine.vibration > 2.5 ? '#f56c6c' : '#67c23a'">
              <Warning v-if="turbine.vibration > 2.5" />
            </el-icon>
          </div>
        </div>
      </div>

      <!-- 效率条 -->
      <div class="efficiency-section">
        <div class="efficiency-label">运行效率</div>
        <div class="efficiency-bar">
          <el-progress 
            :percentage="turbine.efficiency" 
            :color="getEfficiencyColor(turbine.efficiency)"
            :show-text="false"
          />
          <span class="efficiency-value">{{ turbine.efficiency.toFixed(1) }}%</span>
        </div>
      </div>

      <!-- 故障信息 -->
      <div v-if="turbine.faults && turbine.faults.length > 0" class="faults-section">
        <div class="faults-header">
          <el-icon color="#f56c6c"><Warning /></el-icon>
          <span class="faults-title">故障告警 ({{ getActiveFaultsCount }})</span>
        </div>
        <div class="faults-list">
          <div 
            v-for="fault in activeFaults" 
            :key="fault.id"
            class="fault-item"
            :class="`severity-${fault.severity}`"
          >
            <span class="fault-type">{{ getFaultTypeText(fault.type) }}</span>
            <span class="fault-desc">{{ fault.description }}</span>
            <el-tag size="small" :type="getSeverityType(fault.severity)">
              {{ getSeverityText(fault.severity) }}
            </el-tag>
          </div>
        </div>
      </div>

      <!-- 维护信息 -->
      <div class="maintenance-section">
        <span class="maintenance-label">
          上次维护: {{ turbine.lastMaintenance }}
        </span>
        <el-button type="primary" size="small" text>
          查看详情
          <el-icon><ArrowRight /></el-icon>
        </el-button>
      </div>
    </div>
  </el-card>
</template>

<script>
import {
  Location,
  Warning,
  TrendCharts,
  ArrowRight
} from '@element-plus/icons-vue'
import { useRouter } from 'vue-router'

export default {
  name: 'TurbineCard',
  props: {
    turbine: {
      type: Object,
      required: true
    }
  },
  setup(props) {
    const router = useRouter()

    const navigateToAnalysis = () => {
      router.push({
        path: '/local-analysis',
        query: { id: props.turbine.id }
      })
    }

    return {
      navigateToAnalysis
    }
  },
  components: {
    Location,
    Warning,
    TrendCharts,
    ArrowRight
  },
  computed: {
    activeFaults() {
      return this.turbine.faults ? this.turbine.faults.filter(f => !f.resolved) : []
    },
    getActiveFaultsCount() {
      return this.activeFaults.length
    }
  },
  methods: {
    getStatusType(status) {
      const map = {
        running: 'success',
        warning: 'warning',
        stopped: 'info',
        maintenance: ''
      }
      return map[status] || ''
    },
    getStatusText(status) {
      const map = {
        running: '运行中',
        warning: '告警',
        stopped: '已停机',
        maintenance: '维护中'
      }
      return map[status] || status
    },
    getFaultTypeText(type) {
      const map = {
        gearbox: '齿轮箱',
        generator: '发电机',
        blade: '叶片',
        sensor: '传感器',
        electrical: '电气',
        vibration: '振动'
      }
      return map[type] || type
    },
    getSeverityType(severity) {
      const map = {
        low: '',
        medium: 'warning',
        high: 'danger',
        critical: 'danger'
      }
      return map[severity] || ''
    },
    getSeverityText(severity) {
      const map = {
        low: '低',
        medium: '中',
        high: '高',
        critical: '严重'
      }
      return map[severity] || severity
    },
    getEfficiencyColor(efficiency) {
      if (efficiency >= 90) return '#67c23a'
      if (efficiency >= 80) return '#e6a23c'
      return '#f56c6c'
    }
  }
}
</script>

<style scoped>
.turbine-card {
  margin-bottom: 16px;
  transition: all 0.3s ease;
}

.turbine-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.1);
}

.status-warning {
  border-left: 4px solid #e6a23c;
}

.status-stopped {
  border-left: 4px solid #909399;
}

.status-maintenance {
  border-left: 4px solid #409eff;
}

.status-running {
  border-left: 4px solid #67c23a;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 8px;
}

.header-left h3 {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
}

.location {
  display: flex;
  align-items: center;
  gap: 4px;
  color: #606266;
  font-size: 12px;
}

.metrics-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
  margin-bottom: 16px;
}

.metric-item {
  display: flex;
  flex-direction: column;
  padding: 8px;
  background: #f5f7fa;
  border-radius: 4px;
}

.metric-label {
  font-size: 12px;
  color: #909399;
  margin-bottom: 4px;
}

.metric-value {
  font-size: 18px;
  font-weight: 600;
  color: #303133;
}

.metric-trend {
  margin-top: 4px;
}

.efficiency-section {
  margin: 16px 0;
}

.efficiency-label {
  font-size: 12px;
  color: #909399;
  margin-bottom: 8px;
}

.efficiency-bar {
  display: flex;
  align-items: center;
  gap: 12px;
}

.efficiency-value {
  font-size: 14px;
  font-weight: 600;
  color: #303133;
  min-width: 40px;
}

.faults-section {
  margin: 16px 0;
  padding: 12px;
  background: #fef0f0;
  border-radius: 4px;
  border: 1px solid #fde2e2;
}

.faults-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
}

.faults-title {
  font-size: 14px;
  font-weight: 600;
  color: #f56c6c;
}

.faults-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.fault-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 6px 8px;
  background: white;
  border-radius: 4px;
  font-size: 12px;
}

.fault-type {
  font-weight: 600;
  color: #303133;
  min-width: 60px;
}

.fault-desc {
  flex: 1;
  color: #606266;
  margin: 0 8px;
}

.severity-high,
.severity-critical {
  border-left: 3px solid #f56c6c;
}

.severity-medium {
  border-left: 3px solid #e6a23c;
}

.severity-low {
  border-left: 3px solid #67c23a;
}

.maintenance-section {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 12px;
  border-top: 1px solid #ebeef5;
}

.maintenance-label {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  color: #909399;
}
</style>