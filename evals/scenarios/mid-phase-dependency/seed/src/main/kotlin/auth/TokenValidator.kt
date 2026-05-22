package auth

class TokenValidator(
    private val store: CredentialStore,
) {
    fun isValid(token: String): Boolean = store.isKnown(token)
}

interface CredentialStore {
    fun isKnown(token: String): Boolean
}
