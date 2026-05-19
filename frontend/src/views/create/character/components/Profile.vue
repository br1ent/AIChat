<script setup>
import {ref, watch} from "vue";

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
    <textarea class="textarea w-full" rows="6" v-model="myProfile"></textarea>
  </div>
</template>

<style scoped>

</style>
