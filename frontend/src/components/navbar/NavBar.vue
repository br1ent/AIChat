<template>
  <div class="drawer lg:drawer-open">
    <input id="my-drawer-4" type="checkbox" class="drawer-toggle" />
    <div class="drawer-content">
      <nav class="navbar w-full bg-base-100 shadow-sm flex-wrap gap-y-2">
        <div class="navbar-start flex-1 min-w-0">
          <label for="my-drawer-4" aria-label="open sidebar" class="btn btn-square btn-ghost">
            <MenuIcon></MenuIcon>
          </label>
          <div class="px-2 font-bold text-xl sm:text-2xl truncate">AI Chat</div>
        </div>
        <div class="navbar-center order-3 w-full max-w-none px-2 pb-2 flex justify-center lg:order-none lg:w-4/5 lg:max-w-180 lg:px-0 lg:pb-0">
          <form @submit.prevent="search" class="join flex w-full justify-center lg:w-4/5">
            <input class="input join-item rounded-l-full min-w-0 flex-1" placeholder="搜索你感兴趣的内容" v-model="searchQuery"/>
            <button class="btn join-item rounded-r-full gap-1 shrink-0 px-3 sm:px-4">
              <SearchIcon></SearchIcon>
              <span class="hidden sm:inline">搜索</span>
            </button>
          </form>
        </div>
        <div class="navbar-end w-auto">
          <router-link :to="{name: 'create-index'}" v-if="user.isLogin()" active-class="btn-active" class="btn btn-gosh text-base mr-2 sm:mr-6">
            <CreateIcon></CreateIcon>
            <span class="hidden sm:inline">创作</span>
          </router-link>
          <router-link v-if="user.hasPullUserInfo && !user.isLogin()" :to="{name: 'user-account-login-index'}" active-class="btn-active" class="btn btn-ghost text-lg">
            登录
          </router-link>
          <UserMenu v-else-if="user.isLogin()" />
        </div>
      </nav>
      <slot></slot>
    </div>

    <div class="drawer-side is-drawer-close:overflow-visible">
      <label for="my-drawer-4" aria-label="close sidebar" class="drawer-overlay"></label>
      <div class="flex min-h-full flex-col items-start bg-base-200 is-drawer-close:w-16 is-drawer-open:w-50">
        <ul class="menu w-full grow">
          <li>
            <router-link :to="{name: 'homepage-index'}" active-class="menu-focus" class="is-drawer-close:tooltip is-drawer-close:tooltip-right py-4" data-tip="主页">
              <HomepageIcon></HomepageIcon>
              <span class="is-drawer-close:hidden text-base pl-2 whitespace-nowrap">主页</span>
            </router-link>
          </li>
          <li>
            <router-link :to="{name: 'friend-index'}" active-class="menu-focus" class="is-drawer-close:tooltip is-drawer-close:tooltip-right py-4" data-tip="好友">
              <FriendIcon></FriendIcon>
              <span class="is-drawer-close:hidden text-base pl-2 whitespace-nowrap">
                好友
              </span>
            </router-link>
          </li>
          <li>
            <router-link :to="{name: 'create-index'}" active-class="menu-focus" class="is-drawer-close:tooltip is-drawer-close:tooltip-right py-4" data-tip="创作">
              <CreateIcon></CreateIcon>
              <span class="is-drawer-close:hidden text-base pl-2 whitespace-nowrap">
                创作
              </span>
            </router-link>
          </li>
        </ul>
      </div>
    </div>
  </div>
</template>

<script setup>
import MenuIcon from "@/components/navbar/icons/MenuIcon.vue";
import HomepageIcon from "@/components/navbar/icons/HomepageIcon.vue";
import FriendIcon from "@/components/navbar/icons/FriendIcon.vue";
import CreateIcon from "@/components/navbar/icons/CreateIcon.vue";
import SearchIcon from "@/components/navbar/icons/SearchIcon.vue";
import {useUserStore} from "@/stores/user.js";
import UserMenu from "@/components/navbar/UserMenu.vue";
import {ref, watch} from "vue";
import {useRoute, useRouter} from "vue-router";

const user = useUserStore();
const searchQuery = ref("");
const router = useRouter();
const route = useRoute();

watch(() => route.query.q, newQ => {
  searchQuery.value = newQ || '';
})

function search() {
  router.push({
    name: "homepage-index",
    query: {
      q: searchQuery.value.trim()
    }
  })
}


</script>

<style scoped></style>
