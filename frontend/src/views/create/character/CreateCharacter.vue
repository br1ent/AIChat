<script setup>
import Photo from "@/views/create/character/components/Photo.vue";
import Profile from "@/views/create/character/components/Profile.vue";
import BackgroundImage from "@/views/create/character/components/BackgroundImage.vue";
import Name from "@/views/create/character/components/Name.vue";
import {onMounted, ref, useTemplateRef} from "vue";
import api from "@/js/http/api.js";
import {base64ToFile} from "@/js/utils/base64_to_file.js";
import {useRouter} from "vue-router";
import {useUserStore} from "@/stores/user.js";
import Voice from "@/views/create/character/components/Voice.vue";

const photoRef = useTemplateRef("photo-ref");
const nameRef = useTemplateRef("name-ref");
const voiceRef = useTemplateRef("voice-ref");
const profileRef = useTemplateRef("profile-ref");
const backgroundImageRef = useTemplateRef("background-image-ref");

const errorMessage = ref("");
const successMessage = ref("");
const voices = ref([]);
const curVoiceId = ref(null);

const router = useRouter();
const user = useUserStore();

onMounted(async () => {
  try {
    const res = await api.get('/api/create/character/voice/get_list/', {});
    const data = res.data;
    if (data.result === "success") {
      voices.value = data.voices;
      curVoiceId.value = data.voices[0].id;
    }
  } catch (err) {
    console.error(err);
  }
})

async function create() {
  const photo = photoRef.value.myPhoto;
  const name = nameRef.value.myName?.trim();
  const voice = voiceRef.value.myVoice;
  const profile = profileRef.value.myProfile?.trim();
  const backgroundImage = backgroundImageRef.value.myBackgroundImage;
  errorMessage.value = "";
  successMessage.value = "";

  if (!photo) {
    errorMessage.value = "角色头像不能为空!";
  } else if (!name) {
    errorMessage.value = "角色名字不能为空!";
  } else if (!voice) {
    errorMessage.value = "音色不能为空!";
  } else if (!profile) {
    errorMessage.value = "角色简介不能为空!";
  } else if (profile.length > 100000) {
    errorMessage.value = "角色简介的长度不能超过100000字!";
  } else if (!backgroundImage) {
    errorMessage.value = "角色的背景图片不能为空!";
  } else {
    const formData = new FormData();
    formData.append("photo", base64ToFile(photo, "photo.png"));
    formData.append("name", name);
    formData.append("voice_id", voice)
    formData.append("profile", profile);
    formData.append("background_image", base64ToFile(backgroundImage, "background_image.png"));

    try {
      const res = await api.post("/api/create/character/create/", formData);
      const data = res.data;
      if (data.result === "success") {
        successMessage.value = "创建成功!";
        setTimeout(() => {
          successMessage.value = "";
          errorMessage.value = "";
        }, 1000);

        await router.push({
          name: 'user-space-index',
          params: {
            user_id: user.id
          }
        });
      } else {
        errorMessage.value = data.result;
        setTimeout(() => {
          errorMessage.value = "";
        },1000)
      }
    } catch (err) {
    }
  }
}
</script>

<template>
  <div class="flex justify-center px-4">
    <div class="card w-full max-w-120">
      <div class="card-body w-full bg-base-200 shadow-sm mt-8 sm:mt-16">
        <h3 class="text-lg font-bold my-4">创建角色</h3>
        <Photo ref="photo-ref"/>
        <Name ref="name-ref" />
        <Voice ref="voice-ref" :voices="voices" :curVoiceId="curVoiceId"/>
        <Profile ref="profile-ref" />
        <BackgroundImage ref="background-image-ref" />

        <p class="text-sm text-red-500 flex justify-center" v-if="errorMessage">{{ errorMessage }}</p>
        <p class="text-sm text-green-500 flex justify-center" v-if="successMessage">{{ successMessage }}</p>

        <div class="flex justify-center">
          <button class="btn btn-accent w-full max-w-60 mt-2" @click="create">创建</button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>

</style>
