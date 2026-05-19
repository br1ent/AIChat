<script setup>
defineProps(["userProfile"])
</script>

<template>
  <div class="flex flex-col items-center mt-8 gap-4 px-4 text-center sm:mt-12 sm:flex-row sm:gap-8 sm:text-left" v-if="userProfile">
    <div class="avatar">
      <div class="w-32 rounded-full sm:w-44">
        <img :src="userProfile.photo" alt="">
      </div>
    </div>
    <div class="flex flex-col justify-center w-full max-w-64 sm:h-44">
      <div class="text-2xl font-bold line-clamp-1 break-all">{{userProfile.username}}</div>
      <div class="text-sm text-gray-500 mt-4">id: {{userProfile.user_id}}</div>
      <div class="text-sm h-20 mt-4 line-clamp-4 break-all">{{userProfile.profile}}</div>
    </div>
  </div>
</template>

<style scoped>

</style>
