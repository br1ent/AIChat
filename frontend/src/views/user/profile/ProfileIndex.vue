<script setup>
import Photo from "@/views/user/profile/components/Photo.vue";
import Username from "@/views/user/profile/components/Username.vue";
import Profile from "@/views/user/profile/components/Profile.vue";
import {useUserStore} from "@/stores/user.js";
import {ref, useTemplateRef} from "vue";
import api from "@/js/http/api.js";
import {base64ToFile} from "@/js/utils/base64_to_file.js";

const user = useUserStore();

const photoRef = useTemplateRef("photo-ref");
const usernameRef = useTemplateRef("username-ref");
const profileRef = useTemplateRef("profile-ref");
const errorMessage = ref("");
const successMessage = ref("");

async function update() {
  try {
    errorMessage.value = "";
    successMessage.value = "";

    const photo = photoRef.value.myPhoto;
    const username = usernameRef.value.myUsername;
    const profile = profileRef.value.myProfile;

    const formData = new FormData();
    if (!photo) {
      errorMessage.value = "头像不能为空!";
    } else if (!username) {
      errorMessage.value = "用户名不能为空!";
    } else if (!profile) {
      errorMessage.value = "个人简介不能为空!";
    } else if (profile.length > 500) {
      errorMessage.value = "个人简介的字数不能超过500字!";
    } else {
      formData.append("username", username);
      formData.append("profile", profile);
      if (photo !== user.photo)
        formData.append("photo", base64ToFile(photo, "photo.png"));

      const res = await api.post("api/user/profile/update/", formData);
      const data = res.data;
      if (data.result === "success") {
        user.setUserInfo(data);

        successMessage.value = "更新成功!";
        setTimeout(() => {
          successMessage.value = "";
          errorMessage.value = "";
        }, 1000);
      } else {
        errorMessage.value = data.result;
      }
    }
  } catch (e) {
  }
}

</script>

<template>
  <div class="flex justify-center px-4">
    <div class="card bg-base-200 shadow-sm w-full max-w-120 mt-8 sm:mt-16">
      <div class="card-body">
        <h3 class="text-lg font-bold my-4">编辑资料</h3>
        <Photo ref="photo-ref" :photo="user.photo" />
        <Username ref="username-ref" :username="user.username" />
        <Profile ref="profile-ref" :profile="user.profile" />

        <div class="flex justify-center text-sm text-red-500" v-if="errorMessage">{{ errorMessage }}</div>
        <div class="flex justify-center text-sm text-green-500" v-if="successMessage">{{ successMessage }} </div>

        <div class="flex justify-center">
          <button @click="update" class="btn btn-accent w-full max-w-60 mt-4">更新</button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>

</style>
