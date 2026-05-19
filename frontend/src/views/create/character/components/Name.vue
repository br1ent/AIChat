<script setup>
import {ref, watch} from "vue";

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
    <input type="text" class="input w-full" v-model="myName">
  </fieldset>
</template>

<style scoped>

</style>
