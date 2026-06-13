<script setup>
import {ref, watch} from "vue";
import {TEXT_INPUT_DISABLED} from "@/js/config/config.js";

const props = defineProps(["username"]);
const myUsername = ref(props.username);

watch(() => props.username, newVal => {
  myUsername.value = newVal;
})

defineExpose({
  myUsername
})
</script>

<template>
  <fieldset class="fieldset">
    <label class="label text-base">用户名</label>
    <input class="input w-full" type="text" v-model="myUsername" :disabled="TEXT_INPUT_DISABLED">
  </fieldset>

</template>

<style scoped>

</style>
