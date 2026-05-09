<script setup>
import {ref} from "vue";
import {useUserStore} from "@/stores/user.js";
import UpdateIcon from "@/components/character/icons/UpdateIcon.vue";

const props = defineProps(["character", "canEdit"])
const isHover = ref(false);
const user = useUserStore();

</script>

<template>
<div>
  <div class="avatar cursor-pointer" @mouseover="isHover=true" @mouseout="isHover=false">
    <div class="w-60 h-100 rounded-2xl relative">
      <img :src="character.background_image" alt="聊天背景图片" :class="{'scale-120': isHover}" class="transition-transform duration-300">
      <div class="absolute top-50 left-0 w-60 h-50 bg-linear-to-t from-black/40 to-transparent"></div>
      <div v-if="canEdit && character.author.user_id === user.id" class="absolute right-0 top-50">
        <RouterLink :to="{name: 'update-character-index', params: {character_id: character.id}}" class="btn btn-circle btn-ghost">
          <UpdateIcon />
        </RouterLink>
      </div>
    </div>
  </div>
  <div>

  </div>
</div>
</template>

<style scoped>

</style>