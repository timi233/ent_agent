import { defineStore } from 'pinia'

export interface Identity {
  id: string
  displayName: string
  role: string
  roleLabel: string
  permissions: string[]
}

interface IdentityState {
  identity: Identity | null
}

export const useIdentityStore = defineStore('identity', {
  state: (): IdentityState => ({
    identity: null
  }),
  persist: true,
  actions: {
    setIdentity(identity: Identity) {
      this.identity = identity
    },
    clear() {
      this.identity = null
    }
  }
})
