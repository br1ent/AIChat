<script setup>
import {nextTick, onBeforeUnmount, ref, useTemplateRef, watch} from "vue";
import CameraIcon from "@/views/user/profile/components/icons/CameraIcon.vue";
import Croppie from 'croppie'
import 'croppie/croppie.css'

const props = defineProps(["photo"]);
const myPhoto = ref(props.photo);

watch(() => props.photo, newVal => {
  myPhoto.value = newVal
});

const fileInputRef = useTemplateRef("file-input-ref");
const modalRef = useTemplateRef("modal-ref");
const croppieRef = useTemplateRef("croppie-ref");

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

let croppie = null;
async function openModal(photo) {
  modalRef.value.show();
  await nextTick();

  if (!croppie) {
    const boundarySize = window.innerWidth < 640 ? Math.min(window.innerWidth - 48, 280) : 300;
    const viewportSize = window.innerWidth < 640 ? Math.min(180, boundarySize - 40) : 200;
      croppie = new Croppie(croppieRef.value, {
      viewport: {width: viewportSize, height: viewportSize, type: 'square'}, // 裁剪框的长宽和样式
      boundary: {width: boundarySize, height: boundarySize}, // 外边框的长宽
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

  myPhoto.value = await croppie.result({
    type: "base64",
    size: "viewport"
  });

  modalRef.value.close();
}

onBeforeUnmount(() => {
  croppie?.destroy();
})

defineExpose({
  myPhoto
})
</script>

<template>
  <div class="flex justify-center">
    <div class="avatar relative">
      <div class="w-28 rounded-full" v-if="myPhoto">
        <img :src="myPhoto" @click="fileInputRef.click()">
      </div>
      <div v-else class="w-28 h-28 rounded-full bg-base-200"></div>
      <div class="w-28 rounded-full bg-black/20 absolute left-0 top-0 flex justify-center items-center cursor-pointer">
        <CameraIcon @click="fileInputRef.click()"/>
      </div>
    </div>
  </div>

  <input ref="file-input-ref" type="file" class="hidden" accept="image/*" @change="onFileChange">

  <dialog class="modal" ref="modal-ref">
    <div class="modal-box transition-none max-w-[calc(100vw-1rem)]">
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
