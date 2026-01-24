<template>
  <div id="app">
    <el-container>
      <el-header class="app-header">
      </el-header>
      
      <el-main class="app-main">
        <router-view />
      </el-main>
    </el-container>
  </div>
</template>

<script>
import { ref, onMounted, onBeforeUnmount } from 'vue'


export default {
  name: 'App',
  components: {
  },
  setup() {
    return {}
  }
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
  display: none;
}

/* 应用级别样式调整，删除滚动条并使局部分析面板自适应 */
.app-main {
  padding: 20px;
  background: transparent;
  height: 100vh;
  overflow: visible; /* 删除滚动条，改为让内部布局自适应 */
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
