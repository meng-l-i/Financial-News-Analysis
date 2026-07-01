<template>
  <div class="accordion" :class="{ open: isOpen }">
    <button class="accordion-header" @click="toggle">
      <div class="header-left">
        <span class="arrow">{{ isOpen ? '▼' : '▶' }}</span>
        <span class="field-name">{{ field.name }}</span>
        <span class="badge" :class="scoreClass(avgScore)">{{ avgScore }}</span>
      </div>
      <span class="header-right">{{ items.length }} 条</span>
    </button>
    <div class="accordion-body" v-show="isOpen">
      <table v-if="items.length" class="news-table">
        <thead>
          <tr>
            <th>时间</th>
            <th>新闻标题</th>
            <th>关联公司 / 热点</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(item, idx) in items" :key="idx">
            <td class="time">{{ item.date || '-' }}</td>
            <td>
              <a :href="item.newslink || '#'" target="_blank" rel="noopener">
                {{ item.name }}
              </a>
            </td>
            <td>
              <template v-if="item.companyName">
                <span class="company-name">{{ item.companyName }}</span>
                <span class="badge sm" :class="scoreClass(item.companyHotscore)">
                  {{ item.companyHotscore ?? '-' }}
                </span>
              </template>
              <span v-else class="empty">-</span>
            </td>
          </tr>
        </tbody>
      </table>
      <div v-else class="empty-body">暂无新闻</div>
    </div>
  </div>
</template>

<script>
import { ref, computed } from 'vue'

export default {
  name: 'FieldAccordion',
  props: {
    field: { type: Object, required: true },
    avgScore: { type: Number, default: 0 },
    newsItems: { type: Array, default: () => [] },
  },
  setup(props) {
    const isOpen = ref(false)

    const items = computed(() => {
      return props.newsItems.map(n => {
        const isCompany = n.type === 'company'
        return {
          name: n.title || n.name,
          newslink: n.link,
          date: (n.date || '').replace('T', ' '),
          // company 类型：新闻 name 即公司名，热点来自 company 表
          companyName: isCompany ? n.name : null,
          companyHotscore: isCompany ? (n._companyHotscore ?? n.hotscore ?? null) : null,
        }
      })
    })

    function scoreClass(s) {
      if (s >= 7) return 'hot'
      if (s >= 4) return 'warm'
      return 'cool'
    }

    function toggle() { isOpen.value = !isOpen.value }

    return { isOpen, items, scoreClass, toggle }
  },
}
</script>
