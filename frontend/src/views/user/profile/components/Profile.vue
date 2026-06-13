<script setup>
import {ref, watch} from "vue";
import {TEXT_INPUT_DISABLED} from "@/js/config/config.js";

const props = defineProps(["profile"]);
const myProfile = ref(props.profile);

watch(() => props.profile, newVal => {
  myProfile.value = newVal;
})

defineExpose({
  myProfile
})
</script>

<template>
  <fieldset class="fieldset">
    <label class="label test-base">个人简介</label>
    <textarea v-model="myProfile" rows="6" class="textarea w-full" :disabled="TEXT_INPUT_DISABLED"></textarea>
  </fieldset>
</template>

<style scoped>

</style>
