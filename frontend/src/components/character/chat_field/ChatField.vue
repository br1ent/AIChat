<script setup>
import {computed, nextTick, ref, useTemplateRef} from "vue";
import InputField from "@/components/character/chat_field/input_field/InputField.vue";
import CharacterPhotoField from "@/components/character/chat_field/character_photo_field/CharacterPhotoField.vue";
import ChatHistory from "@/components/character/chat_field/chat_history/ChatHistory.vue";

const props = defineProps(["friend"])
const modalRef = useTemplateRef("modal-ref");
const inputRef = useTemplateRef('input-ref');
const history = ref([]);
const chatHistoryRef = useTemplateRef('chat-history-ref');

async function showModal() {
  modalRef.value.showModal();
  await nextTick();
  inputRef.value.focus();
}

const modalStyle = computed(() => {
  if (props.friend) {
    return {
      backgroundImage: `url(${props.friend.character.background_image})`,
      backgroundSize: 'cover',
      backgroundPosition: 'center',
      backgroundRepeat: 'no-repeat',
    }
  } else {
    return {}
  }
})

function pushBackMessage(msg) {
  history.value.push(msg);
  chatHistoryRef.value.scrollToBottom();
}

function addToLastMessage(delta) {
    if (typeof delta === 'object') {
    history.value.push(delta);
    chatHistoryRef.value.scrollToBottom();
  } else {
    history.value.at(-1).content += delta;
    chatHistoryRef.value.scrollToBottom();
  }
}

function pushFrontMessage(msg) {
  history.value.unshift(msg);
}

defineExpose({
  showModal,
})
</script>

<template>
  <dialog ref="modal-ref" class="modal">
    <div class="modal-box w-90 h-150" :style="modalStyle">
      <button class="btn btn-circle btn-sm btn-ghost bg-transparent float-end" @click="modalRef.close()">X</button>
      <ChatHistory
          ref="chat-history-ref"
          v-if="friend"
          :history="history"
          :friendId="friend.id"
          :character="friend.character"
          @pushFrontMessage="pushFrontMessage"
      />
      <InputField
          ref="input-ref"
          v-if="friend"
          :friendId="friend.id"
          @pushBackMessage="pushBackMessage"
          @addToLastMessage="addToLastMessage"
      />
      <CharacterPhotoField v-if="friend" :character="friend.character"/>
    </div>
  </dialog>
</template>

<style scoped>

</style>