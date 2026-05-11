<script setup>
import SendIcon from "@/components/character/icons/SendIcon.vue";
import MicIcon from "@/components/character/icons/MicIcon.vue";
</script>

<template>
  <div class="absolute bottom-4 left-2 h-12 w-86 flex items-center">
    <input
        type="text"
        class="input bg-black/30 backdrop-blur-2xl! text-white text-base w-full h-full rounded-2xl pr-20"
        placeholder="文本输入..."
    >
      <div class="flex justify-center items-center absolute right-2 w-8 h-8 cursor-pointer">
        <SendIcon/>
      </div>
      <div class="flex justify-center items-center absolute right-10 w-8 h-8 cursor-pointer">
        <MicIcon/>
      </div>
  </div>

</template>

<style scoped>

</style>