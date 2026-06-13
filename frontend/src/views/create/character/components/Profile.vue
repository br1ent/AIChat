<script setup>
import {ref, watch} from "vue";
import {TEXT_INPUT_DISABLED} from "@/js/config/config.js";

const props = defineProps(["profile"]);
const myProfile = ref(props.profile);

watch(() => props.profile, newVal => {
  myProfile.value = newVal;
});

defineExpose({
  myProfile
});
</script>

<template>
  <div class="fieldset">
    <label class="label text-base">角色简介</label>
    <textarea class="textarea w-full" rows="6" v-model="myProfile" :disabled="TEXT_INPUT_DISABLED"></textarea>
  </div>
</template>

<style scoped>

</style>
