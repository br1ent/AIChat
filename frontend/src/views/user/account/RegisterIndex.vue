<script setup>
import {ref} from "vue";
import {useUserStore} from "@/stores/user.js";
import api from "@/js/http/api.js";
import {useRouter} from "vue-router";

const username = ref("");
const password = ref("");
const confirmedPassword = ref("");
const errorMessage = ref("");
const successMessage = ref("");

const user = useUserStore();
const router = useRouter();

async function register() {
  errorMessage.value = "";
  if (!username.value.trim()) {
    errorMessage.value = "用户名不能为空!";
  } else if (!password.value) {
    errorMessage.value = "密码不能为空!";
  } else if (confirmedPassword.value !== password.value) {
    errorMessage.value = "两次输入的密码不一致!";
  } else {
    try {
      const res = await api.post("api/user/account/register/", {
        username: username.value,
        password: password.value,
      });
      const data = res.data;
      if (data.result === "success") {
        successMessage.value = "注册成功!";
        user.setAccessToken(data.access);
        user.setUserInfo(data);
        setTimeout(async () => {
          await router.push({name: 'user-account-login-index'});
        }, 1000);
      } else {
        errorMessage.value = data.result;
      }
    } catch(err) {
      errorMessage.value = "系统出错,请稍后再试!";
    }
  }
}
</script>

<template>
  <div class="flex justify-center mt-30">
    <form @submit.prevent="register" class="fieldset bg-base-200 border-base-300 rounded-box w-xs border p-4">
      <legend class="fieldset-legend">注册你的账号</legend>

      <label class="label">用户名</label>
      <input type="text" class="input" placeholder="请输入用户名..." v-model="username" />

      <label class="label">密码</label>
      <input type="password" class="input" placeholder="请输入密码..." v-model="password" />

      <label class="label">确认密码</label>
      <input type="password" class="input" placeholder="请确认密码..." v-model="confirmedPassword" />

      <div class="text-sm text-red-500 mt-3 text-center" v-if="errorMessage">
        {{ errorMessage }}
      </div>
            <div class="text-sm text-green-500 mt-3 text-center" v-if="successMessage">
        {{ successMessage }}
      </div>

      <button class="btn btn-accent mt-4">注册</button>

      <div class="text-center mt-2">
        <span class="text-base">已有账号? </span>
        <router-link :to="{name: 'user-account-login-index'}" class="link link-hover link-info">
          <span class="text-base">返回</span>
        </router-link>
      </div>
    </form>
  </div>
</template>

<style scoped>

</style>