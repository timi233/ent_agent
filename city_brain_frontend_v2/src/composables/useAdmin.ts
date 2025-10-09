import { onMounted } from 'vue'
import { storeToRefs } from 'pinia'

import { useAdminStore } from '@stores/adminStore'

export function useAdmin() {
  const adminStore = useAdminStore()
  const { overview, loading, error, saving } = storeToRefs(adminStore)

  onMounted(() => {
    if (!overview.value) {
      adminStore.load()
    }
  })

  return {
    overview,
    loading,
    error,
    saving,
    reload: adminStore.load,
    persistRole: adminStore.persistRole
  }
}
