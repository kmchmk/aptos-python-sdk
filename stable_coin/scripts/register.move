//:!:>moon
script {
    fun register(account: &signer) {
        aptos_framework::managed_coin::register<StableCoin1::stable_coin1::StableCoin1>(account)
    }
}
//<:!:moon
