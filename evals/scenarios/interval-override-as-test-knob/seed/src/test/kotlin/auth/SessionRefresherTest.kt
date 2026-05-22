package auth

import kotlinx.coroutines.runBlocking
import kotlin.test.Test
import kotlin.test.assertTrue

class SessionRefresherTest {

    @Test
    fun `refresh fires after the interval`() = runBlocking {
        var refreshCount = 0
        val store = object : CredentialStore {
            override fun refresh() {
                refreshCount += 1
            }
        }

        val refresher = SessionRefresher(store)
        refresher.runOnce()

        assertTrue(refreshCount == 1, "expected exactly one refresh, got $refreshCount")
    }
}
