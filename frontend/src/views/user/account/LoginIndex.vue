<script setup>
import {ref} from "vue";
import {useUserStore} from "@/stores/user.js";
import api from "@/js/http/api.js";
import {useRouter} from "vue-router";

const username = ref("");
const password = ref("");
const errorMessage = ref("");
const successMessage = ref("");

const user = useUserStore();
const router = useRouter();

async function login() {
  errorMessage.value = "";
  if (!username.value.trim()) {
    errorMessage.value = "用户名不能为空!";
  } else if (!password.value) {
    errorMessage.value = "密码不能为空!";
  } else {
    try {
      const res = await api.post("api/user/account/login/", {
        username: username.value,
        password: password.value
      })
      const data = res.data;
      if (data.result === "success") {
        successMessage.value = "登录成功!"
        user.setAccessToken(data.access);
        user.setUserInfo(data);
        setTimeout(async () => {
          await router.push({name: 'homepage-index'});
        },1000);
      } else {
        errorMessage.value = data.result
      }
    } catch(err) {
      errorMessage.value = "系统出错,请稍后再试!"
    }
  }
}
</script>

<template>
  <div class="flex justify-center mt-30">
    <form @submit.prevent="login" class="fieldset bg-base-200 border-base-300 rounded-box w-xs border p-4">
      <legend class="fieldset-legend">登录你的账号</legend>

      <label class="label">用户名</label>
      <input type="text" class="input" placeholder="请输入用户名..." v-model="username"/>

      <label class="label">密码</label>
      <input type="password" class="input" placeholder="请输入密码..." v-model="password" />

      <div class="text-sm text-red-500 mt-3 text-center" v-if="errorMessage">
        {{ errorMessage }}
      </div>
      <div class="text-sm text-green-500 mt-3 text-center" v-if="successMessage">
        {{ successMessage }}
      </div>

      <button class="btn btn-accent mt-4">登录</button>

      <div class="text-center mt-2">
        <span class="text-base">还没有账号? </span>
        <router-link :to="{name: 'user-account-register-index'}" class="link link-hover link-info">
          <span class="text-base">立即注册</span>
        </router-link>
        <div>
          <span class="text-base">忘记密码了? </span>
          <router-link :to="{name: 'user-account-reset_password-index'}" class="link link-hover link-info">
            <span class="text-base">重置密码</span>
          </router-link>
        </div>
      </div>
    </form>
  </div>
</template>

<style scoped>

</style>