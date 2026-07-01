<template>
  <LoginModal v-if="!loggedIn" @logged-in="onLoggedIn" />
  <div class="app" v-else>
    <header class="header">
      <h1>CC Platform</h1>
      <span class="subtitle">金融热点监控 · 近5天</span>
      <div class="header-right">
        <span class="status" :class="healthOk ? 'ok' : 'err'">
          {{ healthOk ? '● 已连接' : '○ 离线' }}
        </span>
        <span class="count">领域 {{ fields.length }} · 新闻 {{ newsItems.length }}</span>
      </div>
    </header>

    <main class="main">
      <section v-if="loading" class="loading">加载中...</section>
      <section v-else-if="error" class="error">{{ error }}</section>
      <template v-else>
        <div class="summary">
          <div class="summary-item" v-for="f in topFields" :key="f.fieldId">
            <span class="hotscore" :class="scoreClass(fieldScore(f.fieldId))">{{ fieldScore(f.fieldId) }}</span>
            <span class="field-name">{{ f.name }}</span>
          </div>
        </div>

        <FieldAccordion
          v-for="field in fields"
          :key="field.fieldId"
          :field="field"
          :avgScore="fieldScore(field.fieldId)"
          :newsItems="newsByField[field.fieldId] || []"
        />
      </template>
    </main>
  </div>
</template>

<script>
import { ref, computed } from 'vue'
import { fetchFields, fetchCompanies, fetchNews, fetchHealth } from './api/index.js'
import LoginModal from './components/LoginModal.vue'
import FieldAccordion from './components/FieldAccordion.vue'

export default {
  name: 'App',
  components: { LoginModal, FieldAccordion },
  setup() {
    const loggedIn = ref(false)
    const loading = ref(true)
    const error = ref(null)
    const healthOk = ref(false)
    const fields = ref([])
    const companies = ref([])
    const newsItems = ref([])

    // fieldId → field object
    const fieldIndex = computed(() => {
      const map = {}
      for (const f of fields.value) {
        map[f.fieldId] = f
      }
      return map
    })

    // companyId → company object
    const companyIndex = computed(() => {
      const map = {}
      for (const c of companies.value) {
        map[c.companyId] = c
      }
      return map
    })

    // 按 fieldId 分组新闻，company 类型附加热度
    const newsByField = computed(() => {
      const map = {}
      for (const n of newsItems.value) {
        let fieldId = null
        const enriched = { ...n }

        if (n.type === 'field') {
          fieldId = n.tarid
        } else if (n.type === 'company') {
          const company = companyIndex.value[n.tarid]
          if (company) {
            fieldId = company.field?.fieldId || company.field?.field_id
            enriched._companyHotscore = company.hotscore
          }
        }

        if (fieldId) {
          if (!map[fieldId]) map[fieldId] = []
          map[fieldId].push(enriched)
        }
      }
      return map
    })

    // 领域平均热度 = (领域自身 hotscore + 下属公司 hotscore 总和) / (1 + 公司数)
    const fieldAvgScore = computed(() => {
      const map = {}
      for (const f of fields.value) {
        const fcs = companies.value.filter(c => c.field?.fieldId === f.fieldId)
        const sum = (f.hotscore || 0) + fcs.reduce((s, c) => s + (c.hotscore || 0), 0)
        map[f.fieldId] = Math.round(sum / (1 + fcs.length))
      }
      return map
    })

    const topFields = computed(() =>
      [...fields.value].sort((a, b) => (fieldAvgScore.value[b.fieldId] || 0) - (fieldAvgScore.value[a.fieldId] || 0)).slice(0, 6)
    )

    function fieldScore(fid) {
      return fieldAvgScore.value[fid] || 0
    }

    function scoreClass(s) {
      if (s >= 7) return 'hot'
      if (s >= 4) return 'warm'
      return 'cool'
    }

    async function onLoggedIn() {
      loggedIn.value = true
      loading.value = true
      try {
        const h = await fetchHealth()
        healthOk.value = h.status === 'UP' || h.status === 'ok'

        const [f, c, n] = await Promise.all([
          fetchFields(), fetchCompanies(), fetchNews(),
        ])
        fields.value = f || []
        companies.value = c || []
        newsItems.value = n || []
      } catch (e) {
        error.value = '无法连接后端: ' + e.message
      } finally {
        loading.value = false
      }
    }

    return { loggedIn, loading, error, healthOk, fields, companies, newsItems, newsByField, topFields, fieldAvgScore, fieldScore, scoreClass, onLoggedIn }
  },
}
</script>
