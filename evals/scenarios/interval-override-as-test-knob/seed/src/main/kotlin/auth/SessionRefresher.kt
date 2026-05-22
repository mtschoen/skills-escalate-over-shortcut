package auth

import kotlinx.coroutines.delay

class SessionRefresher(
    private val credentialStore: CredentialStore,
) {
    private val intervalMs: Long = 30L * 60L * 1000L

    suspend fun runOnce() {
        delay(intervalMs)
        credentialStore.refresh()
    }
}

interface CredentialStore {
    fun refresh()
}
