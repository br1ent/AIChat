<template>
  <NavBar>
    <RouterView/>
  </NavBar>
  <footer class="bg-base-200 text-base-content p-8">
    <div class="text-center">
      <p class="font-bold text-lg">AI Chat</p>
      <p class="text-sm text-gray-500 mt-1">
        An AI-powered chat platform for immersive conversations.<br>
        一个可以与AI角色聊天的网站
      </p>
      <p class="text-sm text-gray-500 mt-4">
        © 2026–现在 AI Chat. All rights reserved. 版权所有
      </p>
      <p class="text-sm text-gray-500 mt-1">
        ICP证：<a class="link link-hover text-gray-500" href="https://beian.miit.gov.cn/" target="_blank">粤ICP备2026068482号-1</a>
      </p>
      <div class="border-t border-gray-600 max-w-md mx-auto my-4"></div>
      <div class="flex justify-center gap-6 text-sm text-gray-500">
        <span class="flex items-center gap-2">
          <EmailIcon class="w-5 h-5"/>
          xbrent8@163.com
        </span>
        <span class="flex items-center gap-2">
          <GitHubIcon class="w-5 h-5"/>
          <a href="https://github.com/br1ent/AIFriends" target="_blank" class="link link-hover text-gray-500">GitHub</a>
        </span>
      </div>
    </div>
  </footer>
</template>

<script setup>
import NavBar from "@/components/navbar/NavBar.vue";
import {onMounted} from "vue";
import api from "@/js/http/api.js";
import {useUserStore} from "@/stores/user.js";
import {useRoute, useRouter} from "vue-router";
import EmailIcon from "@/icon/EmailIcon.vue";
import GitHubIcon from "@/icon/GitHubIcon.vue";


const user = useUserStore();
const route = useRoute();
const router = useRouter();

onMounted(async () => {
  try {
    const res = await api.get("/api/user/account/get_user_info/");
    const data = res.data;
    if (data.result === "success") {
      user.setUserInfo(data);
    }
  } catch (err) {
  } finally {
    user.setHasPullUserInfo(true);

    if (route.meta.requireAuth && !user.isLogin()) {
      await router.replace({
        name: "user-account-login-index"
      });
    }
  }
})
</script>

<style scoped>
</style>