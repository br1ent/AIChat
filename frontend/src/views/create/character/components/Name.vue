<script setup>
import {ref, watch} from "vue";
import {TEXT_INPUT_DISABLED} from "@/js/config/config.js";

const props = defineProps(["name"])
const myName = ref(props.name)

watch(() => props.name, newVal => {
  myName.value = newVal;
})

defineExpose({
  myName
})
</script>

<template>
  <fieldset class="fieldset">
    <label class="label text-base">角色名字</label>
    <input type="text" class="input w-full" v-model="myName" :disabled="TEXT_INPUT_DISABLED">
  </fieldset>
</template>

<style scoped>

</style>
