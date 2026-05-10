<script setup>
import {nextTick, onBeforeUnmount, ref, useTemplateRef, watch} from "vue";
import CameraIcon from "@/views/user/profile/components/icons/CameraIcon.vue";
import Croppie from 'croppie'
import 'croppie/croppie.css'

const props = defineProps(["backgroundImage"]);
const myBackgroundImage = ref(props.backgroundImage);

watch(() => props.backgroundImage, newVal => {
  myBackgroundImage.value = newVal;
});

const fileUploadRef = useTemplateRef("file-upload-ref");
const modalRef = useTemplateRef("modal-ref");
const croppieRef = useTemplateRef("croppie-ref");

let croppie = null;

async function openModal(photo) {
  modalRef.value.show();
  await nextTick();

  if (!croppie) {
    croppie = new Croppie(croppieRef.value, {
        viewport: {width: 300, height: 500}, // 裁剪框的长宽和样式
        boundary: {width: 600, height: 600}, // 外边框的长宽
        enableOrientation: true,
        enforceBoundary: true,
    });
  }

  croppie.bind({
    url: photo
  });
}

async function crop() {
  if (!croppie) return;

  myBackgroundImage.value = await croppie.result({
    type: "base64",
    size: "viewport"
  });

  modalRef.value.close();
}

function onFileChange(e) {
  const file = e.target.files[0];
  e.target.value = "";
  if (!file) return;

  const reader = new FileReader();
  reader.onload = () => {
    openModal(reader.result);
  }

  reader.readAsDataURL(file);
}

onBeforeUnmount(() => {
  croppie?.destroy();
})

defineExpose({
  myBackgroundImage
})
</script>

<template>
  <fieldset class="fieldset">
    <label class="label text-base">聊天背景</label>
    <div class="avatar relative">
      <div class="w-15 h-25 rounded-box" v-if="myBackgroundImage">
        <img :src="myBackgroundImage" @click="fileUploadRef.click()">
      </div>
      <div v-else class="w-15 h-25 bg-base-200 rounder-box"></div>
      <div class="w-15 h-25 rounded-box absolute left-0 top-0 flex justify-center items-center bg-black/20 cursor-pointer">
        <CameraIcon @click="fileUploadRef.click()"/>
      </div>
    </div>
  </fieldset>
  <input type="file" accept="image/*" class="hidden" ref="file-upload-ref" @change="onFileChange">

    <dialog class="modal" ref="modal-ref">
    <div class="modal-box transition-none max-w-2xl">
      <button class="btn btn-circle btn-sm btn-ghost float-end" @click="modalRef.close()">✕</button>

      <div ref="croppie-ref" class="flex flex-col justify-center my-4"></div>

      <div class="modal-action">
        <button class="btn btn-accent" @click="crop">保存</button>
        <button class="btn btn-neutral" @click="modalRef.close()">取消</button>
      </div>
    </div>
  </dialog>

</template>

<style scoped>

</style>