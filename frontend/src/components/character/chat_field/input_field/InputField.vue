<script setup>
import SendIcon from "@/components/character/icons/SendIcon.vue";
import MicIcon from "@/components/character/icons/MicIcon.vue";
import {onUnmounted, ref, useTemplateRef} from "vue";
import streamApi from "@/js/http/streamApi.js";
import Microphone from "@/components/character/chat_field/input_field/Microphone.vue";

const inputRef = useTemplateRef('input-ref');
const message = ref("");
const props = defineProps(["friendId"]);
const emit = defineEmits(["pushBackMessage", "addToLastMessage"])
let processId = 0;
const showMic = ref(false);

let mediaSource = null;
let sourceBuffer = null;
let audioPlayer = new Audio(); // 全局播放器实例
let audioQueue = [];           // 待写入 Buffer 的二进制队列
let isUpdating = false;        // Buffer 是否正在写入

const initAudioStream = () => {
    audioPlayer.pause();
    audioQueue = [];
    isUpdating = false;

    mediaSource = new MediaSource();
    audioPlayer.src = URL.createObjectURL(mediaSource);

    mediaSource.addEventListener('sourceopen', () => {
        try {
            sourceBuffer = mediaSource.addSourceBuffer('audio/mpeg');
            sourceBuffer.addEventListener('updateend', () => {
                isUpdating = false;
                processQueue();
            });
        } catch (e) {
        }
    });

    audioPlayer.play().catch(e => console.error("等待用户交互以播放音频"));
};

const processQueue = () => {
    if (isUpdating || audioQueue.length === 0 || !sourceBuffer || sourceBuffer.updating) {
        return;
    }

    isUpdating = true;
    const chunk = audioQueue.shift();
    try {
        sourceBuffer.appendBuffer(chunk);
    } catch (e) {
        isUpdating = false;
    }
};

const stopAudio = () => {
    audioPlayer.pause();
    audioQueue = [];
    isUpdating = false;

    if (mediaSource) {
        if (mediaSource.readyState === 'open') {
            try {
                mediaSource.endOfStream();
            } catch (e) {
            }
        }
        mediaSource = null;
    }

    if (audioPlayer.src) {
        URL.revokeObjectURL(audioPlayer.src);
        audioPlayer.src = '';
    }
};

const handleAudioChunk = (base64Data) => {  // 将语音片段添加到播放器队列中
    try {
        const binaryString = atob(base64Data);
        const len = binaryString.length;
        const bytes = new Uint8Array(len);
        for (let i = 0; i < len; i++) {
            bytes[i] = binaryString.charCodeAt(i);
        }

        audioQueue.push(bytes);
        processQueue();
    } catch (e) {
    }
};

onUnmounted(() => {
    audioPlayer.pause();
    audioPlayer.src = '';
});


function focus() {
  inputRef.value.focus();
}

async function sendMessage(event, audio_msg) {
  let content;
  if (audio_msg) {
    content = audio_msg.trim();
  } else {
    content = message.value.trim();
  }

  if (!content) return;

  initAudioStream();

  const curId = ++ processId;

  message.value = "";

  emit("pushBackMessage", {role: 'user', content: content, id: crypto.randomUUID()}) // 添加用户信息
  emit("addToLastMessage", {role: 'ai', content: "", id: crypto.randomUUID()})

  try {
    await streamApi('/api/friend/message/chat/', {
      body: {
        friend_id: props.friendId,
        message: content
      },
      onmessage(data, isDone) {
        if (curId !== processId) return;
        if (data.content) {
          emit("addToLastMessage", data.content)
        }
        if (data.audio) {
          handleAudioChunk(data.audio);
        }
      },
      onerror(err) {
      }
    })
  } catch (err) {
  }
}

function close() {
  ++ processId;
  showMic.value = false;
  stopAudio();
}

function handleStop() {
  ++ processId;
  stopAudio();
}

defineExpose({
  focus,
  close
})
</script>

<template>
  <form v-if="!showMic" @submit.prevent="sendMessage" class="absolute bottom-4 left-2 h-12 w-86 flex items-center">
    <input
        ref="input-ref"
        type="text"
        class="input bg-black/30 backdrop-blur-sm text-white text-base w-full h-full rounded-2xl pr-20"
        placeholder="文本输入..."
        v-model="message"
    >
      <div class="flex justify-center items-center absolute right-2 w-8 h-8 cursor-pointer" @click="sendMessage">
        <SendIcon/>
      </div>
      <div class="flex justify-center items-center absolute right-10 w-8 h-8 cursor-pointer" @click="showMic = true">
        <MicIcon/>
      </div>
  </form>
  <Microphone
      v-else
      @close="showMic = false"
      @send="sendMessage"
      @stop="handleStop"
  />
</template>

<style scoped>

</style>