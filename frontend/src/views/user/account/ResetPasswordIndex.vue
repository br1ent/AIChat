<script setup>
import {ref} from "vue";
import api from "@/js/http/api.js";
import {useRouter} from "vue-router";

const username = ref("");
const password = ref("");
const confirmedPassword = ref('');
const errorMessage = ref("");
const successMessage = ref("");
const router = useRouter("");

async function resetPassword() {
  errorMessage.value = "";
  successMessage.value = "";

  if (!username.value) {
    errorMessage.value = "用户名不能为空！";
  } else if (!password.value) {
    errorMessage.value = "密码不能为空！";
  } else if (confirmedPassword.value !== password.value) {
    errorMessage.value("两次输入的密码不一致！");
  } else {
    try {
     const res = await api.post("/api/user/account/reset_password/", {
       username: username.value,
       password: password.value,
       confirmedPassword: confirmedPassword.value
     });
     const data = res.data;
     if (data.result === "success") {
       successMessage.value = "重置密码成功!";
       setTimeout(async () => {
         await router.push({name: 'user-account-login-index'});
       }, 1000);
     } else {
       errorMessage.value = data.result;
     }
    } catch (err) {
    }
  }
}
</script>

<template>
  <div class="flex justify-center mt-16 px-4 sm:mt-30">
    <form @submit.prevent="resetPassword" class="fieldset bg-base-200 border-base-300 rounded-box w-xs max-w-full border p-4">
      <legend class="fieldset-legend">重置你的账号</legend>

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

      <button class="btn btn-accent mt-4">重置</button>

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
