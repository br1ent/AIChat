<script setup>
import {ref, useTemplateRef} from "vue";
import {useUserStore} from "@/stores/user.js";
import UpdateIcon from "@/components/character/icons/UpdateIcon.vue";
import RemoveIcon from "@/components/character/icons/RemoveIcon.vue";
import api from "@/js/http/api.js";
import ChatField from "@/components/character/chat_field/ChatField.vue";
import {useRouter} from "vue-router";

const props = defineProps(["character", "canEdit", "canRemove", "friendId"]);
const emit = defineEmits(["remove"]);
const isHover = ref(false);
const user = useUserStore();

const chatFieldRef = useTemplateRef("chat-field-ref");
const friend = ref(null);
const router = useRouter();

const modalRef = useTemplateRef("modal-ref");
const pendingRemove = ref(null);

async function openChatField() {
  if (!user.isLogin()) {
    await router.push({
      name: "user-account-login-index"
    })
  } else {
    try {
      const res = await api.post("/api/friend/get_or_create/", {
        character_id: props.character.id
      })
      const data = res.data;
      if (data.result === "success") {
        friend.value = data.friend;
        chatFieldRef.value.showModal()
      }
    } catch (err) {
    }
  }
}

function removeCharacter() {
  pendingRemove.value = "character";
  modalRef.value.showModal();
}

function removeFriend() {
  pendingRemove.value = "friend";
  modalRef.value.showModal();
}

function cancelRemove() {
  pendingRemove.value = null;
  modalRef.value.close();
}

async function confirmRemove() {
  if (pendingRemove.value === "character") {
    try {
      const res = await api.post("/api/create/character/remove/", {
        character_id: props.character.id
      })
      if (res.data.result === "success") {
        emit("remove", props.character.id);
      }
    } catch (err) {
    }
  } else if (pendingRemove.value === "friend") {
    try {
      const res = await api.post("/api/friend/remove/", {
       friend_id: props.friendId
      })
      if (res.data.result === "success") {
        emit("remove", props.friendId);
      }
    } catch(err) {
    }
  }
  modalRef.value.close();
  pendingRemove.value = null;
}
</script>

<template>
  <div>
    <div class="avatar cursor-pointer" @mouseover="isHover=true" @mouseout="isHover=false" @click="openChatField">
      <div class="w-[min(15rem,calc(100vw-2rem))] sm:w-60 aspect-[3/5] rounded-2xl relative overflow-hidden">
        <img :src="character.background_image" alt="聊天背景图片" :class="{'scale-120': isHover}" class="w-full h-full object-cover transition-transform duration-300">
        <div class="absolute top-1/2 left-0 w-full h-1/2 bg-linear-to-t from-black/40 to-transparent"></div>

        <div v-if="canEdit && character.author.user_id === user.id" class="absolute right-1 top-2">
          <RouterLink @click.stop :to="{name: 'update-character-index', params: {character_id: character.id}}" class="btn btn-circle btn-ghost bg-transparent">
            <UpdateIcon />
          </RouterLink>
          <button class="btn btn-circle btn-ghost bg-transparent" @click.stop="removeCharacter">
            <RemoveIcon />
          </button>
        </div>

        <div v-if="canRemove" class="absolute right-1 top-2">
          <button class="btn btn-ghost btn-circle bg-transparent" @click.stop="removeFriend">
            <RemoveIcon/>
          </button>
        </div>

        <div class="absolute top-[54%] left-4 avatar">
          <div class="w-16 rounded-full ring-3 ring-white">
            <img :src="character.photo" alt="角色头像">
          </div>
        </div>
        <div class="absolute left-24 top-[58%] right-4 text-white font-bold line-clamp-1 break-all">
          {{character.name}}
        </div>
        <div class="absolute left-4 top-[72%] right-4 text-white line-clamp-4 break-all">
          {{character.profile}}
        </div>
      </div>
    </div>
    <RouterLink :to="{name: 'user-space-index', params: {user_id: character.author.user_id}}" class="flex items-center mt-4 gap-2 w-[min(15rem,calc(100vw-2rem))] sm:w-60">
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
  <dialog ref="modal-ref" class="modal" @close="cancelRemove">
    <div class="modal-box">
      <p class="text-lg font-medium mb-1">确认删除</p>
      <p class="text-sm text-gray-400">
        <template v-if="pendingRemove === 'character'">
          确定要移除角色「{{ character.name }}」吗？此操作不可撤销。
        </template>
        <template v-else-if="pendingRemove === 'friend'">
          确定要移除好友「{{ character.name }}」吗？
        </template>
      </p>
      <div class="modal-action">
        <button class="btn btn-neutral" @click="cancelRemove">取消</button>
        <button class="btn btn-error" @click="confirmRemove">确认删除</button>
      </div>
    </div>
  </dialog>
  <ChatField ref="chat-field-ref" :friend="friend"/>
</template>

<style scoped>

</style>
