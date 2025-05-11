<script setup>
import { NConfigProvider, NMessageProvider, NLoadingBarProvider } from 'naive-ui'
</script>

<template>
  <n-config-provider>
    <n-loading-bar-provider>
      <n-message-provider>
        <div id="app">
          <router-view />
        </div>
      </n-message-provider>
    </n-loading-bar-provider>
  </n-config-provider>
</template>

<style>
#app {
  font-family: 'Avenir', Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  color: #2c3e50;
  width: 100%;
  height: 100vh;
}
</style>
