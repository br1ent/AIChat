<template>
  <div class="drawer lg:drawer-open">
    <input id="my-drawer-4" type="checkbox" class="drawer-toggle" />
    <div class="drawer-content">
      <nav class="navbar w-full bg-base-100 shadow-sm">
        <div class="navbar-start">
          <label for="my-drawer-4" aria-label="open sidebar" class="btn btn-square btn-ghost">
            <MenuIcon></MenuIcon>
          </label>
          <div class="px-2 font-bold text-2xl">AIFriends</div>
        </div>
        <div class="navbar-center w-4/5 max-w-180 flex justify-center">
          <div class="join w-4/5 flex justify-center">
            <input class="input join-item rounded-l-full w-4/5" placeholder="搜索你感兴趣的内容" />
            <button class="btn join-item rounded-r-full gap-1">
              <SearchIcon></SearchIcon>
              搜索
            </button>
          </div>
        </div>
        <div class="navbar-end">
          <router-link :to="{name: 'create-index'}" v-if="user.isLogin()" active-class="btn-active" class="btn btn-gosh text-base mr-6">
            <CreateIcon></CreateIcon>
            创作
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

const user = useUserStore()
</script>

<style scoped></style>