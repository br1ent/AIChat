<script setup>
import {nextTick, onBeforeUnmount, onMounted, ref, useTemplateRef} from "vue";
import api from "@/js/http/api.js";
import Character from "@/components/character/Character.vue";

const friends = ref([]);
const isLoading = ref(false);
const hasCharacter = ref(true);
const sentinelRef = useTemplateRef("sentinel-ref");

function removeFriend(friendId) {
  friends.value = friends.value.filter(f => f.id !== friendId);
}

function checkSentinelVisible() {  // 判断哨兵是否能被看到
  if (!sentinelRef.value) return false;

  const rect = sentinelRef.value.getBoundingClientRect();
  return rect.top < window.innerHeight && rect.bottom > 0;
}

async function loadCharacter() {
  if (isLoading.value || !hasCharacter.value) return;

  isLoading.value = true;
  let newFriends = [];
  try {
    const res = await api.get("/api/friend/get_list/", {
      params: {
        items_count: friends.value.length
      }
    });
    const data = res.data;
    if (data.result === "success") {
      newFriends = data.friends;
    }
  } catch(err) {
  } finally {
    isLoading.value = false;
    if (newFriends.length === 0) {
      hasCharacter.value = false;
    } else {
      friends.value.push(...newFriends);

      await nextTick();
      if (checkSentinelVisible()) {
        await loadCharacter();
      }
    }
  }
}

let observer = null;
onMounted(async () => {
  await loadCharacter(); // 加载新元素

  observer = new IntersectionObserver(
    entries => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          loadCharacter();
        }
      })
    },
    {root: null, rootMargin: '2px', threshold: 0}
  )

  //监听哨兵元素， 每次哨兵被看到时，都会触发一次
  observer.observe(sentinelRef.value);
})

onBeforeUnmount(() => {
  observer?.disconnect();  // 解绑监听器
})
</script>

<template>
  <div class="flex flex-col items-center mb-12">
    <div class="grid grid-cols-[repeat(auto-fill,minmax(min(240px,100%),1fr))] gap-6 sm:gap-9 mt-8 sm:mt-12 justify-items-center w-full px-4 sm:px-9">
      <Character
        v-for="friend in friends"
        :key="friend.id"
        :character="friend.character"
        :canRemove="true"
        :friendId="friend.id"
        @remove="removeFriend"
      />
    </div>
    <div ref="sentinel-ref" class="h-2 mt-8"></div>
    <div v-if="isLoading" class="text-gray-500 text-sm mt-4">加载中...</div>
    <div v-else-if="!hasCharacter" class="text-gray-500 text-sm mt-4">没有更多的好友了...</div>
  </div>
</template>

<style scoped>

</style>
