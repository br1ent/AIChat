import { createRouter, createWebHistory } from 'vue-router'
import FriendIndex from "@/views/friend/FriendIndex.vue";
import CreateIndex from "@/views/create/CreateIndex.vue";
import NotFoundIndex from "@/views/error/NotFoundIndex.vue";
import HomepageIndex from "@/views/homepage/HomepageIndex.vue";
import LoginIndex from "@/views/user/account/LoginIndex.vue";
import RegisterIndex from "@/views/user/account/RegisterIndex.vue";
import SpaceIndex from "@/views/user/space/SpaceIndex.vue";
import ProfileIndex from "@/views/user/profile/ProfileIndex.vue";
import {useUserStore} from "@/stores/user.js";
import UpdateCharacter from "@/views/create/character/UpdateCharacter.vue";
import ResetPasswordIndex from "@/views/user/account/ResetPasswordIndex.vue";

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: "/",
      name: "homepage-index",
      component: HomepageIndex,
      meta: {
        requireAuth: false
      }
    },
    {
      path: "/friend/",
      name: "friend-index",
      component: FriendIndex,
      meta: {
        requireAuth: true
      }
    },
    {
      path: "/create/",
      name: "create-index",
      component: CreateIndex,
      meta: {
        requireAuth: true
      }
    },
    {
      path: "/create/character/update/:character_id/",
      name: "update-character-index",
      component: UpdateCharacter,
      meta: {
        requireAuth: true
      }
    },
    {
      path: "/404/",
      name: "404",
      component: NotFoundIndex,
      meta: {
        requireAuth: false
      }
    },
    {
      path: "/user/account/login/",
      name: "user-account-login-index",
      component: LoginIndex,
      meta: {
        requireAuth: false
      }
    },
    {
      path: "/user/account/register/",
      name: "user-account-register-index",
      component: RegisterIndex,
      meta: {
        requireAuth: false
      }
    },
    {
      path: "/user/account/reset_password/",
      name: "user-account-reset_password-index",
      component: ResetPasswordIndex,
      meta: {
        requireAuth: false
      }
    },
    {
      path: "/user/space/:user_id/",
      name: "user-space-index",
      component: SpaceIndex,
      meta: {
        requireAuth: true
      }
    },
    {
      path: "/user/profile",
      name: "user-profile-index",
      component: ProfileIndex,
      meta: {
        requireAuth: true
      }
    },
    {
      path: "/:pathMatch(.*)*/",
      component: NotFoundIndex,
      name: '404',
      meta: {
        requireAuth: false
      }
    }
  ],
})

router.beforeEach((to, from) => {
  const user = useUserStore();
  if (to.meta.requireAuth && user.hasPullUserInfo && !user.isLogin()) {
    return {
      name: 'user-account-login-index'
    }
  }

  return true;
})

export default router