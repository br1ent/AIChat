<script setup>
import {ref} from "vue";
import {useUserStore} from "@/stores/user.js";
import UpdateIcon from "@/components/character/icons/UpdateIcon.vue";
import RemoveIcon from "@/components/character/icons/RemoveIcon.vue";
import api from "@/js/http/api.js";

const props = defineProps(["character", "canEdit"])
const emit = defineEmits(["remove"])
const isHover = ref(false);
const user = useUserStore();

async function removeCharacter() {
  try {
    const res = await api.post("/api/create/character/remove/", {
      character_id: props.character.id
    })
    if (res.data.result === "success") {
      emit("remove", props.character.id);
    }
  } catch (err) {
  }
}
</script>

<template>
<div>
  <div class="avatar cursor-pointer" @mouseover="isHover=true" @mouseout="isHover=false">
    <div class="w-60 h-100 rounded-2xl relative">
      <img :src="character.background_image" alt="聊天背景图片" :class="{'scale-120': isHover}" class="transition-transform duration-300">
      <div class="absolute top-50 left-0 w-60 h-50 bg-linear-to-t from-black/40 to-transparent"></div>
      <div v-if="canEdit && character.author.user_id === user.id" class="absolute right-0 top-50">
        <RouterLink :to="{name: 'update-character-index', params: {character_id: character.id}}" class="btn btn-circle btn-ghost bg-transparent">
          <UpdateIcon />
        </RouterLink>
        <button class="btn btn-circle btn-ghost bg-transparent" @click="removeCharacter">
          <RemoveIcon />
        </button>
      </div>
      <div class="absolute top-54 left-4 avatar">
        <div class="w-16 rounded-full ring-3 ring-white">
          <img :src="character.photo" alt="角色头像">
        </div>
      </div>
      <div class="absolute left-24 top-58 right-4 text-white font-bold line-clamp-1 break-all">
        {{character.name}}
      </div>
      <div class="absolute left-4 top-72 right-4 text-white line-clamp-4 break-all">
        {{character.profile}}
      </div>
    </div>
  </div>
  <RouterLink :to="{name: 'user-space-index', params: {user_id: character.author.user_id}}" class="flex items-center mt-4 gap-2 w-60">
    <div class="avatar">
      <div class="w-7 rounded-full">
        <img :src="character.author.photo" alt="作者头像">
      </div>
    </div>
    <div class="text-sm line-clamp-1 break-all">
      {{character.author.username}}
    </div>
  </RouterLink>

</div>
</template>

<style scoped>

</style>