<script setup>
import { RouterLink } from "vue-router";
</script>

<template>
  <div class="flex flex-col items-center justify-center min-h-[60vh] gap-4">
    <div class="text-8xl font-black text-gray-500 select-none">
      404
    </div>
    <p class="text-lg text-gray-400">页面未找到</p>
    <p class="text-sm text-gray-500">你访问的页面不存在或已被移除</p>
    <RouterLink to="/" class="btn btn-neutral btn-sm mt-4">
      返回首页
    </RouterLink>
  </div>
</template>

<style scoped>
</style>
