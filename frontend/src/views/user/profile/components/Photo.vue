<script setup>
import {nextTick, onBeforeMount, ref, useTemplateRef, watch} from "vue";
import CameraIcon from "@/views/user/profile/components/icons/CameraIcon.vue";
import Croppie from 'croppie'
import 'croppie/croppie.css'

const props = defineProps(["photo"]);
const myPhoto = ref(props.photo);

watch(() => props.photo, newVal => {
  myPhoto.value = newVal;
})

const fileInputRef = useTemplateRef("file-input-ref");
const modalRef = useTemplateRef("modal-ref");
const croppieRef = useTemplateRef("croppie-ref");

let croppie = null;

async function openModal(photo) {
  modalRef.value.showModal();
  await nextTick();

  if (!croppie) {
    const boundarySize = window.innerWidth < 640 ? Math.min(window.innerWidth - 48, 280) : 300;
    const viewportSize = window.innerWidth < 640 ? Math.min(180, boundarySize - 40) : 200;
    croppie = new Croppie(croppieRef.value, { // 创建croppie对象
    viewport: {width: viewportSize, height: viewportSize, type: 'square'}, // 裁剪框的长宽和样式
    boundary: {width: boundarySize, height: boundarySize}, // 外边框的长宽
    enableOrientation: true,
    enforceBoundary: true,
    });
  }

  croppie.bind({
    url: photo,
  })
}

async function crop() {
  if (!croppie) return;

  myPhoto.value = await croppie.result({
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
    openModal(reader.result)
  };

  reader.readAsDataURL(file);
}

onBeforeMount(() => {
  croppie?.destroy(); // ?是一个语法,如果?是null的话就返回null,不会执行后面的.destory()函数,否则就执行后面的函数
})

defineExpose({
  myPhoto
})
</script>

<template>
  <div class="flex justify-center">
    <div class="avatar">
      <div class="w-28 rounded-full relative">
        <img :src="myPhoto" alt="用户头像"/>
      </div>
      <div @click="fileInputRef.click()" class="absolute left-0 top-0 w-28 h-28 flex justify-center items-center bg-black/20 rounded-full cursor-pointer">
        <CameraIcon/>
      </div>
    </div>
  </div>
  <input type="file" accept="image/*" class="hidden" ref="file-input-ref" @change="onFileChange">

  <dialog class="modal" ref="modal-ref">
    <div class="modal-box transition-none max-w-[calc(100vw-1rem)]">
      <button class="btn btn-circle btn-sm btn-ghost float-end" @click="modalRef.close()">✕</button>

      <!-- 定义croppie绑定的标签 -->
      <div ref="croppie-ref" class="flex flex-col justify-center my-4"></div>

      <div class="modal-action">
        <button class="btn btn-accent" @click="crop">确认</button>
        <button class="btn btn-neutral" @click="modalRef.close()">取消</button>
      </div>
    </div>
  </dialog>
</template>

<style scoped>

</style>
