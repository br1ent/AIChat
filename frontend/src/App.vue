<template>
  <NavBar>
    <RouterView/>
  </NavBar>
  <footer class="footer sm:footer-horizontal bg-base-200 text-base-content p-10 flex justify-center">
    <aside>
      <div>
        <span>ICP证：</span>
        <a class="link-primary" href="https://beian.miit.gov.cn/" target="_blank">粤ICP备2026068482号-1</a>
      </div>
    </aside>
  </footer>
</template>

<script setup>
import NavBar from "@/components/navbar/NavBar.vue";
import {onMounted} from "vue";
import api from "@/js/http/api.js";
import {useUserStore} from "@/stores/user.js";
import {useRoute, useRouter} from "vue-router";


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