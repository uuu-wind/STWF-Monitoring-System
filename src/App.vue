<template>
  <div id="app">
    <el-container>
      <el-header class="app-header">
        <div class="header-content">
          <div class="logo">
            <el-icon size="28"><WindPower /></el-icon>
            <span class="logo-text">风电智能监控平台</span>
          </div>
          <div class="top-menu">
            <el-menu
              :default-active="$route.path"
              class="top-nav"
              mode="horizontal"
              router
            >
              <el-menu-item index="/">
                <el-icon><Monitor /></el-icon>
                <span>总体预览</span>
              </el-menu-item>
              <el-menu-item index="/analysis">
                <el-icon><Histogram /></el-icon>
                <span>局部分析</span>
              </el-menu-item>
            </el-menu>
          </div>
          <div class="header-actions">
            <el-button type="text" :icon="Bell">告警中心</el-button>
            <el-button type="text" :icon="User">管理员</el-button>
            <el-dropdown>
              <span class="el-dropdown-link">
                更多操作<el-icon class="el-icon--right"><arrow-down /></el-icon>
              </span>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item :icon="Document">报表导出</el-dropdown-item>
                  <el-dropdown-item :icon="Setting">系统设置</el-dropdown-item>
                  <el-dropdown-item divided :icon="SwitchButton">退出登录</el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </div>
        </div>
      </el-header>
      
      <el-main class="app-main">
        <router-view />
      </el-main>
    </el-container>
  </div>
</template>

<script>
import {
  WindPower,
  Bell,
  User,
  ArrowDown,
  Document,
  Setting as SettingIcon,
  SwitchButton,
  Monitor,
  Histogram,
  Warning as WarningIcon,
  Calendar,
  DataAnalysis
} from '@element-plus/icons-vue'

export default {
  name: 'App'
}
</script>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

html, body, #app {
  width: 100%;
  height: 100%;
  overflow: hidden;
  font-family: 'Helvetica Neue', Helvetica, 'PingFang SC', 'Hiragino Sans GB',
    'Microsoft YaHei', '微软雅黑', Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  font-size: calc(12px + 0.3vw);
}

#app {
  background: #27408B;
  background: linear-gradient(135deg, #1a237e 0%, #27408B 50%, #1565c0 100%);
  color: white;
}

.app-header {
  background: rgba(39, 64, 139, 0.8);
  backdrop-filter: blur(10px);
  color: white;
  padding: 0 24px;
  display: flex;
  align-items: center;
  height: 60px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.3);
}

.header-content {
  width: 100%;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.top-menu {
  flex: 1;
  margin: 0 40px;
}

.top-nav {
  background: transparent;
  border-bottom: none;
}

.top-nav .el-menu-item {
  color: white;
  height: 60px;
  line-height: 60px;
  font-size: calc(14px + 0.2vw);
}

.top-nav .el-menu-item:hover {
  background: rgba(255, 255, 255, 0.1);
}

.top-nav .el-menu-item.is-active {
  background: rgba(255, 255, 255, 0.2);
  border-bottom: 2px solid #4fc3f7;
}

.logo {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: calc(16px + 0.4vw);
  font-weight: 600;
}

.logo-text {
  font-size: calc(16px + 0.4vw);
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 16px;
}

.header-actions .el-button {
  color: white;
}

.header-actions .el-button:hover {
  background: rgba(255, 255, 255, 0.1);
}

.app-sidebar {
  background: rgba(39, 64, 139, 0.7);
  backdrop-filter: blur(10px);
  border-right: 1px solid rgba(255, 255, 255, 0.1);
}

.sidebar-menu {
  border-right: none;
  height: 100%;
}

.sidebar-menu .el-menu-item {
  color: white;
}

.sidebar-menu .el-menu-item:hover,
.sidebar-menu .el-menu-item.is-active {
  background: rgba(255, 255, 255, 0.1);
  color: #4fc3f7;
}

.app-main {
  padding: 20px;
  background: transparent;
  height: calc(100vh - 60px);
  overflow: hidden;
}

.el-dropdown-link {
  color: white;
  cursor: pointer;
  display: flex;
  align-items: center;
}

/* 自定义卡片样式 */
.el-card {
  background: rgba(39, 64, 139, 0.6);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
}

.el-card__header {
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  color: white;
}

/* 自定义按钮样式 */
.el-button {
  border-color: rgba(255, 255, 255, 0.2);
  background: rgba(255, 255, 255, 0.1);
  color: white;
}

.el-button:hover {
  background: rgba(255, 255, 255, 0.2);
  border-color: rgba(255, 255, 255, 0.3);
  color: white;
}

.el-button--primary {
  background: rgba(79, 195, 247, 0.8);
  border-color: rgba(79, 195, 247, 0.8);
}

.el-button--primary:hover {
  background: rgba(79, 195, 247, 1);
  border-color: rgba(79, 195, 247, 1);
}

/* 自定义输入框样式 */
.el-input__wrapper {
  background: rgba(255, 255, 255, 0.1);
  border-color: rgba(255, 255, 255, 0.2);
}

.el-input__inner {
  color: white;
}

/* 自定义下拉框样式 */
.el-select {
  color: white;
}

.el-select .el-input__inner {
  color: white;
}

/* 自定义标签样式 */
.el-tag {
  background: rgba(79, 195, 247, 0.3);
  border-color: rgba(79, 195, 247, 0.5);
  color: white;
}

/* 自定义警告样式 */
.el-alert {
  background: rgba(255, 255, 255, 0.1);
  border-color: rgba(255, 255, 255, 0.2);
  color: white;
}

.el-alert__title {
  color: white;
}

.el-alert__description {
  color: rgba(255, 255, 255, 0.8);
}
</style>
